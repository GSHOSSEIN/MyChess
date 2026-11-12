"""Puzzles: find the mate. Solutions are checked with python-chess, so any correct mating line is accepted."""
import random

import chess
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QPushButton, QComboBox)

import coaches
from i18n import tr
from puzzles_data import PUZZLES
from store import elo_change
from trainer import TrainerController
from widgets import BoardWidget, CoachBubble, THEME


def mate_in_one_exists(board):
    for m in board.legal_moves:
        board.push(m)
        mate = board.is_checkmate()
        board.pop()
        if mate:
            return True
    return False


def forces_mate_next(board):
    """True if, after the side to move's reply (any), the other side has mate in one."""
    replies = list(board.legal_moves)
    if not replies:
        return False
    for r in replies:
        board.push(r)
        ok = mate_in_one_exists(board)
        board.pop()
        if not ok:
            return False
    return True


class PuzzlePage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.puzzle = None
        self.start_board = None
        self.stage = 0
        self.failed = False
        self.hinted = False
        self.done = False
        self.user_color = chess.WHITE
        root = QHBoxLayout(self)
        root.setContentsMargins(20, 12, 20, 12)
        root.setSpacing(18)
        self.bw = BoardWidget(app.pieces)
        self.ctl = TrainerController(self.bw, self.on_move)
        root.addWidget(self.bw, 1)
        panel = QFrame()
        panel.setObjectName('panel')
        panel.setFixedWidth(360)
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(14, 14, 14, 14)
        pl.setSpacing(10)
        title = QLabel(tr('Puzzles'))
        title.setObjectName('pageTitle')
        pl.addWidget(title)
        self.kind = QComboBox()
        self.kind.addItem(tr('All puzzles'), 'all')
        self.kind.addItem(tr('Mate in 1'), 'mate1')
        self.kind.addItem(tr('Mate in 2'), 'mate2')
        self.kind.currentIndexChanged.connect(lambda i: self.next_puzzle())
        pl.addWidget(self.kind)
        self.info = QLabel('')
        self.info.setStyleSheet('font-size:16px;font-weight:bold;')
        pl.addWidget(self.info)
        self.stats = QLabel('')
        self.stats.setObjectName('muted')
        self.stats.setWordWrap(True)
        pl.addWidget(self.stats)
        self.coach_box = CoachBubble(56)
        pl.addWidget(self.coach_box)
        self.turn_label = QLabel('')
        self.turn_label.setStyleSheet('font-weight:bold;')
        pl.addWidget(self.turn_label)
        pl.addStretch(1)
        row = QHBoxLayout()
        self.hint_btn = QPushButton(tr('Hint'))
        self.hint_btn.clicked.connect(self.hint)
        self.sol_btn = QPushButton(tr('Show solution'))
        self.sol_btn.clicked.connect(self.show_solution)
        row.addWidget(self.hint_btn)
        row.addWidget(self.sol_btn)
        pl.addLayout(row)
        row2 = QHBoxLayout()
        self.skip_btn = QPushButton(tr('Skip'))
        self.skip_btn.clicked.connect(self.next_puzzle)
        self.next_btn = QPushButton(tr('Next puzzle'))
        self.next_btn.setObjectName('primary')
        self.next_btn.clicked.connect(self.next_puzzle)
        row2.addWidget(self.skip_btn)
        row2.addWidget(self.next_btn, 1)
        pl.addLayout(row2)
        root.addWidget(panel)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._after_timer)
        self._pending = None

    # --------------------------------------------------------- selection
    def prefs(self):
        return self.app.store.prefs

    def rating(self):
        return int(self.prefs().get('puzzle_rating', 800))

    def refresh(self):
        self.bw.light, self.bw.dark = self.app.light_color(), self.app.dark_color()
        self.bw.show_coords = self.prefs().get('show_coordinates', True)
        self.bw.clear_cache()
        c = self.app.coach()
        self.coach_box.set_coach(c.name, self.app.coach_pixmap())
        if self.puzzle is None:
            self.next_puzzle()
        else:
            self.update_stats()

    def update_stats(self):
        p = self.prefs()
        solved = len(p.get('puzzles_solved', []))
        self.stats.setText(tr('Puzzle rating: {r}   ·   Solved: {s}/{t}   ·   Streak: {k}').format(
            r=self.rating(), s=solved, t=len(PUZZLES), k=p.get('puzzle_streak', 0)))

    def next_puzzle(self):
        kind = self.kind.currentData()
        pool = [p for p in PUZZLES if kind in ('all', None) or p['kind'] == kind]
        solved = set(self.prefs().get('puzzles_solved', []))
        fresh = [p for p in pool if p['id'] not in solved]
        if not fresh:
            fresh = pool
        r = self.rating()
        fresh.sort(key=lambda p: abs(p['rating'] - r) + random.random() * 140)
        if self.puzzle is not None and len(fresh) > 1 and fresh[0]['id'] == self.puzzle['id']:
            fresh = fresh[1:]
        self.load(fresh[0])

    def load(self, puzzle):
        self._timer.stop()
        self.puzzle = puzzle
        board = chess.Board(puzzle['fen'])
        self.start_board = board.copy()
        self.user_color = board.turn
        self.stage = 0
        self.failed = False
        self.hinted = False
        self.done = False
        self.ctl.enabled = True
        self.ctl.set_board(board, None, flipped=(board.turn == chess.BLACK))
        self.info.setText('%s   (%d)' % (tr(puzzle['title']), puzzle['rating']))
        self.turn_label.setText(tr('White to move') if board.turn == chess.WHITE else tr('Black to move'))
        self.coach_box.say(tr('Find the checkmate!') if puzzle['n'] == 1 else tr('Find the move that forces checkmate in two moves.'))
        self.hint_btn.setEnabled(True)
        self.sol_btn.setEnabled(True)
        self.update_stats()

    # ------------------------------------------------------------ moves
    def on_move(self, move):
        if self.done:
            return
        tone = self.app.coach().tone
        board = self.ctl.board
        test = board.copy()
        test.push(move)
        remaining = self.puzzle['n'] - self.stage
        if remaining == 1:
            good = test.is_checkmate()
        else:
            good = (not test.is_game_over()) and forces_mate_next(test)
        if not good:
            self.on_wrong(tone)
            return
        self.ctl.enabled = False
        self.ctl.apply(move)
        self.app.sound.play('check' if self.ctl.board.is_check() else 'move')
        if remaining == 1:
            self.success(tone)
        else:
            self.stage += 1
            self._pending = 'reply'
            self._timer.start(650)

    def _after_timer(self):
        if self._pending == 'reply':
            board = self.ctl.board
            legal = list(board.legal_moves)
            reply = None
            if len(self.puzzle['sol']) > 1 and self.stage == 1:
                try:
                    cand = chess.Move.from_uci(self.puzzle['sol'][1])
                    if cand in legal:
                        reply = cand
                except ValueError:
                    pass
            if reply is None and legal:
                reply = legal[0]
            if reply is not None:
                self.ctl.apply(reply)
                self.app.sound.play('move_opponent')
            self.ctl.enabled = True
            self.coach_box.say(tr('Now deliver checkmate!'))
        self._pending = None

    def on_wrong(self, tone):
        self.app.sound.play('notify')
        if not self.failed:
            self.failed = True
            self.apply_rating(0.0)
            self.prefs()['puzzle_streak'] = 0
            self.app.store.save_prefs()
        self.coach_box.say(coaches.line(tone, 'puzzle_bad'), '#ca3431')
        self.ctl.refresh()                       # the wrong move was never played: the piece simply returns
        self.update_stats()

    def apply_rating(self, score):
        p = self.prefs()
        r = self.rating()
        p['puzzle_rating'] = max(100, r + elo_change(r, self.puzzle['rating'], score, 20))
        self.app.store.save_prefs()

    def success(self, tone):
        self.done = True
        p = self.prefs()
        solved = p.setdefault('puzzles_solved', [])
        if self.puzzle['id'] not in solved:
            solved.append(self.puzzle['id'])
        if not self.failed and not self.hinted:
            self.apply_rating(1.0)
            p['puzzle_streak'] = p.get('puzzle_streak', 0) + 1
            p['puzzle_best_streak'] = max(p.get('puzzle_best_streak', 0), p['puzzle_streak'])
        self.app.store.save_prefs()
        self.app.sound.play('end')
        self.coach_box.say(coaches.line(tone, 'puzzle_ok') + ' ' + tr('Press "Next puzzle" to continue.'), '#81b64c')
        self.update_stats()

    # ------------------------------------------------------------- help
    def solution_first(self):
        board = self.ctl.board
        remaining = self.puzzle['n'] - self.stage
        for m in board.legal_moves:
            b = board.copy()
            b.push(m)
            if remaining == 1 and b.is_checkmate():
                return m
            if remaining > 1 and not b.is_game_over() and forces_mate_next(b):
                return m
        return None

    def hint(self):
        if self.done:
            return
        m = self.solution_first()
        if m is not None:
            self.hinted = True
            self.bw.highlights = {m.from_square}
            self.bw.update()
            piece = self.ctl.board.piece_at(m.from_square)
            names = {chess.PAWN: 'pawn', chess.KNIGHT: 'knight', chess.BISHOP: 'bishop', chess.ROOK: 'rook', chess.QUEEN: 'queen', chess.KING: 'king'}
            self.coach_box.say(tr('Hint: look at your {piece}.').format(piece=tr(names[piece.piece_type])))

    def show_solution(self):
        if self.done:
            return
        m = self.solution_first()
        if m is not None:
            self.hinted = True
            self.failed = True
            self.bw.hint_arrows = [(m.from_square, m.to_square, 'best')]
            self.bw.update()
            self.coach_box.say(tr('The solution is {move}.').format(move=self.ctl.board.san(m)))
