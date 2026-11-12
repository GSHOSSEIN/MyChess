"""Lessons: interactive teaching with the selected coach."""
import chess
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QPushButton, QListWidget,
                               QListWidgetItem, QProgressBar)

import coaches
from i18n import tr
from lessons_data import LESSONS
from trainer import TrainerController
from widgets import BoardWidget, CoachBubble, THEME


class LessonPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.lesson = None
        self.step_index = 0
        self.solved = False
        self.fails = 0
        root = QHBoxLayout(self)
        root.setContentsMargins(20, 12, 20, 12)
        root.setSpacing(18)
        left = QVBoxLayout()
        title = QLabel(tr('Lessons'))
        title.setObjectName('pageTitle')
        left.addWidget(title)
        self.list = QListWidget()
        self.list.setFixedWidth(270)
        self.list.currentRowChanged.connect(self.pick_lesson)
        left.addWidget(self.list, 1)
        root.addLayout(left)
        self.bw = BoardWidget(app.pieces)
        self.ctl = TrainerController(self.bw, self.on_move)
        root.addWidget(self.bw, 1)
        panel = QFrame()
        panel.setObjectName('panel')
        panel.setFixedWidth(360)
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(14, 14, 14, 14)
        pl.setSpacing(10)
        self.heading = QLabel('')
        self.heading.setStyleSheet('font-size:18px;font-weight:bold;')
        self.heading.setWordWrap(True)
        pl.addWidget(self.heading)
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        pl.addWidget(self.progress)
        self.coach_box = CoachBubble(56)
        pl.addWidget(self.coach_box)
        self.task_label = QLabel('')
        self.task_label.setWordWrap(True)
        self.task_label.setStyleSheet('font-weight:bold;')
        pl.addWidget(self.task_label)
        pl.addStretch(1)
        row = QHBoxLayout()
        self.hint_btn = QPushButton(tr('Hint'))
        self.hint_btn.clicked.connect(self.hint)
        self.show_btn = QPushButton(tr('Show me'))
        self.show_btn.clicked.connect(self.show_answer)
        row.addWidget(self.hint_btn)
        row.addWidget(self.show_btn)
        pl.addLayout(row)
        row2 = QHBoxLayout()
        self.back_btn = QPushButton(tr('Back'))
        self.back_btn.clicked.connect(self.prev_step)
        self.next_btn = QPushButton(tr('Next'))
        self.next_btn.setObjectName('primary')
        self.next_btn.clicked.connect(self.next_step)
        row2.addWidget(self.back_btn)
        row2.addWidget(self.next_btn, 1)
        pl.addLayout(row2)
        root.addWidget(panel)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._reset_step)

    # ------------------------------------------------------------- list
    def refresh(self):
        done = set(self.app.store.prefs.get('lessons_done', []))
        row = self.list.currentRow()
        self.list.blockSignals(True)
        self.list.clear()
        for les in LESSONS:
            mark = '✔  ' if les['id'] in done else '○  '
            item = QListWidgetItem('%s%s\n     %s' % (mark, les['title'], tr(les['level'])))
            self.list.addItem(item)
        self.list.blockSignals(False)
        c = self.app.coach()
        self.coach_box.set_coach(c.name, self.app.coach_pixmap())
        self.bw.light, self.bw.dark = self.app.light_color(), self.app.dark_color()
        self.bw.show_coords = self.app.store.prefs.get('show_coordinates', True)
        self.bw.clear_cache()
        if self.lesson is None:
            self.list.setCurrentRow(max(0, row))
        else:
            self.list.setCurrentRow(LESSONS.index(self.lesson))

    def pick_lesson(self, row):
        if 0 <= row < len(LESSONS):
            self.lesson = LESSONS[row]
            self.show_step(0)

    # ------------------------------------------------------------ steps
    def show_step(self, i):
        les = self.lesson
        self.step_index = max(0, min(len(les['steps']) - 1, i))
        st = les['steps'][self.step_index]
        self._timer.stop()
        self.solved = False
        self.fails = 0
        board = chess.Board(st['fen'])
        task = st.get('task')
        self.ctl.enabled = bool(task)
        self.ctl.show_square = chess.parse_square(st['show']) if st.get('show') else None
        self.ctl.set_board(board, None, flipped=(board.turn == chess.BLACK) if task else False)
        self.bw.hint_arrows = [(chess.parse_square(a), chess.parse_square(b), 'blue') for a, b in st.get('arrows', [])]
        self.ctl.refresh()
        total = len(les['steps'])
        self.progress.setRange(0, total)
        self.progress.setValue(self.step_index + 1)
        self.heading.setText('%s  (%d/%d)' % (les['title'], self.step_index + 1, total))
        c = self.app.coach()
        self.coach_box.set_coach(c.name, self.app.coach_pixmap())
        self.coach_box.say(st['text'])
        self.task_label.setText(tr('Your turn: make the right move on the board.') if task else '')
        self.hint_btn.setVisible(bool(task))
        self.show_btn.setVisible(bool(task))
        self.back_btn.setEnabled(self.step_index > 0)
        last = self.step_index == total - 1
        self.next_btn.setText(tr('Finish') if last else tr('Next'))
        self.next_btn.setEnabled(not task)

    def prev_step(self):
        self.show_step(self.step_index - 1)

    def next_step(self):
        if self.step_index >= len(self.lesson['steps']) - 1:
            done = self.app.store.prefs.setdefault('lessons_done', [])
            if self.lesson['id'] not in done:
                done.append(self.lesson['id'])
                self.app.store.save_prefs()
            self.refresh()
            nxt = LESSONS.index(self.lesson) + 1
            if nxt < len(LESSONS):
                self.list.setCurrentRow(nxt)
            else:
                self.coach_box.say(tr("You finished every lesson. Great work! Try some puzzles next."))
            return
        self.show_step(self.step_index + 1)

    # ------------------------------------------------------------ tasks
    def is_correct(self, move):
        st = self.lesson['steps'][self.step_index]
        if st.get('task') == 'mate1':
            b = self.ctl.board.copy()
            b.push(move)
            return b.is_checkmate()
        for a in st.get('answers', []):
            if len(a) == 2:
                if move.to_square == chess.parse_square(a):
                    return True
            elif move.uci() == a:
                return True
        return False

    def on_move(self, move):
        st = self.lesson['steps'][self.step_index]
        tone = self.app.coach().tone
        if self.is_correct(move):
            self.ctl.enabled = False
            self.ctl.apply(move)
            self.solved = True
            self.app.sound.play('capture' if self.ctl.board.is_check() else 'move')
            self.coach_box.say(coaches.line(tone, 'lesson_ok'), '#81b64c')
            self.next_btn.setEnabled(True)
        else:
            self.fails += 1
            self.app.sound.play('notify')
            txt = coaches.line(tone, 'lesson_bad')
            if st.get('hint') and self.fails >= 2:
                txt += ' ' + st['hint']
            self.coach_box.say(txt, '#ca3431')
            self.ctl.enabled = False
            self.ctl.apply(move, animate=False)
            self._timer.start(900)

    def _reset_step(self):
        st = self.lesson['steps'][self.step_index]
        board = chess.Board(st['fen'])
        self.ctl.set_board(board, None, flipped=(board.turn == chess.BLACK))
        self.ctl.enabled = True

    def solution_move(self):
        st = self.lesson['steps'][self.step_index]
        board = chess.Board(st['fen'])
        for m in board.legal_moves:
            b = board.copy()
            b.push(m)
            if st.get('task') == 'mate1' and b.is_checkmate():
                return m
            for a in st.get('answers', []):
                if (len(a) == 2 and m.to_square == chess.parse_square(a)) or m.uci() == a:
                    return m
        return None

    def hint(self):
        st = self.lesson['steps'][self.step_index]
        self.coach_box.say(st.get('hint') or tr('Look for forcing moves: checks and captures.'))

    def show_answer(self):
        m = self.solution_move()
        if m is not None and not self.solved:
            self.bw.hint_arrows = [(m.from_square, m.to_square, 'best')]
            self.bw.update()
