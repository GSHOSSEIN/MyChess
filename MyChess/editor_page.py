"""Custom positions: set up any position, save it, and play it against a bot or a friend."""
import chess
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QGuiApplication
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QPushButton, QComboBox, QLineEdit,
                               QToolButton, QGridLayout, QButtonGroup, QCheckBox, QInputDialog, QMessageBox)

from bots import BOTS
from i18n import tr
from widgets import BoardWidget, THEME

PRESETS = [
    ('King + Queen vs King', '8/8/8/4k3/8/8/8/3QK3 w - - 0 1'),
    ('King + Rook vs King', '8/8/8/4k3/8/8/8/R3K3 w - - 0 1'),
    ('Lucena position', '1K1k4/1P6/8/8/8/8/r7/2R5 w - - 0 1'),
    ('Two bishops mate', '8/8/8/8/8/2k5/8/KBB5 w - - 0 1'),
    ('Bishop + knight mate', '8/8/8/8/8/3k4/8/KNB5 w - - 0 1'),
    ('Queens only', '3qk3/8/8/8/8/8/8/3QK3 w - - 0 1'),
    ('Pawns only', '4k3/pppppppp/8/8/8/8/PPPPPPPP/4K3 w - - 0 1'),
    ('Rooks and kings', 'r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1'),
    ('Knights vs bishops', '2b1kb2/pppppppp/8/8/8/8/PPPPPPPP/2N1KN2 w - - 0 1'),
]
TYPES = [chess.KING, chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN]


class EditorController:
    def __init__(self, page):
        self.page = page

    def on_left_press(self, sq):
        return self.page.press(sq)

    def on_left_release(self, src, dst, dragged):
        self.page.release(src, dst, dragged)

    def on_right_release(self, start, end, color, pos):
        self.page.erase(start)

    def on_promotion(self, src, dst, ptype):
        pass


class EditorPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.tool = 'move'
        self.board = chess.Board.empty()
        root = QHBoxLayout(self)
        root.setContentsMargins(20, 12, 20, 12)
        root.setSpacing(18)
        self.bw = BoardWidget(app.pieces)
        self.bw.controller = EditorController(self)
        self.bw.interactive = True
        root.addWidget(self.bw, 1)
        panel = QFrame()
        panel.setObjectName('panel')
        panel.setFixedWidth(400)
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(14, 12, 14, 12)
        pl.setSpacing(7)
        t = QLabel(tr('Custom positions'))
        t.setObjectName('pageTitle')
        pl.addWidget(t)
        hint = QLabel(tr('Pick a piece and click squares to place it (click again to remove). Drag pieces to move them. Right-click erases.'))
        hint.setWordWrap(True)
        hint.setObjectName('muted')
        pl.addWidget(hint)
        grid = QGridLayout()
        grid.setSpacing(4)
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        self.tool_buttons = {}
        for r, color in enumerate((chess.WHITE, chess.BLACK)):
            for c, t_ in enumerate(TYPES):
                b = QToolButton()
                b.setCheckable(True)
                b.setObjectName('pieceButton')
                b.setIconSize(QSize(38, 38))
                b.setFixedSize(52, 52)
                b.clicked.connect(lambda checked=False, key=(color, t_): self.set_tool(key))
                self.group.addButton(b)
                self.tool_buttons[(color, t_)] = b
                grid.addWidget(b, r, c)
        mv = QToolButton()
        mv.setCheckable(True)
        mv.setChecked(True)
        mv.setText(tr('Move'))
        mv.setObjectName('pieceButton')
        mv.setFixedSize(52, 52)
        mv.clicked.connect(lambda checked=False: self.set_tool('move'))
        er = QToolButton()
        er.setCheckable(True)
        er.setText(tr('Erase'))
        er.setObjectName('pieceButton')
        er.setFixedSize(52, 52)
        er.clicked.connect(lambda checked=False: self.set_tool('erase'))
        for b in (mv, er):
            self.group.addButton(b)
        self.tool_buttons['move'], self.tool_buttons['erase'] = mv, er
        grid.addWidget(mv, 2, 0)
        grid.addWidget(er, 2, 1)
        pl.addLayout(grid)
        row = QHBoxLayout()
        row.addWidget(QLabel(tr('Side to move')))
        self.side = QComboBox()
        self.side.addItem(tr('White'), True)
        self.side.addItem(tr('Black'), False)
        self.side.currentIndexChanged.connect(lambda i: self.update_status())
        row.addWidget(self.side, 1)
        pl.addLayout(row)
        self.castle = QCheckBox(tr('Allow castling (when king and rooks are on their home squares)'))
        self.castle.toggled.connect(lambda on: self.update_status())
        pl.addWidget(self.castle)
        row = QHBoxLayout()
        for text, fn in ((tr('Clear'), self.clear), (tr('Start position'), self.start), (tr('Flip'), self.flip)):
            b = QPushButton(text)
            b.clicked.connect(lambda checked=False, f=fn: f())
            row.addWidget(b)
        pl.addLayout(row)
        row = QHBoxLayout()
        self.preset = QComboBox()
        self.preset.addItem(tr('Presets…'), None)
        for name, fen in PRESETS:
            self.preset.addItem(tr(name), fen)
        self.preset.currentIndexChanged.connect(self.load_preset)
        row.addWidget(self.preset, 1)
        pl.addLayout(row)
        row = QHBoxLayout()
        self.fen_edit = QLineEdit()
        self.fen_edit.setPlaceholderText('FEN')
        row.addWidget(self.fen_edit, 1)
        b = QPushButton(tr('Load FEN'))
        b.clicked.connect(self.load_fen)
        c = QPushButton(tr('Copy'))
        c.clicked.connect(self.copy_fen)
        row.addWidget(b)
        row.addWidget(c)
        pl.addLayout(row)
        row = QHBoxLayout()
        self.saved = QComboBox()
        row.addWidget(self.saved, 1)
        for text, fn in ((tr('Load'), self.load_saved), (tr('Save'), self.save_current), (tr('Delete'), self.delete_saved)):
            b = QPushButton(text)
            b.clicked.connect(lambda checked=False, f=fn: f())
            row.addWidget(b)
        pl.addLayout(row)
        pl.addWidget(QLabel(tr('Play this position')))
        row = QHBoxLayout()
        self.opp = QComboBox()
        self.opp.addItem(tr('Pass & Play'), 'local')
        for bot in BOTS:
            self.opp.addItem('%s (%d)' % (bot.name, bot.elo), bot.id)
        self.me = QComboBox()
        self.me.addItem(tr('I play White'), 'white')
        self.me.addItem(tr('I play Black'), 'black')
        row.addWidget(self.opp, 1)
        row.addWidget(self.me)
        pl.addLayout(row)
        self.play_btn = QPushButton(tr('Play from this position'))
        self.play_btn.setObjectName('primary')
        self.play_btn.clicked.connect(self.play)
        pl.addWidget(self.play_btn)
        self.status = QLabel('')
        self.status.setWordWrap(True)
        pl.addWidget(self.status)
        pl.addStretch(1)
        root.addWidget(panel)
        self.start()

    # ------------------------------------------------------------- tools
    def set_tool(self, tool):
        self.tool = tool

    def refresh(self):
        pieces = self.app.pieces()
        for key, b in self.tool_buttons.items():
            if isinstance(key, tuple):
                b.setIcon(QIcon(pieces[key]))
        self.bw.light, self.bw.dark = self.app.light_color(), self.app.dark_color()
        self.bw.show_coords = self.app.store.prefs.get('show_coordinates', True)
        self.bw.clear_cache()
        self.saved.clear()
        for item in self.app.store.prefs.get('saved_positions', []):
            self.saved.addItem(item['name'], item['fen'])
        self.update_status()

    def press(self, sq):
        tool = self.tool
        if isinstance(tool, tuple):
            color, ptype = tool
            cur = self.board.piece_at(sq)
            if cur is not None and cur.color == color and cur.piece_type == ptype:
                self.board.remove_piece_at(sq)
            else:
                self.board.set_piece_at(sq, chess.Piece(ptype, color))
            self.update_status()
            return False
        if tool == 'erase':
            self.board.remove_piece_at(sq)
            self.update_status()
            return False
        return self.board.piece_at(sq) is not None

    def release(self, src, dst, dragged):
        if self.tool == 'move' and dragged and src is not None:
            piece = self.board.remove_piece_at(src)
            if piece is not None and dst is not None:
                self.board.set_piece_at(dst, piece)
            self.update_status()

    def erase(self, sq):
        self.board.remove_piece_at(sq)
        self.update_status()

    def clear(self):
        self.board = chess.Board.empty()
        self.update_status()

    def start(self):
        self.board = chess.Board()
        self.side.setCurrentIndex(0)
        self.castle.setChecked(True)
        self.update_status()

    def flip(self):
        self.bw.flipped = not self.bw.flipped
        self.bw.clear_cache()

    # --------------------------------------------------------------- FEN
    def build(self):
        b = self.board.copy()
        b.turn = bool(self.side.currentData())
        b.ep_square = None
        if self.castle.isChecked():
            b.castling_rights = chess.BB_A1 | chess.BB_H1 | chess.BB_A8 | chess.BB_H8
            b.castling_rights = b.clean_castling_rights()
        else:
            b.castling_rights = 0
        return b

    def problems(self, b):
        st = b.status()
        msgs = []
        pairs = ((chess.STATUS_NO_WHITE_KING, 'White needs a king.'), (chess.STATUS_NO_BLACK_KING, 'Black needs a king.'),
                 (chess.STATUS_TOO_MANY_KINGS, 'Each side can have only one king.'),
                 (chess.STATUS_PAWNS_ON_BACKRANK, 'Pawns cannot stand on the first or last rank.'),
                 (chess.STATUS_OPPOSITE_CHECK, 'The side that is NOT to move cannot be in check.'),
                 (chess.STATUS_TOO_MANY_WHITE_PAWNS, 'White has too many pawns.'), (chess.STATUS_TOO_MANY_BLACK_PAWNS, 'Black has too many pawns.'),
                 (chess.STATUS_TOO_MANY_WHITE_PIECES, 'White has too many pieces.'), (chess.STATUS_TOO_MANY_BLACK_PIECES, 'Black has too many pieces.'),
                 (chess.STATUS_TOO_MANY_CHECKERS, 'The king is attacked by too many pieces.'))
        for flag, text in pairs:
            if st & flag:
                msgs.append(tr(text))
        if not msgs and st:
            msgs.append(tr('This position is not legal.'))
        if not msgs and not any(b.legal_moves):
            msgs.append(tr('The side to move has no legal moves.'))
        return msgs

    def update_status(self):
        b = self.build()
        self.bw.board = self.board
        self.bw.set_position(self.board, None, None)
        self.fen_edit.setText(b.fen())
        msgs = self.problems(b)
        self.play_btn.setEnabled(not msgs)
        if msgs:
            self.status.setText('⚠ ' + ' '.join(msgs))
            self.status.setStyleSheet('color:#e58f2a;')
        else:
            self.status.setText('✔ ' + tr('Position is valid.'))
            self.status.setStyleSheet('color:%s;' % THEME['accent'])

    def set_fen(self, fen):
        try:
            b = chess.Board(fen)
        except ValueError:
            QMessageBox.warning(self, tr('Custom positions'), tr('That FEN could not be read.'))
            return
        self.board = chess.Board.empty()
        for sq, piece in b.piece_map().items():
            self.board.set_piece_at(sq, piece)
        self.side.setCurrentIndex(0 if b.turn == chess.WHITE else 1)
        self.castle.setChecked(bool(b.castling_rights))
        self.update_status()

    def load_fen(self):
        self.set_fen(self.fen_edit.text().strip())

    def copy_fen(self):
        QGuiApplication.clipboard().setText(self.fen_edit.text())

    def load_preset(self, idx):
        fen = self.preset.currentData()
        if fen:
            self.set_fen(fen)
        self.preset.blockSignals(True)
        self.preset.setCurrentIndex(0)
        self.preset.blockSignals(False)

    # ----------------------------------------------------------- saved list
    def save_current(self):
        name, ok = QInputDialog.getText(self, tr('Save position'), tr('Name:'))
        if ok and name.strip():
            lst = self.app.store.prefs.setdefault('saved_positions', [])
            lst.append({'name': name.strip()[:40], 'fen': self.build().fen()})
            self.app.store.save_prefs()
            self.refresh()
            self.saved.setCurrentIndex(self.saved.count() - 1)

    def load_saved(self):
        fen = self.saved.currentData()
        if fen:
            self.set_fen(fen)

    def delete_saved(self):
        i = self.saved.currentIndex()
        lst = self.app.store.prefs.get('saved_positions', [])
        if 0 <= i < len(lst):
            del lst[i]
            self.app.store.save_prefs()
            self.refresh()

    # ---------------------------------------------------------------- play
    def play(self):
        b = self.build()
        if self.problems(b):
            return
        self.app.start_custom_position(b.fen(), self.opp.currentData(), self.me.currentData())
