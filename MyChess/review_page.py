"""Game Review screen with a coach, move ratings, evaluation graph and accuracy summary."""
import threading

import chess
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QShortcut, QKeySequence, QPixmap
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QPushButton, QProgressBar,
                               QTabWidget, QGridLayout, QMessageBox)

import coaches
import engines
import review as rv
from bots import bot_by_id
from i18n import tr
from widgets import BoardWidget, EvalBar, EvalGraph, MoveTable, PlayerStrip, AvatarLabel, review_icon, THEME, ASSETS
import os

BAD = ('inaccuracy', 'mistake', 'miss', 'blunder')


class ReviewPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.entry = None
        self.moves = []
        self.boards = []
        self.sans = []
        self.evals = None
        self.reviews = []
        self.ply = 0
        self.token = 0
        self.progress = (0, 1)
        self.done = False
        self.show_best = False
        self.flipped = False
        self._build()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll)
        self.timer.start(120)
        for key, fn in ((Qt.Key.Key_Left, lambda: self.goto(self.ply - 1)), (Qt.Key.Key_Right, lambda: self.goto(self.ply + 1)),
                        (Qt.Key.Key_Up, lambda: self.goto(0)), (Qt.Key.Key_Down, lambda: self.goto(len(self.moves)))):
            sc = QShortcut(QKeySequence(key), self)
            sc.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
            sc.activated.connect(fn)

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(8, 4, 8, 4)
        root.setSpacing(14)
        self.bar = EvalBar()
        root.addWidget(self.bar)
        left = QVBoxLayout()
        left.setSpacing(4)
        self.top = PlayerStrip()
        self.bottom = PlayerStrip()
        for s in (self.top, self.bottom):
            s.clock.setVisible(False)
        self.bw = BoardWidget(self.app.pieces)
        self.bw.interactive = False
        left.addWidget(self.top)
        left.addWidget(self.bw, 1)
        left.addWidget(self.bottom)
        root.addLayout(left, 1)

        panel = QFrame()
        panel.setObjectName('panel')
        panel.setFixedWidth(390)
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(14, 14, 14, 14)
        pl.setSpacing(8)
        head = QLabel(tr('Game Review'))
        head.setStyleSheet('font-size:20px;font-weight:800;')
        pl.addWidget(head)
        coach = QHBoxLayout()
        self.coach_av = AvatarLabel(58)
        self.coach_av.set_avatar(self.app.coach_pixmap(), 'C')
        coach.addWidget(self.coach_av, alignment=Qt.AlignmentFlag.AlignTop)
        self.bubble = QLabel('')
        self.bubble.setWordWrap(True)
        self.bubble.setMinimumHeight(84)
        self.bubble.setStyleSheet('background:%s;border-radius:10px;padding:10px;font-size:14px;' % THEME['panel2'])
        self.bubble.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        coach.addWidget(self.bubble, 1)
        self.bubble_icon = QLabel('')
        self.bubble_icon.setFixedWidth(40)
        coach.addWidget(self.bubble_icon, alignment=Qt.AlignmentFlag.AlignTop)
        pl.addLayout(coach)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        pl.addWidget(self.progress_bar)
        self.note = QLabel('')
        self.note.setWordWrap(True)
        self.note.setObjectName('muted')
        pl.addWidget(self.note)
        nav = QHBoxLayout()
        for text, fn in (('|<', lambda: self.goto(0)), ('<', lambda: self.goto(self.ply - 1)),
                         ('>', lambda: self.goto(self.ply + 1)), ('>|', lambda: self.goto(len(self.moves)))):
            b = QPushButton(text)
            b.clicked.connect(lambda checked=False, f=fn: f())
            nav.addWidget(b)
        pl.addLayout(nav)
        row = QHBoxLayout()
        self.best_btn = QPushButton(tr('Show best move'))
        self.best_btn.setCheckable(True)
        self.best_btn.toggled.connect(self.toggle_best)
        flip = QPushButton(tr('Flip'))
        flip.clicked.connect(self.flip)
        row.addWidget(self.best_btn)
        row.addWidget(flip)
        pl.addLayout(row)
        self.tabs = QTabWidget()
        mv = QWidget()
        ml = QVBoxLayout(mv)
        ml.setContentsMargins(0, 6, 0, 0)
        self.table = MoveTable()
        self.table.ply_selected.connect(self.goto)
        ml.addWidget(self.table, 1)
        self.graph = EvalGraph()
        self.graph.ply_clicked.connect(self.goto)
        ml.addWidget(self.graph)
        self.tabs.addTab(mv, tr('Moves'))
        self.summary = QWidget()
        self.sum_layout = QGridLayout(self.summary)
        self.sum_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.tabs.addTab(self.summary, tr('Summary'))
        pl.addWidget(self.tabs, 1)
        back = QPushButton(tr('Back'))
        back.clicked.connect(self.app.go_back_from_review)
        pl.addWidget(back)
        root.addWidget(panel)

    # --------------------------------------------------------------- loading
    def load(self, entry):
        self.token += 1
        self.entry = entry
        self.coach_av.set_avatar(self.app.coach_pixmap(), 'C')
        self.evals = None
        self.reviews = []
        self.done = False
        self.show_best = False
        self.best_btn.setChecked(False)
        start_fen = entry.get('start_fen') or chess.STARTING_FEN
        board = chess.Board(start_fen)
        self.boards = [board.copy(stack=False)]
        self.moves, self.sans = [], []
        for uci in entry.get('moves', []):
            try:
                m = chess.Move.from_uci(uci)
            except ValueError:
                break
            if m not in board.legal_moves:
                break
            self.sans.append(board.san(m))
            board.push(m)
            self.moves.append(m)
            self.boards.append(board.copy(stack=False))
        self.start_fen = start_fen
        self.flipped = entry.get('color') == 'black'
        self.table.set_moves([(s, None) for s in self.sans])
        self.graph.set_data([])
        self.clear_summary()
        self.bw.light, self.bw.dark = self.app.light_color(), self.app.dark_color()
        self.bw.show_coords = self.app.store.prefs.get('show_coordinates', True)
        self.bw.clear_cache()
        self.set_players()
        if not self.moves:
            self.bubble.setText(tr('There are no moves to review.'))
            self.progress_bar.setVisible(False)
            self.goto(0)
            return
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        path = self.app.engine_path()
        self.note.setText(tr('Analyzing with Stockfish…') if path else
                          tr('Stockfish was not found: using the built-in engine (basic analysis).'))
        self.bubble.setText(tr('Let me take a look at the game…'))
        token = self.token
        moves = list(self.moves)

        def prog(i, n):
            if token == self.token:
                self.progress = (i, n)

        def work():
            try:
                res = engines.analyse_game(start_fen, moves, path, 0.25, prog, lambda: token != self.token)
            except Exception:
                res = None
            if token == self.token:
                self.evals = res
                self.done = True
        threading.Thread(target=work, daemon=True).start()
        self.goto(0)

    def cancel(self):
        self.token += 1

    def set_players(self):
        e = self.entry
        white = {'name': e.get('white', tr('White')), 'rating': e.get('white_elo'), 'pix': None}
        black = {'name': e.get('black', tr('Black')), 'rating': e.get('black_elo'), 'pix': None}
        me_color = e.get('color')
        opp = e.get('opponent', {}) or {}
        pix_me = self.app.my_pixmap()
        pix_opp = None
        if opp.get('bot'):
            pix_opp = self.app.bot_pixmap(bot_by_id(opp['bot']))
        elif opp.get('id'):
            f = self.app.store.find_friend(opp['id'])
            pix_opp = self.app.friend_pixmap(f) if f else None
        if me_color == 'white':
            white['pix'], black['pix'] = pix_me, pix_opp
        elif me_color == 'black':
            white['pix'], black['pix'] = pix_opp, pix_me
        self.info = {chess.WHITE: white, chess.BLACK: black}
        for color, strip in ((chess.WHITE, None), (chess.BLACK, None)):
            pass
        self.place()

    def place(self):
        top = chess.WHITE if self.flipped else chess.BLACK
        for strip, color in ((self.top, top), (self.bottom, not top)):
            i = self.info[color]
            strip.set_player(i['name'], i['rating'], i['pix'])
        self.bw.flipped = self.flipped
        self.bw.clear_cache()

    def flip(self):
        self.flipped = not self.flipped
        self.place()
        self.goto(self.ply)

    def toggle_best(self, on):
        self.show_best = on
        self.goto(self.ply)

    # ------------------------------------------------------------- analysis
    def poll(self):
        if not self.isVisible() and not self.done:
            return
        if self.entry and not self.done and self.moves:
            i, n = self.progress
            self.progress_bar.setValue(int(100 * i / max(1, n)))
        if self.done and self.evals is not None and not self.reviews and self.moves:
            self.finish_analysis()
        elif self.done and self.evals is None and self.progress_bar.isVisible():
            self.progress_bar.setVisible(False)
            self.note.setText(tr('The analysis could not be completed.'))

    def finish_analysis(self):
        self.progress_bar.setVisible(False)
        self.reviews = rv.review_game(self.start_fen, self.moves, self.evals)
        self.note.setText(tr('Analysis complete.') + ('' if self.app.engine_path() else ' ' + tr('(basic engine)')))
        self.table.set_moves([(s, rv.LABEL_STYLE[r['label']][0], review_icon(r['label'], 20))
                              for s, r in zip(self.sans, self.reviews)])
        self.graph.set_data([engines.win_percent(e['cp']) for e in self.evals])
        self.fill_summary()
        self.bubble.setText(tr("Analysis done! Use the arrows to step through the game."))
        self.goto(self.ply)

    def clear_summary(self):
        while self.sum_layout.count():
            item = self.sum_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def fill_summary(self):
        self.clear_summary()
        wc, wacc = rv.summarize(self.reviews, chess.WHITE)
        bc, bacc = rv.summarize(self.reviews, chess.BLACK)
        g = self.sum_layout
        g.setHorizontalSpacing(14)
        g.setVerticalSpacing(6)
        for col, (name, acc) in ((1, (self.info[chess.WHITE]['name'], wacc)), (2, (self.info[chess.BLACK]['name'], bacc))):
            h = QLabel(name)
            h.setStyleSheet('font-weight:bold;')
            h.setAlignment(Qt.AlignmentFlag.AlignCenter)
            g.addWidget(h, 0, col)
            a = QLabel('%.1f%%' % acc)
            a.setAlignment(Qt.AlignmentFlag.AlignCenter)
            a.setStyleSheet('font-size:22px;font-weight:900;background:%s;border-radius:8px;padding:6px;color:#262522;' % ('#f2f2f2' if col == 1 else '#cfcfcf'))
            g.addWidget(a, 1, col)
        g.addWidget(QLabel(tr('Accuracy')), 1, 0)
        row = 2
        for label in rv.LABEL_ORDER:
            color, symbol = rv.LABEL_STYLE[label]
            cell = QWidget()
            ch = QHBoxLayout(cell)
            ch.setContentsMargins(0, 0, 0, 0)
            ic = QLabel()
            pm = review_icon(label, 22)
            if pm is not None:
                ic.setPixmap(pm)
            else:
                ic.setText(symbol)
            ch.addWidget(ic)
            ch.addWidget(QLabel(rv.label_name(label)))
            ch.addStretch(1)
            g.addWidget(cell, row, 0)
            for col, counts in ((1, wc), (2, bc)):
                c = QLabel(str(counts[label]))
                c.setAlignment(Qt.AlignmentFlag.AlignCenter)
                g.addWidget(c, row, col)
            row += 1

    # ------------------------------------------------------------ navigation
    def goto(self, ply):
        if not self.boards:
            return
        ply = max(0, min(len(self.moves), ply))
        self.ply = ply
        board = self.boards[ply]
        last = self.moves[ply - 1] if ply > 0 else None
        check_sq = board.king(board.turn) if board.is_check() else None
        self.bw.badge = None
        self.bw.hint_arrows = []
        review = self.reviews[ply - 1] if (self.reviews and ply > 0) else None
        if review is not None:
            color, symbol = rv.LABEL_STYLE[review['label']]
            self.bw.badge = (last.to_square, color, symbol, review_icon(review['label'], 64))
            if review['label'] in BAD and review['best_uci']:
                try:
                    bm = chess.Move.from_uci(review['best_uci'])
                    self.bw.hint_arrows.append((bm.from_square, bm.to_square, 'best'))
                except ValueError:
                    pass
        if self.show_best and self.evals and ply < len(self.evals) and self.evals[ply]['best']:
            try:
                bm = chess.Move.from_uci(self.evals[ply]['best'])
                self.bw.hint_arrows = [(bm.from_square, bm.to_square, 'blue')]
            except ValueError:
                pass
        self.bw.set_position(board, last, check_sq)
        self.table.set_current(ply)
        self.graph.set_current(ply)
        # eval bar
        if self.evals:
            e = self.evals[ply]
            wp = engines.win_percent(e['cp'])
            if e['mate'] is not None:
                text = '#' if e['mate'] == 0 else 'M%d' % abs(e['mate'])
            else:
                text = '%+.1f' % (e['cp'] / 100.0)
            self.bar.set_value(wp, text, self.flipped)
        else:
            self.bar.set_value(50, '0.0', self.flipped)
        # coach
        if review is not None:
            tone = self.app.coach().tone
            self.bubble.setText((coaches.label_line(tone, review['label']) + ' ' + rv.coach_text(review)).strip())
            color, _ = rv.LABEL_STYLE[review['label']]
            pm = review_icon(review['label'], 32)
            self.bubble_icon.setPixmap(pm) if pm is not None else self.bubble_icon.setText(rv.LABEL_STYLE[review['label']][1])
            self.bubble.setStyleSheet('background:%s;border-radius:10px;padding:10px;font-size:14px;border-left:5px solid %s;' % (THEME['panel2'], color))
        elif ply == 0 and self.reviews:
            self.bubble_icon.clear()
            self.bubble.setText(tr("Let's review the game! Step through the moves with the arrow keys."))
            self.bubble.setStyleSheet('background:%s;border-radius:10px;padding:10px;font-size:14px;' % THEME['panel2'])
