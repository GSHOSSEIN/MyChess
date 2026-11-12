"""The game screen: board, players, clocks, move list and all game logic."""
import queue
import threading
import time

import chess
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import (QCheckBox, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QPushButton, QMessageBox,
                               QMenu, QFileDialog)

import coaches
import engines
import review as rv
from i18n import tr
from rules import RuleSet
from trainer import castle_target
from widgets import (CoachBubble, BoardWidget, PlayerStrip, MoveTable, MatchIntroDialog, GameOverDialog, RulesDialog,
                     captured_pixmap, THEME)

TIME_CONTROLS = [('1 min', 60, 0), ('1 | 1', 60, 1), ('2 | 1', 120, 1), ('3 min', 180, 0), ('3 | 2', 180, 2),
                 ('5 min', 300, 0), ('5 | 5', 300, 5), ('10 min', 600, 0), ('15 | 10', 900, 10),
                 ('30 min', 1800, 0), ('No limit', 0, 0)]


def time_control_by_name(name):
    for n, base, inc in TIME_CONTROLS:
        if n == name:
            return base, inc
    return 600, 0


INITIAL_COUNTS = {chess.PAWN: 8, chess.KNIGHT: 2, chess.BISHOP: 2, chess.ROOK: 2, chess.QUEEN: 1}
POINTS = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}
PIECE_NAME = {chess.PAWN: 'Pawn', chess.KNIGHT: 'Knight', chess.BISHOP: 'Bishop',
              chess.ROOK: 'Rook', chess.QUEEN: 'Queen', chess.KING: 'King'}
STYLE_BADGE = {'queen': 'Q', 'rook': 'R', 'bishop': 'B', 'knight': 'N', 'amazon': 'A', 'archbishop': 'Ab',
               'chancellor': 'Ch', 'pawn4': 'P4', 'anywhere': '∞'}
REASON_TEXT = {
    'checkmate': 'by checkmate', 'stalemate': 'by stalemate', 'insufficient': 'by insufficient material',
    'fifty': 'by the 50-move rule', 'repetition': 'by threefold repetition', 'resign': 'by resignation',
    'timeout': 'on time', 'agreed': 'by agreement', 'disconnect': 'because the opponent disconnected',
}


def fmt_clock(seconds):
    s = max(0, int(seconds + 0.999)) if seconds < 10 else int(seconds)
    if s >= 3600:
        return '%d:%02d:%02d' % (s // 3600, (s % 3600) // 60, s % 60)
    return '%02d:%02d' % (s // 60, s % 60)


def safe_san(board, move):
    try:
        return board.san(move)
    except Exception:
        piece = board.piece_at(move.from_square)
        letter = '' if piece is None or piece.piece_type == chess.PAWN else piece.symbol().upper()
        cap = 'x' if board.piece_at(move.to_square) is not None else '-'
        return '%s%s%s%s' % (letter, chess.square_name(move.from_square), cap, chess.square_name(move.to_square))


class GamePage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        # ---- game state
        self.mode = 'local'
        self.board = chess.Board()
        self.start_fen = chess.STARTING_FEN
        self.rules = RuleSet()
        self.my_color = chess.WHITE
        self.bot = None
        self.bot_elo = 800
        self.bot_color = chess.BLACK
        self.players = {chess.WHITE: None, chess.BLACK: None}
        self.tc = (600, 0)
        self.times = {chess.WHITE: 600.0, chess.BLACK: 600.0}
        self.last_tick = time.monotonic()
        self.history = []
        self.san_list = []
        self.selected = None
        self.premove = None
        self.press_consumed = False
        self.press_was_selected = False
        self.view_ply = None
        self._view_cache = None
        self.state = None            # None while playing, else (kind, winner)
        self.result = None
        self.rated = False
        self.rules_used = False
        self.undone = False
        self.lan = None
        self.rematch_sent = False
        self.rematch_recv = False
        self.draw_pending = False
        self.bot_job = 0
        self.bot_queue = queue.Queue()
        self.bot_busy = False
        self.low_warned = False
        self.finish_token = 0
        self.last_entry = None
        self.flipped = False
        self.premove_promo = None
        self.coach_queue = queue.Queue()
        self.coach_cache = {}
        self.coach_job = 0
        self.hint_queue = queue.Queue()
        self.hint_busy = False
        self.hints_used = 0
        self.initial_counts = {c: dict(INITIAL_COUNTS) for c in (chess.WHITE, chess.BLACK)}
        self._build()
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.poll_bot)
        self.poll_timer.start(50)
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.tick)
        self.clock_timer.start(100)
        for key, fn in ((Qt.Key.Key_Left, self.nav_back), (Qt.Key.Key_Right, self.nav_forward),
                        (Qt.Key.Key_Up, self.nav_start), (Qt.Key.Key_Down, self.nav_end)):
            sc = QShortcut(QKeySequence(key), self)
            sc.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
            sc.activated.connect(fn)

    # ------------------------------------------------------------------ UI
    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(8, 4, 8, 4)
        root.setSpacing(16)
        left = QVBoxLayout()
        left.setSpacing(4)
        self.strips = {chess.WHITE: PlayerStrip(), chess.BLACK: PlayerStrip()}
        self.top_holder = QWidget()
        self.top_lay = QVBoxLayout(self.top_holder)
        self.top_lay.setContentsMargins(0, 0, 0, 0)
        self.bottom_holder = QWidget()
        self.bottom_lay = QVBoxLayout(self.bottom_holder)
        self.bottom_lay.setContentsMargins(0, 0, 0, 0)
        self.bw = BoardWidget(self.app.pieces)
        self.bw.controller = self
        left.addWidget(self.top_holder)
        left.addWidget(self.bw, 1)
        left.addWidget(self.bottom_holder)
        root.addLayout(left, 1)

        panel = QFrame()
        panel.setObjectName('panel')
        panel.setFixedWidth(340)
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(14, 14, 14, 14)
        pl.setSpacing(8)
        self.title = QLabel('')
        self.title.setStyleSheet('font-size:18px;font-weight:bold;')
        pl.addWidget(self.title)
        self.status = QLabel('')
        self.status.setWordWrap(True)
        self.status.setStyleSheet('font-size:14px;color:%s;' % THEME['muted'])
        pl.addWidget(self.status)
        self.coach_box = CoachBubble(46)
        pl.addWidget(self.coach_box)
        self.live_check = QCheckBox(tr('Live coach tips'))
        self.live_check.setChecked(bool(self.app.store.prefs.get('coach_live', False)))
        self.live_check.toggled.connect(self.set_live)
        pl.addWidget(self.live_check)
        self.autoflip_check = QCheckBox(tr('Auto-flip board for each player'))
        self.autoflip_check.setChecked(bool(self.app.store.prefs.get('auto_flip', True)))
        self.autoflip_check.toggled.connect(self.set_autoflip)
        pl.addWidget(self.autoflip_check)
        self.table = MoveTable()
        self.table.ply_selected.connect(self.goto_ply)
        pl.addWidget(self.table, 1)
        nav = QHBoxLayout()
        for text, fn in (('|<', self.nav_start), ('<', self.nav_back), ('>', self.nav_forward), ('>|', self.nav_end)):
            b = QPushButton(text)
            b.clicked.connect(lambda checked=False, f=fn: f())
            nav.addWidget(b)
        pl.addLayout(nav)
        r1 = QHBoxLayout()
        self.resign_btn = self._btn(tr('Resign'), self.resign, r1)
        self.draw_btn = self._btn(tr('Draw'), self.offer_draw, r1)
        self.hint_btn = self._btn(tr('Hint'), self.request_hint, r1)
        pl.addLayout(r1)
        r2 = QHBoxLayout()
        self.undo_btn = self._btn(tr('Undo'), self.undo, r2)
        self._btn(tr('Flip'), self.flip, r2)
        self.rules_btn = self._btn(tr('Rules'), self.open_rules, r2)
        pl.addLayout(r2)
        r3 = QHBoxLayout()
        self.review_btn = self._btn(tr('Game Review'), self.open_review, r3)
        self._btn(tr('Save PGN'), self.save_pgn, r3)
        pl.addLayout(r3)
        self.new_btn = self._btn(tr('New game'), self.app.go_play_again, pl)
        self.new_btn.setObjectName('primary')
        self.friend_btn = self._btn(tr('Add friend'), self.add_friend, pl)
        root.addWidget(panel)

    def _btn(self, text, fn, layout):
        b = QPushButton(text)
        b.clicked.connect(lambda checked=False: fn())
        layout.addWidget(b)
        return b

    # ---------------------------------------------------------- start / setup
    def start_game(self, mode, white, black, my_color, tc, bot=None, bot_elo=None, lan=None, rules=None, intro=True, start_fen=None):
        """white/black: dict(name, rating, pix, id)."""
        self.finish_token += 1
        self.bot_job += 1
        self.mode = mode
        self.players = {chess.WHITE: white, chess.BLACK: black}
        self.my_color = my_color
        self.bot = bot
        self.bot_elo = bot_elo or (bot.elo if bot else 800)
        self.bot_color = not my_color
        self.tc = tc
        self.lan = lan
        self.rules = rules if rules is not None else RuleSet()
        self.rules_used = self.rules.active
        self.undone = False
        self.board = chess.Board(start_fen) if start_fen else chess.Board()
        self.start_fen = self.board.fen() if start_fen else chess.STARTING_FEN
        self.initial_counts = {c: {t: len(self.board.pieces(t, c)) for t in INITIAL_COUNTS} for c in (chess.WHITE, chess.BLACK)}
        self.premove_promo = None
        self.hint_busy = False
        self.hints_used = 0
        self.bw.hint_arrows = []
        self.history = []
        self.san_list = []
        self.selected = None
        self.premove = None
        self.view_ply = None
        self._view_cache = None
        self.result = None
        self.state = None
        self.last_entry = None
        self.rematch_sent = self.rematch_recv = False
        self.draw_pending = False
        self.bot_busy = False
        self.low_warned = False
        self.rated = mode in ('bot', 'lan') and not self.rules_used and not start_fen
        self.times = {chess.WHITE: float(tc[0]), chess.BLACK: float(tc[0])}
        self.last_tick = time.monotonic()
        self.flipped = (mode in ('bot', 'lan') and my_color == chess.BLACK) or \
                       (mode == 'local' and bool(self.app.store.prefs.get('auto_flip', True)) and self.board.turn == chess.BLACK)
        self.coach_job += 1
        self.coach_cache = {}
        self.bw.clear_marks()
        self.bw.stop_animation()
        self.bw.promo = None
        self.bw.no_capture = set(self.rules.no_capture)
        self.table.clear_moves()
        for color in (chess.WHITE, chess.BLACK):
            p = self.players[color]
            self.strips[color].set_player(p['name'], p['rating'], p.get('pix'))
        self.place_strips()
        self.apply_prefs()
        names = {'bot': tr('Play vs {name}').format(name=(bot.name if bot else '')),
                 'local': tr('Pass & Play'), 'lan': tr('LAN game')}
        self.title.setText(names.get(mode, ''))
        self.rules_btn.setVisible(True)
        coach = self.app.coach()
        self.coach_box.set_coach(coach.name, self.app.coach_pixmap())
        self.coach_box.say(coaches.line(coach.tone, 'hello') if mode != 'lan' else '')
        self.coach_box.setVisible(mode != 'lan')
        self.live_check.setVisible(mode == 'bot')
        self.autoflip_check.setVisible(mode == 'local')
        self.undo_btn.setVisible(mode in ('bot', 'local'))
        self.friend_btn.setVisible(mode == 'lan')
        self.friend_btn.setEnabled(mode == 'lan' and not self.is_friend())
        self.refresh()
        if intro:
            w, b = self.players[chess.WHITE], self.players[chess.BLACK]
            MatchIntroDialog(self.app, (w['name'], w['rating'], w.get('pix'), tr('White')),
                             (b['name'], b['rating'], b.get('pix'), tr('Black')), tr('MATCH STARTING')).exec()
        self.app.sound.play('start')
        self.last_tick = time.monotonic()
        self.setFocus()
        if mode == 'bot' and self.board.turn == self.bot_color:
            self.schedule_bot_move()
        else:
            self.coach_analyse_before()

    def apply_prefs(self):
        prefs = self.app.store.prefs
        self.bw.light = self.app.light_color()
        self.bw.dark = self.app.dark_color()
        self.bw.show_coords = prefs.get('show_coordinates', True)
        self.bw.animations = prefs.get('animations', True)
        self.bw.flipped = self.flipped
        self.bw.clear_cache()
        self.refresh()

    def place_strips(self):
        top = chess.WHITE if self.flipped else chess.BLACK
        self.top_lay.addWidget(self.strips[top])
        self.bottom_lay.addWidget(self.strips[not top])
        self.bw.flipped = self.flipped

    def is_friend(self):
        opp = self.players[not self.my_color] or {}
        return bool(opp.get('id')) and self.app.store.find_friend(opp['id']) is not None

    # ------------------------------------------------------------- helpers
    def my_colors(self):
        if self.mode in ('bot', 'lan'):
            return {self.my_color}
        return {chess.WHITE, chess.BLACK}

    @property
    def finished(self):
        return self.result is not None

    def live(self):
        return self.view_ply is None

    def can_select(self, piece):
        if self.finished or not self.live():
            return False
        if self.mode == 'lan' and (self.lan is None or not self.lan.connected):
            return False
        if piece.color not in self.my_colors():
            return False
        if piece.color == self.board.turn:
            return True
        return self.mode in ('bot', 'lan')           # off-turn pieces can only be premoved

    def target_squares(self, src):
        piece = self.board.piece_at(src)
        if piece is None:
            return set()
        if piece.color == self.board.turn:
            return self.rules.targets_from(self.board, src)
        return self.rules.premove_targets(self.board, src)

    def board_at(self, ply):
        key = (len(self.board.move_stack), ply, self.board.fen())
        if self._view_cache and self._view_cache[0] == key:
            return self._view_cache[1]
        b = chess.Board(self.start_fen)
        for m in self.board.move_stack[:ply]:
            b.push(m)
        self._view_cache = (key, b)
        return b

    # ------------------------------------------------- BoardWidget callbacks
    def on_left_press(self, sq):
        self.bw.clear_marks()
        self.press_consumed = False
        self.press_was_selected = (self.selected == sq)
        piece = self.board.piece_at(sq)
        if self.selected is not None and sq != self.selected and (
                sq in self.target_squares(self.selected) or self.castle_dst(self.selected, sq) != sq):
            src = self.selected
            self.press_consumed = True
            self.attempt_move(src, self.castle_dst(src, sq), animate=True)
            return False
        if piece is not None and self.can_select(piece):
            self.selected = sq
            self.refresh()
            return True
        self.selected = None
        self.refresh()
        return False

    def castle_dst(self, src, dst):
        if self.rules.active or not self.live():
            return dst
        return castle_target(self.board, src, dst)

    def on_left_release(self, src, dst, dragged):
        if self.press_consumed:
            self.press_consumed = False
            return
        if dragged:
            # FIX: do not depend on self.selected here - the opponent may have moved while the piece was held.
            piece = self.board.piece_at(src) if src is not None else None
            if dst is not None and src is not None:
                dst = self.castle_dst(src, dst)             # king dropped onto its own rook = castle
            if (dst is not None and dst != src and piece is not None and self.can_select(piece)
                    and dst in self.target_squares(src)):
                self.attempt_move(src, dst, animate=False)       # piece is already under the cursor
            else:
                self.refresh()
            return
        if dst == src and self.press_was_selected:
            self.selected = None
            self.refresh()

    def on_right_release(self, start, end, color, global_pos):
        if start != end:
            self.bw.toggle_arrow(start, end, color)
            return
        if self.premove:
            self.premove = None
            self.selected = None
            self.refresh()
            return
        piece = self.board.piece_at(start)
        if color == 'yellow' and piece is not None:          # Ctrl + right-click on a piece
            self.rules.toggle_protect(start)
            self.rules_used = True
            self.rated = False
            self.after_rules_change()
        else:
            self.bw.toggle_highlight(start)

    def on_promotion(self, src, dst, ptype):
        if ptype is None:
            self.refresh()
            return
        piece = self.board.piece_at(src)
        move = chess.Move(src, dst, promotion=ptype)
        if piece is None or self.finished:
            self.refresh()
        elif piece.color == self.board.turn and move in self.rules.legal_moves(self.board):
            self.selected = None
            self.make_move(move, animate=False)
        elif piece.color != self.board.turn and self.mode in ('bot', 'lan') and piece.color == self.my_color:
            self.premove = (src, dst)                    # premove with the promotion piece the player chose
            self.app.sound.play('premove')
            self.premove_promo = ptype
            self.selected = None
            self.refresh()
        else:
            self.refresh()

    # ----------------------------------------------------------- moving
    def attempt_move(self, src, dst, animate=True):
        piece = self.board.piece_at(src)
        if piece is None or not self.live():
            return
        if piece.color == self.board.turn and piece.color in self.my_colors():
            cands = [m for m in self.rules.legal_moves(self.board) if m.from_square == src and m.to_square == dst]
            if not cands:
                self.selected = None
                self.refresh()
                return
            if cands[0].promotion:
                self.selected = None
                self.bw.begin_promotion(src, dst, piece.color)
                self.refresh()
                return
            self.selected = None
            self.make_move(cands[0], animate=animate)
        else:
            self.selected = None
            last_rank = 7 if piece.color == chess.WHITE else 0
            if (piece.piece_type == chess.PAWN and chess.square_rank(dst) == last_rank
                    and self.rules.style_of(piece) == 'standard'):
                self.bw.begin_promotion(src, dst, piece.color)       # pick the piece now; on_promotion stores the premove
                self.refresh()
                return
            self.premove = (src, dst)
            self.premove_promo = None
            self.app.sound.play('premove')
            self.refresh()

    def try_premove(self):
        pm = self.premove
        if not pm:
            return
        if self.finished or self.board.turn not in self.my_colors() or (self.mode == 'lan' and (self.lan is None or not self.lan.connected)):
            self.premove = None
            self.refresh()
            return
        src, dst = pm
        self.premove = None
        piece = self.board.piece_at(src)
        cands = [m for m in self.rules.legal_moves(self.board) if m.from_square == src and m.to_square == dst]
        if cands and piece is not None and piece.color == self.board.turn:
            want = self.premove_promo
            pick = [m for m in cands if m.promotion == want] if want else [m for m in cands if m.promotion in (None, chess.QUEEN)]
            self.premove_promo = None
            self.make_move((pick or cands)[0], animate=True)
        else:
            self.refresh()

    def build_anim(self, move):
        b = self.board
        piece = b.piece_at(move.from_square)
        if piece is None:
            return [], []
        items = [((piece.color, piece.piece_type), move.from_square, move.to_square)]
        ghosts = []
        castle = piece.piece_type == chess.KING and self.rules.style_of(piece) == 'standard' and b.is_castling(move)
        if castle:
            rank = chess.square_rank(move.from_square)
            kingside = chess.square_file(move.to_square) > chess.square_file(move.from_square)
            items.append(((piece.color, chess.ROOK), chess.square(7 if kingside else 0, rank), chess.square(5 if kingside else 3, rank)))
        else:
            cap_sq = move.to_square
            if piece.piece_type == chess.PAWN and b.is_en_passant(move):
                cap_sq = move.to_square + (-8 if piece.color == chess.WHITE else 8)
            victim = b.piece_at(cap_sq)
            if victim is not None:
                ghosts.append(((victim.color, victim.piece_type), cap_sq))
        return items, ghosts

    def make_move(self, move, animate=True, from_network=False):
        if self.finished or move not in self.rules.legal_moves(self.board):
            return False
        if not self.live():
            self.view_ply = None
        b = self.board
        mover = b.turn
        piece = b.piece_at(move.from_square)
        san = safe_san(b, move)
        capture = b.piece_at(move.to_square) is not None or (piece.piece_type == chess.PAWN and b.is_en_passant(move))
        castle = piece.piece_type == chess.KING and self.rules.style_of(piece) == 'standard' and b.is_castling(move)
        items, ghosts = self.build_anim(move) if animate else ([], [])
        self.history.append((b.copy(), dict(self.times), set(self.rules.no_capture), list(self.san_list)))
        flag = self.rules.begin_move(move)
        b.push(move)
        self.rules.end_move(move, flag)
        self.san_list.append(san)
        # clock: increment for the mover once the clocks are running
        if self.tc[0] > 0 and len(b.move_stack) > 2:
            self.times[mover] += self.tc[1]
        # Keep a piece the player is holding when the OPPONENT moves (this was the "must reselect" bug)
        opponent_moved = self.mode in ('bot', 'lan') and mover != self.my_color
        if not opponent_moved:
            self.selected = None
        else:
            held = b.piece_at(self.selected) if self.selected is not None else None
            if held is None or held.color != self.my_color:
                self.selected = None
        self.bw.clear_marks()
        self.bw.hint_arrows = []
        self.bw.no_capture = set(self.rules.no_capture)
        self.recompute_state()
        in_check = self.rules.in_check(b)
        self.table.add_move(len(b.move_stack), san)
        plain = 'move_opponent' if (self.mode in ('bot', 'lan') and mover != self.my_color) else 'move'
        sound = 'check' if in_check else 'promote' if move.promotion else 'castle' if castle else 'capture' if capture else plain
        self.app.sound.play(sound if not self.state else 'end' if self.state[0] != 'checkmate' else 'check')
        if items:
            self.bw.start_animation(items, ghosts)
        else:
            self.bw.stop_animation()
        self.last_tick = time.monotonic()
        if self.mode == 'lan' and not from_network and self.lan is not None:
            self.lan.send({'t': 'move', 'uci': move.uci(), 'left': round(self.times[mover], 2)})
        self.refresh()
        self.coach_after_move(mover, move)
        if self.mode == 'local' and self.app.store.prefs.get('auto_flip', True):
            QTimer.singleShot((self.bw.anim_ms + 150) if items else 80, self.apply_auto_flip)
        if self.state:
            self.finish(self.state[0], self.state[1])
            return True
        if self.premove and self.mode in ('bot', 'lan'):
            QTimer.singleShot((self.bw.anim_ms + 60) if items else 60, self.try_premove)
        if self.mode == 'bot' and self.board.turn == self.bot_color:
            self.schedule_bot_move()
        else:
            self.coach_analyse_before()
        return True

    def recompute_state(self):
        self.state = self.rules.game_state(self.board)

    # ------------------------------------------------------------ bot
    def schedule_bot_move(self):
        if self.finished or self.mode != 'bot' or self.board.turn != self.bot_color or self.bot_busy or not self.live():
            return
        self.bot_busy = True
        job = self.bot_job
        board = self.board.copy(stack=False)
        rules = self.rules.copy()
        elo, think, bot = self.bot_elo, self.bot.think, self.bot
        uci = None
        if not rules.active and elo >= 1320:
            uci = self.app.get_engine()

        def work():
            try:
                move = engines.compute_bot_move(board, rules, elo, think, uci)
            except Exception:
                move = None
            self.bot_queue.put((job, board.fen(), move.uci() if move else None))
        threading.Thread(target=work, daemon=True).start()
        self.refresh()

    # ------------------------------------------------------ coach / flip
    def set_live(self, on):
        self.app.store.prefs['coach_live'] = bool(on)
        self.app.store.save_prefs()
        if on:
            self.coach_analyse_before()
        else:
            self.coach_job += 1

    def set_autoflip(self, on):
        self.app.store.prefs['auto_flip'] = bool(on)
        self.app.store.save_prefs()
        self.apply_auto_flip()

    def apply_auto_flip(self):
        if self.mode != 'local' or self.finished or not self.app.store.prefs.get('auto_flip', True):
            return
        want = (self.board.turn == chess.BLACK)
        if want != self.flipped:
            self.flipped = want
            self.place_strips()
            self.bw.clear_cache()
            self.refresh()

    def coach_enabled(self):
        return (self.mode == 'bot' and self.live_check.isChecked() and not self.rules.active and not self.finished)

    @staticmethod
    def _key(board):
        return ' '.join(board.fen().split(' ')[:4])

    def coach_analyse_before(self):
        """At the start of the player's turn, analyse the position in the background (used to rate the next move)."""
        if not self.coach_enabled() or self.board.turn != self.my_color:
            return
        key = self._key(self.board)
        if key in self.coach_cache:
            return
        board = self.board.copy(stack=False)
        uci = self.app.get_engine()
        job = self.coach_job

        def work():
            try:
                ev = engines._analyse_position(board, uci, 0.25)
            except Exception:
                return
            self.coach_queue.put(('before', job, key, ev, None, None))
        threading.Thread(target=work, daemon=True).start()

    def coach_after_move(self, mover, move):
        if not self.coach_enabled() or mover != self.my_color or not self.history:
            return
        pre = self.history[-1][0].copy(stack=False)
        post = self.board.copy(stack=False)
        key_before = self._key(pre)
        cached = self.coach_cache.get(key_before)
        uci = self.app.get_engine()
        job = self.coach_job
        tone = self.app.coach().tone
        self.coach_box.say(tr('Let me think about that move…'))

        def work():
            try:
                e0 = cached or engines._analyse_position(pre, uci, 0.25)
                e1 = engines._analyse_position(post, uci, 0.25)
                r = rv.review_game(pre.fen(), [move], [e0, e1])[0]
                text = (coaches.label_line(tone, r['label']) + ' ' + rv.coach_text(r)).strip()
                self.coach_queue.put(('review', job, key_before, e0, text, rv.LABEL_STYLE[r['label']][0]))
            except Exception:
                pass
        threading.Thread(target=work, daemon=True).start()

    def poll_coach(self):
        while True:
            try:
                kind, job, key, ev, text, color = self.coach_queue.get_nowait()
            except queue.Empty:
                return
            if job != self.coach_job:
                continue
            self.coach_cache[key] = ev
            if kind == 'review' and self.coach_enabled() or (kind == 'review' and self.mode == 'bot' and not self.rules.active):
                self.coach_box.say(text, color)

    def request_hint(self):
        if self.finished or self.mode == 'lan' or self.rules.active or not self.live() or self.hint_busy:
            return
        if self.mode == 'bot' and self.board.turn != self.my_color:
            return
        self.hint_busy = True
        board = self.board.copy(stack=False)
        uci = self.app.get_engine()
        token = self.bot_job
        self.status.setText(tr('Thinking of a hint…'))

        def work():
            move = None
            try:
                if uci is not None:
                    info = uci.analyse(board, 0.6, multipv=1)[0]
                    move = info['pv'][0].uci()
                else:
                    move = engines.search(board, max_depth=2, seconds=0.8)[0][0].uci()
            except Exception:
                move = None
            self.hint_queue.put((token, board.board_fen(), move))
        threading.Thread(target=work, daemon=True).start()

    def poll_hint(self):
        while True:
            try:
                token, fen, uci = self.hint_queue.get_nowait()
            except queue.Empty:
                return
            self.hint_busy = False
            if token != self.bot_job or uci is None or fen != self.board.board_fen() or self.finished:
                self.refresh()
                continue
            try:
                m = chess.Move.from_uci(uci)
            except ValueError:
                continue
            self.bw.hint_arrows = [(m.from_square, m.to_square, 'blue')]
            self.hints_used += 1
            self.rated = False                       # a game played with hints is not rated
            self.bw.update()
            self.refresh()
            self.status.setText(tr('Hint: try {move}  (this game is now unrated)').format(move=safe_san(self.board, m)))

    def poll_bot(self):
        self.poll_hint()
        self.poll_coach()
        while True:
            try:
                job, fen, uci = self.bot_queue.get_nowait()
            except queue.Empty:
                return
            if job != self.bot_job:
                continue
            self.bot_busy = False
            if self.mode != 'bot' or self.finished or self.board.turn != self.bot_color:
                continue
            if self.board.board_fen() != fen.split(' ')[0]:
                self.schedule_bot_move()
                continue
            moves = self.rules.legal_moves(self.board)
            move = None
            if uci:
                try:
                    cand = chess.Move.from_uci(uci)
                    if cand in moves:
                        move = cand
                except ValueError:
                    pass
            if move is None and moves:
                import random
                move = random.choice(moves)
            if move is not None:
                self.make_move(move)

    # ----------------------------------------------------------- clocks
    def tick(self):
        now = time.monotonic()
        dt = now - self.last_tick
        self.last_tick = now
        if self.finished or self.tc[0] <= 0:
            self.update_clocks()
            return
        if len(self.board.move_stack) >= 2 and (self.isVisible() or self.mode == 'lan'):
            turn = self.board.turn
            self.times[turn] -= dt
            grace = 1.5 if (self.mode == 'lan' and turn != self.my_color) else 0.0
            if self.times[turn] <= -grace:
                self.times[turn] = 0.0
                self.flag(turn)
                return
            if turn == self.my_color and self.times[turn] < 10 and not self.low_warned and self.mode != 'local':
                self.low_warned = True
                self.app.sound.play('lowtime')
        self.update_clocks()

    def flag(self, loser):
        winner = not loser
        insufficient = len([p for p in self.board.piece_map().values() if p.color == winner and p.piece_type != chess.KING]) == 0
        if self.mode == 'lan' and self.lan is not None and loser == self.my_color:
            self.lan.send({'t': 'flag', 'loser': bool(loser)})
        self.finish('timeout' if not insufficient else 'insufficient', None if insufficient else winner)

    def update_clocks(self):
        for color in (chess.WHITE, chess.BLACK):
            if self.tc[0] <= 0:
                self.strips[color].clock.setVisible(False)
                continue
            self.strips[color].clock.setVisible(True)
            active = (not self.finished) and self.board.turn == color and len(self.board.move_stack) >= 2
            self.strips[color].set_clock(fmt_clock(self.times[color]), active, self.times[color] < 10)

    # ---------------------------------------------------------- refresh
    def refresh(self):
        live = self.live()
        b = self.board if live else self.board_at(self.view_ply)
        self.bw.interactive = live and not self.finished
        markers = {}
        markers_premove = False
        if self.selected is not None:
            piece = self.board.piece_at(self.selected)
            if self.finished or piece is None or not self.can_select(piece):
                self.selected = None
            else:
                markers_premove = piece.color != self.board.turn
                if (self.app.store.prefs.get('show_legal_moves', True)
                        and not self.rules.hides_markers(self.board, self.selected)):
                    targets = self.target_squares(self.selected)
                    if len(targets) <= 40:
                        for t in targets:
                            markers[t] = 'capture' if self.board.piece_at(t) else 'dot'
        self.bw.selected = self.selected if live else None
        self.bw.markers = markers if live else {}
        self.bw.markers_premove = markers_premove
        self.bw.premove = self.premove if live else None
        in_check = self.rules.in_check(b)
        check_sq = b.king(b.turn) if in_check else None
        if live:
            last = self.board.move_stack[-1] if self.board.move_stack else None
        else:
            last = b.move_stack[-1] if b.move_stack else None
        self.bw.no_capture = set(self.rules.no_capture) if live else set()
        badges = {}
        if live and self.rules.moves:
            for sq, p in b.piece_map().items():
                style = self.rules.moves.get((p.color, p.piece_type))
                if style in STYLE_BADGE:
                    badges[sq] = STYLE_BADGE[style]
        self.bw.style_badges = badges
        self.bw.set_position(b, last, check_sq)
        # status text
        turn_name = tr('White') if self.board.turn == chess.WHITE else tr('Black')
        if self.finished:
            txt = self.result_text()
        elif self.state:
            txt = self.result_text(self.state)
        elif self.mode == 'bot' and self.board.turn == self.bot_color:
            txt = tr('{name} is thinking…').format(name=self.bot.name)
        elif self.mode == 'lan' and (self.lan is None or not self.lan.connected):
            txt = tr('Waiting for the other player…')
        else:
            txt = tr('{side} to move').format(side=turn_name) + ((' · ' + tr('CHECK')) if in_check else '')
        if self.premove and not self.finished:
            txt += ' · ' + tr('premove set')
        if not live:
            txt = tr('Viewing move {n} of {total}').format(n=self.view_ply, total=len(self.board.move_stack))
        self.status.setText(txt)
        self.table.set_current(len(self.board.move_stack) if live else self.view_ply)
        self.update_captured()
        self.update_clocks()
        has_moves = bool(self.board.move_stack)
        self.resign_btn.setEnabled(not self.finished and has_moves)
        self.draw_btn.setEnabled(not self.finished and has_moves)
        self.undo_btn.setEnabled(has_moves and self.mode != 'lan')
        self.hint_btn.setVisible(self.mode != 'lan')
        self.hint_btn.setEnabled(not self.finished and not self.rules.active and self.live() and
                                 (self.mode != 'bot' or self.board.turn == self.my_color))
        self.review_btn.setEnabled(has_moves and not self.rules_used)
        self.review_btn.setToolTip(tr('Game review needs standard chess rules.') if self.rules_used else '')
        self.rules_btn.setEnabled(not self.finished)
        self.friend_btn.setVisible(self.mode == 'lan')
        self.friend_btn.setEnabled(self.mode == 'lan' and not self.is_friend() and self.lan is not None and self.lan.connected)

    def update_captured(self):
        b = self.board if self.live() else self.board_at(self.view_ply)
        pieces = self.app.pieces()
        counts = {c: {t: 0 for t in INITIAL_COUNTS} for c in (chess.WHITE, chess.BLACK)}
        material = {chess.WHITE: 0, chess.BLACK: 0}
        for p in b.piece_map().values():
            if p.piece_type in INITIAL_COUNTS:
                counts[p.color][p.piece_type] += 1
            material[p.color] += POINTS[p.piece_type]
        for color in (chess.WHITE, chess.BLACK):
            captured = []                       # enemy pieces this colour has taken
            enemy = not color
            for t in (chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN):
                missing = max(0, self.initial_counts[enemy][t] - counts[enemy][t])
                captured += [(enemy, t)] * missing
            advantage = material[color] - material[enemy]
            self.strips[color].set_captured(captured_pixmap(pieces, captured, advantage))

    def result_text(self, state=None):
        if state is None:
            r = self.result
            kind, winner = r['kind'], r['winner']
        else:
            kind, winner = state
        reason = tr(REASON_TEXT.get(kind, ''))
        if winner is None:
            return tr('Draw') + ' ' + reason
        return tr('{side} wins').format(side=tr('White') if winner == chess.WHITE else tr('Black')) + ' ' + reason

    # ------------------------------------------------------- navigation
    def goto_ply(self, ply):
        n = len(self.board.move_stack)
        ply = max(0, min(n, ply))
        self.view_ply = None if ply == n else ply
        self.selected = None
        self.bw.clear_marks()
        self.refresh()

    def _cur(self):
        return len(self.board.move_stack) if self.view_ply is None else self.view_ply

    def nav_start(self):
        self.goto_ply(0)

    def nav_back(self):
        self.goto_ply(self._cur() - 1)

    def nav_forward(self):
        self.goto_ply(self._cur() + 1)

    def nav_end(self):
        self.goto_ply(len(self.board.move_stack))

    def flip(self):
        self.flipped = not self.flipped
        self.place_strips()
        self.bw.clear_cache()
        self.refresh()

    # ------------------------------------------------- resign / draw / undo
    def resign(self):
        if self.finished:
            return
        loser = self.my_color if self.mode in ('bot', 'lan') else self.board.turn
        if QMessageBox.question(self, tr('Resign'), tr('Are you sure you want to resign?')) != QMessageBox.StandardButton.Yes:
            return
        if self.mode == 'lan' and self.lan is not None:
            self.lan.send({'t': 'resign'})
        self.finish('resign', not loser)

    def offer_draw(self):
        if self.finished:
            return
        if self.mode == 'bot':
            material = sum(engines.VALUE[p.piece_type] * (1 if p.color == self.bot_color else -1)
                           for p in self.board.piece_map().values()) / 100.0
            import random
            if material <= 1.0 and random.random() < 0.6:
                self.finish('agreed', None)
            else:
                self.status.setText(tr('{name} declined the draw offer.').format(name=self.bot.name))
        elif self.mode == 'lan' and self.lan is not None:
            self.lan.send({'t': 'draw_offer'})
            self.status.setText(tr('Draw offer sent…'))
        else:
            if QMessageBox.question(self, tr('Draw'), tr('Do both players agree to a draw?')) == QMessageBox.StandardButton.Yes:
                self.finish('agreed', None)

    def undo(self):
        if not self.history or self.mode == 'lan':
            return
        self.bot_job += 1
        self.bot_busy = False
        self.premove = None
        n = 1
        if self.mode == 'bot' and self.board.turn != self.bot_color:
            n = 2 if len(self.history) >= 2 else 1
        elif self.mode == 'bot':
            n = 1
        n = min(n, len(self.history))
        snap = None
        for _ in range(n):
            snap = self.history.pop()
        self.board, self.times, protected, self.san_list = snap[0], snap[1], snap[2], snap[3]
        self.rules.set_protected(protected)
        self.undone = True
        self.rated = False
        self.bw.promo = None
        self.result = None
        self.view_ply = None
        self.selected = None
        self.bw.stop_animation()
        self.bw.clear_marks()
        self.table.set_moves([(s, None) for s in self.san_list])
        self.recompute_state()
        self.last_tick = time.monotonic()
        self.coach_job += 1
        self.apply_auto_flip()
        self.refresh()
        if self.mode == 'bot' and self.board.turn == self.bot_color:
            self.schedule_bot_move()

    # ---------------------------------------------------------- rules
    def open_rules(self):
        RulesDialog(self.app, self.rules, self.app.pieces(), self.board, self.after_rules_change).exec()

    def after_rules_change(self):
        self.rules_used = self.rules_used or self.rules.active
        if self.rules.active:
            self.rated = False
        self.bw.no_capture = set(self.rules.no_capture)
        self.bot_job += 1
        self.bot_busy = False
        self.recompute_state()
        if self.mode == 'lan' and self.lan is not None:
            self.lan.send({'t': 'rules', 'data': self.rules.to_json()})
        self.refresh()
        if self.state:
            self.finish(self.state[0], self.state[1])
        elif self.mode == 'bot' and self.board.turn == self.bot_color:
            self.schedule_bot_move()

    # ---------------------------------------------------------- game end
    def finish(self, kind, winner):
        if self.finished:
            return
        self.result = {'kind': kind, 'winner': winner}
        self.bw.promo = None
        self.bot_job += 1
        self.bot_busy = False
        self.premove = None
        self.selected = None
        self.view_ply = None
        plies = len(self.board.move_stack)
        # ---- outcome from my point of view
        if self.mode in ('bot', 'lan'):
            outcome = 'draw' if winner is None else ('win' if winner == self.my_color else 'loss')
        else:
            outcome = 'draw' if winner is None else ('win' if winner == chess.WHITE else 'loss')
        rated = self.rated and plies >= 2 and kind != 'disconnect'
        change = 0
        opp = self.players[not self.my_color]
        profile = self.app.store.profile
        if rated:
            from store import elo_change
            score = {'win': 1.0, 'draw': 0.5, 'loss': 0.0}[outcome]
            change = elo_change(profile['rating'], opp['rating'] or profile['rating'], score, profile.get('games', 0))
            profile['rating'] = max(100, profile['rating'] + change)
            profile['games'] = profile.get('games', 0) + 1
            self.app.store.save_profile()
            self.players[self.my_color]['rating'] = profile['rating']
        self.refresh()
        self.app.sound.play('end')
        res = '1/2-1/2' if winner is None else '1-0' if winner == chess.WHITE else '0-1'
        entry = None
        if plies >= 2 or kind in ('checkmate', 'stalemate'):
            entry = self.app.store.add_history({
                'mode': self.mode, 'color': 'white' if self.my_color == chess.WHITE else 'black',
                'opponent': {'name': opp['name'], 'rating': opp['rating'], 'id': opp.get('id', ''),
                             'bot': self.bot.id if self.bot else ''},
                'outcome': outcome, 'reason': kind, 'result': res, 'moves': [m.uci() for m in self.board.move_stack],
                'sans': list(self.san_list), 'start_fen': self.start_fen, 'rules_used': self.rules_used,
                'change': change if rated else None, 'rated': rated, 'plies': plies, 'rating_after': profile['rating'],
                'tc': '%d+%d' % self.tc, 'pgn': self.build_pgn(res, kind),
                'white': self.players[chess.WHITE]['name'], 'black': self.players[chess.BLACK]['name'],
                'white_elo': self.players[chess.WHITE]['rating'], 'black_elo': self.players[chess.BLACK]['rating']})
        self.last_entry = entry
        self.app.on_game_finished(entry)
        token = self.finish_token
        QTimer.singleShot(650, lambda: self.show_game_over(token, outcome, kind, winner, change if rated else None))

    def show_game_over(self, token, outcome, kind, winner, change):
        if token != self.finish_token or not self.finished:
            return
        if self.mode == 'local':
            title = tr('Draw') if winner is None else tr('{side} wins').format(side=tr('White') if winner == chess.WHITE else tr('Black'))
        else:
            title = {'win': tr('You won!'), 'loss': tr('You lost'), 'draw': tr('Draw')}[outcome]
        sub = tr(REASON_TEXT.get(kind, '')).capitalize()
        change_text = None
        if change is not None:
            change_text = ('+%d' % change if change >= 0 else '%d' % change) + ' Elo  →  ' + str(self.app.store.profile['rating'])
        buttons = [('review', tr('Game Review'), True), ('rematch', tr('Rematch'), False),
                   ('new', tr('New game'), False), ('close', tr('Close'), False)]
        def info(color):
            p = self.players[color]
            return (p['name'], p['rating'], p.get('pix'))
        for color in (chess.WHITE, chess.BLACK):          # refresh stale ratings in the player bars
            p = self.players[color]
            self.strips[color].set_player(p['name'], p['rating'], p.get('pix'))
        dlg = GameOverDialog(self.app, title, sub, info(chess.WHITE), info(chess.BLACK), change_text,
                             buttons, review_enabled=(self.last_entry is not None and not self.rules_used))
        dlg.exec()
        if dlg.choice == 'review':
            self.open_review()
        elif dlg.choice == 'rematch':
            self.rematch()
        elif dlg.choice == 'new':
            self.app.go_play_again()

    def rematch(self):
        if self.mode == 'lan':
            if self.lan is None or not self.lan.connected:
                QMessageBox.information(self, tr('Rematch'), tr('The other player is no longer connected.'))
                return
            self.rematch_sent = True
            self.lan.send({'t': 'rematch'})
            self.status.setText(tr('Rematch requested…'))
            self.maybe_start_lan_rematch()
            return
        w, b = self.players[chess.WHITE], self.players[chess.BLACK]
        self.start_game(self.mode, b, w, not self.my_color if self.mode == 'bot' else chess.WHITE, self.tc,
                        bot=self.bot, bot_elo=self.bot_elo, rules=self.rules.copy() if self.rules.active else None, intro=False)

    def maybe_start_lan_rematch(self):
        if not (self.rematch_sent and self.rematch_recv) or self.lan is None:
            return
        if self.lan.role == 'host':
            w, b = self.players[chess.WHITE], self.players[chess.BLACK]
            self.lan.send({'t': 'start', 'host_color': 'white' if self.my_color == chess.BLACK else 'black',
                           'tc': list(self.tc), 'rules': self.rules.to_json() if self.rules.active else None})
            self.start_game('lan', b, w, not self.my_color, self.tc, lan=self.lan,
                            rules=self.rules.copy() if self.rules.active else None, intro=False)

    def add_friend(self):
        opp = self.players[not self.my_color]
        if self.lan is not None and self.lan.connected and opp:
            self.lan.send({'t': 'friend_req'})
            self.status.setText(tr('Friend request sent.'))

    # ------------------------------------------------------------ LAN
    def lan_message(self, msg):
        t = msg.get('t')
        if t == 'move':
            try:
                move = chess.Move.from_uci(msg.get('uci', ''))
            except ValueError:
                return
            mover = self.board.turn
            if mover == self.my_color or self.finished:
                return
            if self.make_move(move, animate=True, from_network=True):
                left = msg.get('left')
                if isinstance(left, (int, float)):
                    self.times[mover] = float(left)
                    self.last_tick = time.monotonic()
                    self.update_clocks()
            else:
                QMessageBox.warning(self, tr('LAN game'), tr('The boards are out of sync. Please start a new game.'))
        elif t == 'rules' and not self.finished:
            self.rules.load_json(msg.get('data') or {})
            self.rules_used = self.rules_used or self.rules.active
            self.rated = False
            self.bw.no_capture = set(self.rules.no_capture)
            self.recompute_state()
            self.status.setText(tr('The other player changed the rules.'))
            self.refresh()
            if self.state:
                self.finish(self.state[0], self.state[1])
        elif t == 'resign' and not self.finished:
            self.finish('resign', self.my_color)
        elif t == 'flag' and not self.finished:
            self.finish('timeout', not bool(msg.get('loser')))
        elif t == 'draw_offer' and not self.finished:
            self.app.sound.play('notify')
            ok = QMessageBox.question(self, tr('Draw'), tr('Your opponent offers a draw. Accept?')) == QMessageBox.StandardButton.Yes
            if self.lan is not None:
                self.lan.send({'t': 'draw_accept' if ok else 'draw_decline'})
            if ok:
                self.finish('agreed', None)
        elif t == 'draw_accept' and not self.finished:
            self.finish('agreed', None)
        elif t == 'draw_decline':
            self.status.setText(tr('Your draw offer was declined.'))
        elif t == 'rematch':
            self.rematch_recv = True
            self.app.sound.play('notify')
            self.status.setText(tr('Your opponent wants a rematch.'))
            self.maybe_start_lan_rematch()

    def lan_closed(self, reason):
        if self.mode != 'lan':
            return
        if not self.finished and len(self.board.move_stack) >= 2:
            self.status.setText(tr(reason))
            self.finish('disconnect', self.my_color)
        elif not self.finished:
            self.status.setText(tr(reason))
            self.refresh()
        else:
            self.status.setText(tr(reason))

    # --------------------------------------------------------- PGN / review
    def build_pgn(self, result, reason=''):
        import datetime
        w, b = self.players[chess.WHITE], self.players[chess.BLACK]
        heads = [('Event', 'My Chess game'), ('Site', 'My Chess'), ('Date', datetime.date.today().strftime('%Y.%m.%d')),
                 ('White', w['name']), ('Black', b['name']), ('Result', result)]
        if w['rating'] is not None:
            heads.append(('WhiteElo', w['rating']))
        if b['rating'] is not None:
            heads.append(('BlackElo', b['rating']))
        if self.tc[0] > 0:
            heads.append(('TimeControl', '%d+%d' % self.tc))
        if reason:
            heads.append(('Termination', reason))
        if self.rules_used:
            heads.append(('Note', 'House rules were used'))
        if self.start_fen != chess.STARTING_FEN:
            heads += [('SetUp', '1'), ('FEN', self.start_fen)]
        text = '\n'.join('[%s "%s"]' % (k, str(v).replace('"', "'")) for k, v in heads) + '\n\n'
        parts = []
        for i, san in enumerate(self.san_list):
            parts.append(('%d. ' % (i // 2 + 1) if i % 2 == 0 else '') + san)
        return text + ' '.join(parts) + ' ' + result + '\n'

    def save_pgn(self):
        path, _ = QFileDialog.getSaveFileName(self, tr('Save game as PGN'), 'game.pgn', 'PGN (*.pgn)')
        if not path:
            return
        res = '*'
        if self.finished:
            w = self.result['winner']
            res = '1/2-1/2' if w is None else '1-0' if w == chess.WHITE else '0-1'
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.build_pgn(res, self.result['kind'] if self.finished else ''))
            self.status.setText(tr('PGN saved.'))
        except OSError as e:
            QMessageBox.warning(self, tr('Save PGN'), str(e))

    def open_review(self):
        if not self.board.move_stack:
            return
        if self.rules_used:
            QMessageBox.information(self, tr('Game Review'), tr('Game review needs standard chess rules.'))
            return
        entry = self.last_entry or {
            'moves': [m.uci() for m in self.board.move_stack], 'sans': list(self.san_list), 'start_fen': self.start_fen,
            'white': self.players[chess.WHITE]['name'], 'black': self.players[chess.BLACK]['name'],
            'white_elo': self.players[chess.WHITE]['rating'], 'black_elo': self.players[chess.BLACK]['rating'],
            'color': 'white' if self.my_color == chess.WHITE else 'black', 'result': '*'}
        self.app.open_review(entry)

    def stop(self):
        """Called when leaving the page for good."""
        self.bot_job += 1
        self.bot_busy = False
