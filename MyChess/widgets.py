"""Reusable Qt widgets for My Chess."""
import math
import os
import time

import chess
from PySide6.QtCore import (Qt, QTimer, QPointF, QRectF, QSize, QEasingCurve, QUrl, Signal)
from PySide6.QtGui import (QPixmap, QFont, QIcon, QPainter, QColor, QPen, QBrush, QPainterPath,
                           QPainterPathStroker, QPolygonF, QRadialGradient, QLinearGradient)
from PySide6.QtWidgets import (QWidget, QLabel, QFrame, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton,
                               QToolButton, QDialog, QComboBox, QListWidget, QListWidgetItem, QSizePolicy,
                               QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QApplication)

from i18n import tr

try:
    from PySide6.QtMultimedia import QSoundEffect
except Exception:                      # multimedia not available: fall back to a system beep
    QSoundEffect = None

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, 'assets')

# ---- enum shortcuts (fully qualified names work on every PySide6 6.x)
AlignCenter = Qt.AlignmentFlag.AlignCenter
AlignLeft = Qt.AlignmentFlag.AlignLeft
AlignRight = Qt.AlignmentFlag.AlignRight
AlignTop = Qt.AlignmentFlag.AlignTop
AlignBottom = Qt.AlignmentFlag.AlignBottom
AlignVCenter = Qt.AlignmentFlag.AlignVCenter
NoPen = Qt.PenStyle.NoPen
NoBrush = Qt.BrushStyle.NoBrush
Smooth = Qt.TransformationMode.SmoothTransformation
KeepAspect = Qt.AspectRatioMode.KeepAspectRatio
KeepExpand = Qt.AspectRatioMode.KeepAspectRatioByExpanding
AA = QPainter.RenderHint.Antialiasing
SMOOTHPIX = QPainter.RenderHint.SmoothPixmapTransform

THEME = {'bg': '#302e2b', 'panel': '#262522', 'panel2': '#33312e', 'text': '#ffffff', 'muted': '#a3a19f',
         'accent': '#81b64c', 'accent_dark': '#5d8a36', 'border': '#3d3a37'}


def set_theme(values):
    THEME.update(values)


# ------------------------------------------------------------------ pixmaps
def round_pixmap(pix, size, radius=0.14):
    out = QPixmap(size, size)
    out.fill(Qt.GlobalColor.transparent)
    if pix is None or pix.isNull():
        return out
    p = QPainter(out)
    p.setRenderHint(AA)
    p.setRenderHint(SMOOTHPIX)
    path = QPainterPath()
    path.addRoundedRect(0, 0, size, size, size * radius, size * radius)
    p.setClipPath(path)
    scaled = pix.scaled(size, size, KeepExpand, Smooth)
    p.drawPixmap((size - scaled.width()) // 2, (size - scaled.height()) // 2, scaled)
    p.end()
    return out


def fallback_avatar(letter, size, color='#6b7a8a'):
    out = QPixmap(size, size)
    out.fill(Qt.GlobalColor.transparent)
    p = QPainter(out)
    p.setRenderHint(AA)
    p.setBrush(QColor(color))
    p.setPen(NoPen)
    p.drawRoundedRect(0, 0, size, size, size * 0.14, size * 0.14)
    p.setPen(QColor('#ffffff'))
    f = QFont()
    f.setBold(True)
    f.setPixelSize(int(size * 0.5))
    p.setFont(f)
    p.drawText(QRectF(0, 0, size, size), AlignCenter, (letter or '?')[:1].upper())
    p.end()
    return out


_ICON_CACHE = {}


def review_icon(label, size=24):
    """Move-rating picture (brilliant, great, best, ...) from assets/review_icons, or None."""
    key = (label, size)
    if key not in _ICON_CACHE:
        pm = QPixmap(os.path.join(ASSETS, 'review_icons', label + '.png'))
        _ICON_CACHE[key] = pm.scaled(size, size, KeepAspect, Smooth) if not pm.isNull() else None
    return _ICON_CACHE[key]


PIECE_LETTER = {chess.PAWN: 'P', chess.KNIGHT: 'N', chess.BISHOP: 'B', chess.ROOK: 'R', chess.QUEEN: 'Q', chess.KING: 'K'}
CLASSIC_FILES = {
    (chess.WHITE, chess.PAWN): 'pieces/white_pieces/White_Pawn.png.png',
    (chess.WHITE, chess.KNIGHT): 'pieces/white_pieces/White_Knight.png.png',
    (chess.WHITE, chess.BISHOP): 'pieces/white_pieces/White_Bishop.png.png',
    (chess.WHITE, chess.ROOK): 'pieces/white_pieces/White_Rook.png.png',
    (chess.WHITE, chess.QUEEN): 'pieces/white_pieces/White_Queen.png.png',
    (chess.WHITE, chess.KING): 'pieces/white_pieces/White_King.png.png',
    (chess.BLACK, chess.PAWN): 'pieces/Black_pieces/Black_Pawn.png.png',
    (chess.BLACK, chess.KNIGHT): 'pieces/Black_pieces/Black_Knight.png.png',
    (chess.BLACK, chess.BISHOP): 'pieces/Black_pieces/Black_Bishop.png.png',
    (chess.BLACK, chess.ROOK): 'pieces/Black_pieces/Black_Rook.png.png',
    (chess.BLACK, chess.QUEEN): 'pieces/Black_pieces/Black_Queen.png.png',
    (chess.BLACK, chess.KING): 'pieces/Black_pieces/Black_King.png.png'}


class PieceSets:
    """Piece artwork: 'Classic' (your original PNGs) + every folder in assets/piece_sets.
    A custom set is a folder with wP.png wN.png wB.png wR.png wQ.png wK.png and bP.png ... bK.png."""

    def __init__(self):
        self.cache = {}

    def names(self):
        names = ['Classic']
        folder = os.path.join(ASSETS, 'piece_sets')
        if os.path.isdir(folder):
            names += sorted(n for n in os.listdir(folder) if os.path.isdir(os.path.join(folder, n)))
        return names

    def load(self, name):
        if name in self.cache:
            return self.cache[name]
        pieces = {}
        for key in CLASSIC_FILES:
            if name == 'Classic':
                path = os.path.join(ASSETS, CLASSIC_FILES[key])
            else:
                path = os.path.join(ASSETS, 'piece_sets', name, ('w' if key[0] else 'b') + PIECE_LETTER[key[1]] + '.png')
            pix = QPixmap(path)
            if pix.isNull() and name != 'Classic':
                return self.load('Classic')
            pieces[key] = pix
        self.cache[name] = pieces
        return pieces


def captured_pixmap(pieces, captured, advantage, height=22):
    """Row of small captured-piece icons (overlapping) followed by '+N'."""
    if not captured and advantage <= 0:
        return None
    step = max(6, int(height * 0.5))
    width = height + max(0, len(captured) - 1) * step + (34 if advantage > 0 else 0)
    out = QPixmap(max(width, 1), height)
    out.fill(Qt.GlobalColor.transparent)
    p = QPainter(out)
    p.setRenderHint(AA)
    p.setRenderHint(SMOOTHPIX)
    x = 0
    for key in captured:
        pm = pieces[key].scaled(height, height, KeepAspect, Smooth)
        p.drawPixmap(x, 0, pm)
        x += step
    if advantage > 0:
        p.setPen(QColor(THEME['muted']))
        f = QFont()
        f.setBold(True)
        f.setPixelSize(int(height * 0.6))
        p.setFont(f)
        p.drawText(QRectF(x + height * 0.55, 0, 40, height), AlignLeft | AlignVCenter, '+%d' % advantage)
    p.end()
    return out


# ------------------------------------------------------------------- sounds
class SoundManager:
    """Plays move sounds. A "sound pack" is a folder with move.wav, capture.wav, castle.wav, check.wav,
    promote.wav, start.wav, end.wav, notify.wav, lowtime.wav - the default pack is assets/sounds itself,
    every sub-folder of assets/sounds is another pack (drop your own WAV files in there)."""
    NAMES = ['move', 'move_opponent', 'premove', 'capture', 'castle', 'check', 'promote', 'start', 'end', 'notify', 'lowtime']
    FALLBACK = {'move_opponent': 'move', 'premove': 'move'}

    def __init__(self, pack='Default'):
        self.enabled = True
        self.volume = 0.7
        self.effects = {}
        self.pack = None
        self.load_pack(pack)

    @staticmethod
    def packs():
        names = ['Default']
        folder = os.path.join(ASSETS, 'sounds')
        if os.path.isdir(folder):
            names += sorted(n for n in os.listdir(folder) if os.path.isdir(os.path.join(folder, n)))
        return names

    def load_pack(self, pack):
        if pack == self.pack or QSoundEffect is None:
            self.pack = pack
            return
        self.pack = pack
        self.effects = {}
        base = os.path.join(ASSETS, 'sounds')
        folder = base if pack in ('', 'Default') else os.path.join(base, pack)
        for n in self.NAMES:
            candidates = [os.path.join(folder, n + '.wav')]
            if n in self.FALLBACK:
                candidates.append(os.path.join(folder, self.FALLBACK[n] + '.wav'))
            candidates += [os.path.join(base, n + '.wav'), os.path.join(base, self.FALLBACK.get(n, n) + '.wav')]
            path = next((c for c in candidates if os.path.exists(c)), None)     # missing in the pack: default sound
            if path:
                try:
                    e = QSoundEffect()
                    e.setSource(QUrl.fromLocalFile(path))
                    e.setVolume(self.volume)
                    self.effects[n] = e
                except Exception:
                    pass

    def set_volume(self, percent):
        self.volume = max(0.0, min(1.0, percent / 100.0))
        for e in self.effects.values():
            e.setVolume(self.volume)

    def play(self, name):
        if not self.enabled:
            return
        e = self.effects.get(name)
        if e is not None:
            e.play()
        elif not self.effects:
            QApplication.beep()


# ------------------------------------------------------------------- avatar
class AvatarLabel(QLabel):
    def __init__(self, size=44, parent=None):
        super().__init__(parent)
        self.px = size
        self.setFixedSize(size, size)
        self.setScaledContents(False)

    def set_avatar(self, pix, letter='?'):
        if pix is None or pix.isNull():
            self.setPixmap(fallback_avatar(letter, self.px))
        else:
            self.setPixmap(round_pixmap(pix, self.px))


class PlayerStrip(QWidget):
    """Avatar + name + rating + captured pieces on the left, clock on the right (like chess.com)."""

    def __init__(self, avatar_px=46):
        super().__init__()
        row = QHBoxLayout(self)
        row.setContentsMargins(2, 2, 2, 2)
        row.setSpacing(10)
        self.avatar = AvatarLabel(avatar_px)
        row.addWidget(self.avatar)
        col = QVBoxLayout()
        col.setSpacing(1)
        top = QHBoxLayout()
        top.setSpacing(8)
        self.name = QLabel('Player')
        self.name.setObjectName('stripName')
        self.rating = QLabel('')
        self.rating.setObjectName('stripRating')
        top.addWidget(self.name)
        top.addWidget(self.rating)
        top.addStretch(1)
        col.addLayout(top)
        self.captured = QLabel('')
        self.captured.setMinimumHeight(22)
        col.addWidget(self.captured)
        row.addLayout(col, 1)
        self.clock = QLabel('10:00')
        self.clock.setAlignment(AlignCenter)
        self.clock.setMinimumWidth(110)
        self.set_clock('10:00', False, False)
        row.addWidget(self.clock)

    def set_player(self, name, rating, pix):
        self.name.setText(name)
        self.rating.setText('(%s)' % rating if rating is not None else '')
        self.avatar.set_avatar(pix, name[:1])

    def set_captured(self, pix):
        if pix is None:
            self.captured.clear()
        else:
            self.captured.setPixmap(pix)

    def set_clock(self, text, active, low):
        key = (text, active, low, THEME['panel'])
        if key == getattr(self, '_clock_key', None):
            return                                  # re-parsing the stylesheet 10x a second is wasteful
        self._clock_key = key
        if active:
            bg, fg = ('#ffffff', '#262522') if not low else ('#ca3431', '#ffffff')
        else:
            bg, fg = (THEME['panel'], THEME['muted'])
        self.clock.setText(text)
        self.clock.setStyleSheet('font-size:24px;font-weight:bold;padding:6px 14px;border-radius:6px;'
                                 'background:%s;color:%s;' % (bg, fg))


# -------------------------------------------------------------------- board
ARROW_COLORS = {'green': QColor(129, 182, 76, 215), 'red': QColor(205, 45, 45, 205),
                'yellow': QColor(235, 180, 20, 220), 'blue': QColor(45, 105, 205, 215),
                'best': QColor(129, 182, 76, 235)}
PROMO_ORDER = [chess.QUEEN, chess.KNIGHT, chess.ROOK, chess.BISHOP]


def arrow_color_for(modifiers):
    if modifiers & Qt.KeyboardModifier.ShiftModifier:
        return 'red'
    if modifiers & Qt.KeyboardModifier.ControlModifier:
        return 'yellow'
    if modifiers & Qt.KeyboardModifier.AltModifier:
        return 'blue'
    return 'green'


class BoardWidget(QWidget):
    """Painted chess board: animations, drag & drop, arrows, premove, chess.com style promotion
    picker and review badges.  The owner (controller) supplies the game state and callbacks:
        on_left_press(sq) -> bool (drag allowed)     on_left_release(src, dst, dragged)
        on_right_release(start, end, colour, global_pos)    on_promotion(src, dst, piece_type_or_None)
    """

    def __init__(self, pieces_fn):
        super().__init__()
        self.pieces_fn = pieces_fn
        self.controller = None
        self.interactive = True
        self.setMinimumSize(360, 360)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMouseTracking(True)
        # state set by the owner
        self.board = chess.Board()
        self.last_move = None
        self.selected = None
        self.markers = {}
        self.markers_premove = False
        self.premove = None
        self.check_sq = None
        self.no_capture = set()
        self.flipped = False
        self.light = QColor('#EEEED2')
        self.dark = QColor('#769656')
        self.show_coords = True
        self.animations = True
        self.hint_arrows = []
        self.badge = None            # (square, colour, symbol[, QPixmap])
        self.style_badges = {}       # square -> short text for pieces with house-rule movement
        self.promo = None
        self.promo_hover = -1
        # user marks
        self.arrows = {}
        self.highlights = set()
        # mouse state
        self.left_down = False
        self.press_sq = None
        self.press_pos = QPointF()
        self.drag_possible = False
        self.dragging = False
        self.drag_sq = None
        self.drag_piece = None
        self.drag_pos = QPointF()
        self.hover_sq = None
        self.right_start = None
        self.right_cur = None
        self.right_color = 'green'
        # animation
        self.anim_items = []
        self.anim_ghosts = []
        self.anim_hidden = set()
        self.anim_start = 0.0
        self.anim_ms = 200
        self.curve = QEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._anim_step)
        # caches
        self.pix_cache = {}
        self._bg = None
        self._bg_key = None

    # ---------------------------------------------------------------- geometry
    def sq_size(self):
        return max(8, min(self.width(), self.height()) // 8)

    def origin(self):
        s = self.sq_size()
        return (self.width() - 8 * s) // 2, (self.height() - 8 * s) // 2

    def sq_rect(self, sq):
        s = self.sq_size()
        ox, oy = self.origin()
        f, r = chess.square_file(sq), chess.square_rank(sq)
        col, row = (7 - f, r) if self.flipped else (f, 7 - r)
        return QRectF(ox + col * s, oy + row * s, s, s)

    def sq_center(self, sq):
        return self.sq_rect(sq).center()

    def sq_at(self, pos):
        s = self.sq_size()
        ox, oy = self.origin()
        col = int((pos.x() - ox) // s)
        row = int((pos.y() - oy) // s)
        if not (0 <= col < 8 and 0 <= row < 8):
            return None
        return chess.square(7 - col, row) if self.flipped else chess.square(col, 7 - row)

    def piece_pixmap(self, key, size):
        k = (key, size)
        pm = self.pix_cache.get(k)
        if pm is None:
            dpr = self.devicePixelRatioF()
            pm = self.pieces_fn()[key].scaled(int(size * dpr), int(size * dpr), KeepAspect, Smooth)
            pm.setDevicePixelRatio(dpr)
            self.pix_cache[k] = pm
        return pm

    def clear_cache(self):
        self.pix_cache.clear()
        self._bg_key = None
        self.update()

    # --------------------------------------------------------------- owner API
    def set_position(self, board, last_move=None, check_sq=None):
        self.board = board
        self.last_move = last_move
        self.check_sq = check_sq
        if self.dragging and (self.drag_sq is None or board.piece_at(self.drag_sq) != self.drag_piece):
            self.cancel_drag()
        self.update()

    def cancel_drag(self):
        self.dragging = False
        self.left_down = False
        self.drag_possible = False
        self.drag_sq = None
        self.drag_piece = None
        self.update()

    def begin_promotion(self, src, dst, color):
        self.promo = {'src': src, 'dst': dst, 'color': color}
        self.promo_hover = -1
        self.update()

    def clear_marks(self):
        if self.arrows or self.highlights:
            self.arrows.clear()
            self.highlights.clear()
            self.update()

    def toggle_arrow(self, a, b, color):
        if a == b:
            return
        if (a, b) in self.arrows:
            del self.arrows[(a, b)]
        else:
            self.arrows[(a, b)] = color
        self.update()

    def toggle_highlight(self, sq):
        if sq in self.highlights:
            self.highlights.discard(sq)
        else:
            self.highlights.add(sq)
        self.update()

    # --------------------------------------------------------------- animation
    def start_animation(self, items, ghosts):
        """items: [(piece_key, from_sq, to_sq)]   ghosts: [(piece_key, sq)] (captured pieces)."""
        if not items or not self.animations:
            self.stop_animation()
            return
        longest = max(max(abs(chess.square_file(a) - chess.square_file(b)),
                          abs(chess.square_rank(a) - chess.square_rank(b))) for _, a, b in items)
        self.anim_ms = 120 + 20 * longest
        self.anim_items = list(items)
        self.anim_ghosts = list(ghosts)
        self.anim_hidden = {b for _, _, b in items}
        self.anim_start = time.monotonic()
        self.anim_timer.start(16)
        self.update()

    def stop_animation(self):
        self.anim_timer.stop()
        self.anim_items = []
        self.anim_ghosts = []
        self.anim_hidden = set()
        self.update()

    def _anim_step(self):
        if time.monotonic() - self.anim_start >= self.anim_ms / 1000.0:
            self.stop_animation()
        else:
            self.update()

    # ---------------------------------------------------------------- painting
    def _background(self):
        dpr = self.devicePixelRatioF()
        key = (self.width(), self.height(), self.flipped, self.light.rgb(), self.dark.rgb(), self.show_coords, dpr)
        if key == self._bg_key and self._bg is not None:
            return self._bg
        pm = QPixmap(int(self.width() * dpr), int(self.height() * dpr))
        pm.setDevicePixelRatio(dpr)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        p.setRenderHint(AA)
        s = self.sq_size()
        for sq in range(64):
            rect = self.sq_rect(sq)
            light = (chess.square_file(sq) + chess.square_rank(sq)) % 2 == 1
            p.fillRect(rect, self.light if light else self.dark)
        if self.show_coords:
            font = QFont()
            font.setBold(True)
            font.setPixelSize(max(9, int(s * 0.16)))
            p.setFont(font)
            for i in range(8):
                file_idx = 7 - i if self.flipped else i
                rank_idx = i if self.flipped else 7 - i
                bottom_sq = chess.square(file_idx, 7 if self.flipped else 0)
                left_sq = chess.square(7 if self.flipped else 0, rank_idx)
                rb, rl = self.sq_rect(bottom_sq), self.sq_rect(left_sq)
                lb = (chess.square_file(bottom_sq) + chess.square_rank(bottom_sq)) % 2 == 1
                ll = (chess.square_file(left_sq) + chess.square_rank(left_sq)) % 2 == 1
                p.setPen(self.dark if lb else self.light)
                p.drawText(QRectF(rb.x(), rb.y(), rb.width() - 4, rb.height() - 2), AlignRight | AlignBottom, 'abcdefgh'[file_idx])
                p.setPen(self.dark if ll else self.light)
                p.drawText(QRectF(rl.x() + 3, rl.y() + 2, rl.width(), rl.height()), AlignLeft | AlignTop, str(rank_idx + 1))
        p.end()
        self._bg, self._bg_key = pm, key
        return pm

    def paintEvent(self, event):
        b = self.board
        p = QPainter(self)
        p.setRenderHint(AA)
        p.setRenderHint(SMOOTHPIX)
        s = self.sq_size()
        p.drawPixmap(0, 0, self._background())
        last = self.last_move
        # highlights
        for sq in range(64):
            color = None
            if last is not None and sq in (last.from_square, last.to_square):
                color = QColor(246, 246, 105, 125)
            if sq == self.selected:
                color = QColor(246, 246, 105, 175)
            if self.premove and sq in self.premove:
                color = QColor(215, 45, 45, 130)
            if sq in self.highlights:
                color = QColor(235, 97, 80, 175)
            if color is not None:
                p.fillRect(self.sq_rect(sq), color)
            if self.check_sq == sq:
                rect = self.sq_rect(sq)
                grad = QRadialGradient(rect.center(), s * 0.62)
                grad.setColorAt(0.0, QColor(255, 0, 0, 215))
                grad.setColorAt(0.55, QColor(231, 0, 0, 110))
                grad.setColorAt(1.0, QColor(231, 0, 0, 0))
                p.fillRect(rect, QBrush(grad))
        # move dots / capture rings
        for sq, kind in self.markers.items():
            rect = self.sq_rect(sq)
            base = QColor(190, 40, 40) if self.markers_premove else QColor(20, 85, 30)
            if kind == 'dot':
                base.setAlpha(150)
                p.setPen(NoPen)
                p.setBrush(base)
                p.drawEllipse(rect.center(), s * 0.11, s * 0.11)
            else:
                base.setAlpha(165)
                p.setPen(QPen(base, max(4, s * 0.075)))
                p.setBrush(NoBrush)
                p.drawEllipse(rect.center(), s * 0.43, s * 0.43)
        # standing pieces
        hidden = set(self.anim_hidden)
        if self.dragging and self.drag_sq is not None:
            hidden.add(self.drag_sq)
        psize = int(s * 0.94)
        off = (s - psize) / 2
        for sq, piece in b.piece_map().items():
            if sq in hidden:
                continue
            rect = self.sq_rect(sq)
            p.drawPixmap(int(rect.x() + off), int(rect.y() + off), self.piece_pixmap((piece.color, piece.piece_type), psize))
            if sq in self.no_capture:
                p.setPen(QPen(QColor(255, 255, 255), 1.5))
                p.setBrush(QColor(40, 110, 220))
                p.drawEllipse(QPointF(rect.right() - s * 0.16, rect.top() + s * 0.16), s * 0.09, s * 0.09)
        # animation
        if self.anim_items:
            t = min(1.0, (time.monotonic() - self.anim_start) / (self.anim_ms / 1000.0))
            k = self.curve.valueForProgress(t)
            if t < 0.8:
                for key, sq in self.anim_ghosts:
                    rect = self.sq_rect(sq)
                    p.drawPixmap(int(rect.x() + off), int(rect.y() + off), self.piece_pixmap(key, psize))
            for key, a, z in self.anim_items:
                ra, rz = self.sq_rect(a), self.sq_rect(z)
                x = ra.x() + (rz.x() - ra.x()) * k
                y = ra.y() + (rz.y() - ra.y()) * k
                p.drawPixmap(int(x + off), int(y + off), self.piece_pixmap(key, psize))
        # review badge (picture if available, otherwise a coloured circle with a symbol)
        if self.badge is not None:
            sq, color, symbol = self.badge[0], self.badge[1], self.badge[2]
            pix = self.badge[3] if len(self.badge) > 3 else None
            rect = self.sq_rect(sq)
            if pix is not None:
                d = int(s * 0.36)
                scaled = pix.scaled(d, d, KeepAspect, Smooth)
                p.drawPixmap(int(rect.right() - d * 0.62), int(rect.top() - d * 0.38), scaled)
            else:
                c = QPointF(rect.right() - s * 0.14, rect.top() + s * 0.14)
                p.setPen(QPen(QColor(255, 255, 255, 230), max(1.5, s * 0.02)))
                p.setBrush(QColor(color))
                p.drawEllipse(c, s * 0.15, s * 0.15)
                f = QFont()
                f.setBold(True)
                f.setPixelSize(max(8, int(s * 0.17)))
                p.setFont(f)
                p.setPen(QColor('#ffffff'))
                p.drawText(QRectF(c.x() - s * 0.15, c.y() - s * 0.15, s * 0.3, s * 0.3), AlignCenter, symbol)
        # small letters on pieces that use house-rule movement (A = Amazon, Q = queen-like, ...)
        if self.style_badges:
            f = QFont()
            f.setBold(True)
            f.setPixelSize(max(8, int(s * 0.15)))
            p.setFont(f)
            for sq, text in self.style_badges.items():
                if sq in hidden:
                    continue
                rect = self.sq_rect(sq)
                bw = max(s * 0.26, len(text) * s * 0.13)
                box = QRectF(rect.left() + 2, rect.bottom() - s * 0.24, bw, s * 0.22)
                p.setPen(NoPen)
                p.setBrush(QColor(140, 60, 200, 225))
                p.drawRoundedRect(box, 4, 4)
                p.setPen(QColor('#ffffff'))
                p.drawText(box, AlignCenter, text)
        # arrows
        for (a, z), cname in self.arrows.items():
            self.draw_arrow(p, a, z, ARROW_COLORS[cname])
        for a, z, cname in self.hint_arrows:
            self.draw_arrow(p, a, z, ARROW_COLORS[cname])
        if self.right_start is not None and self.right_cur is not None and self.right_cur != self.right_start:
            self.draw_arrow(p, self.right_start, self.right_cur, ARROW_COLORS[self.right_color])
        # promotion picker
        if self.promo is not None:
            self._paint_promotion(p, s)
        # dragged piece
        if self.dragging and self.drag_sq is not None:
            piece = b.piece_at(self.drag_sq)
            if piece:
                if self.hover_sq is not None:
                    hr = self.sq_rect(self.hover_sq)
                    p.setPen(QPen(QColor(255, 255, 255, 200), 3))
                    p.setBrush(NoBrush)
                    p.drawRect(hr.adjusted(1.5, 1.5, -1.5, -1.5))
                big = int(s * 1.08)
                p.drawPixmap(int(self.drag_pos.x() - big / 2), int(self.drag_pos.y() - big / 2),
                             self.piece_pixmap((piece.color, piece.piece_type), big))
        p.end()

    def promo_rects(self):
        s = self.sq_size()
        r0 = self.sq_rect(self.promo['dst'])
        ox, oy = self.origin()
        down = r0.top() < oy + 3.5 * s
        return [QRectF(r0.x(), r0.y() + (i * s if down else -i * s), s, s) for i in range(5)]

    def _paint_promotion(self, p, s):
        ox, oy = self.origin()
        p.fillRect(QRectF(ox, oy, 8 * s, 8 * s), QColor(0, 0, 0, 110))
        rects = self.promo_rects()
        color = self.promo['color']
        union = rects[0].united(rects[3])
        p.setPen(NoPen)
        p.setBrush(QColor(0, 0, 0, 70))
        p.drawRoundedRect(union.translated(3, 4), 6, 6)
        p.setBrush(QColor('#f6f6f6'))
        p.drawRoundedRect(union, 6, 6)
        for i, ptype in enumerate(PROMO_ORDER):
            r = rects[i]
            if i == self.promo_hover:
                p.setBrush(QColor('#cfe8b0'))
                p.drawRoundedRect(r.adjusted(2, 2, -2, -2), 6, 6)
            size = int(s * 0.88)
            p.drawPixmap(int(r.x() + (s - size) / 2), int(r.y() + (s - size) / 2), self.piece_pixmap((color, ptype), size))
        cr = rects[4]
        p.setBrush(QColor('#e9e9e9') if self.promo_hover != 4 else QColor('#d6d6d6'))
        p.drawRoundedRect(cr.adjusted(s * 0.22, s * 0.22, -s * 0.22, -s * 0.22), 6, 6)
        p.setPen(QPen(QColor('#555555'), max(2, s * 0.045)))
        c = cr.center()
        d = s * 0.14
        p.drawLine(QPointF(c.x() - d, c.y() - d), QPointF(c.x() + d, c.y() + d))
        p.drawLine(QPointF(c.x() - d, c.y() + d), QPointF(c.x() + d, c.y() - d))

    def draw_arrow(self, p, a, z, color):
        s = self.sq_size()
        c1, c2 = self.sq_center(a), self.sq_center(z)
        df = abs(chess.square_file(a) - chess.square_file(z))
        dr = abs(chess.square_rank(a) - chess.square_rank(z))
        if sorted((df, dr)) == [1, 2]:                       # knight arrows bend like an L
            corner = QPointF(c1.x(), c2.y()) if abs(c2.y() - c1.y()) > abs(c2.x() - c1.x()) else QPointF(c2.x(), c1.y())
            pts = [c1, corner, c2]
        else:
            pts = [c1, c2]
        la, lb = pts[-2], pts[-1]
        dx, dy = lb.x() - la.x(), lb.y() - la.y()
        length = math.hypot(dx, dy)
        if length < 1:
            return
        ux, uy = dx / length, dy / length
        tip = QPointF(lb.x() - ux * s * 0.10, lb.y() - uy * s * 0.10)
        head_len, head_half = s * 0.36, s * 0.21
        base = QPointF(tip.x() - ux * head_len, tip.y() - uy * head_len)
        px, py = -uy, ux
        shaft = QPainterPath()
        shaft.moveTo(pts[0])
        for q in pts[1:-1]:
            shaft.lineTo(q)
        shaft.lineTo(base)
        stroker = QPainterPathStroker()
        stroker.setWidth(s * 0.17)
        stroker.setCapStyle(Qt.PenCapStyle.FlatCap)
        stroker.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        shape = stroker.createStroke(shaft)
        head = QPainterPath()
        head.addPolygon(QPolygonF([tip, QPointF(base.x() + px * head_half, base.y() + py * head_half),
                                   QPointF(base.x() - px * head_half, base.y() - py * head_half)]))
        head.closeSubpath()
        p.setPen(NoPen)
        p.setBrush(color)
        p.drawPath(shape.united(head))

    # ------------------------------------------------------------------- mouse
    def _promo_index(self, pos):
        for i, r in enumerate(self.promo_rects()):
            if r.contains(pos):
                return i
        return -1

    def mousePressEvent(self, e):
        if self.promo is not None:
            if e.button() == Qt.MouseButton.LeftButton:
                idx = self._promo_index(e.position())
                promo, self.promo = self.promo, None
                self.update()
                if self.controller:
                    self.controller.on_promotion(promo['src'], promo['dst'], PROMO_ORDER[idx] if 0 <= idx < 4 else None)
            return
        sq = self.sq_at(e.position())
        if sq is None:
            return
        if e.button() == Qt.MouseButton.LeftButton:
            self.left_down = True
            self.press_sq = sq
            self.press_pos = e.position()
            self.dragging = False
            self.drag_sq = None
            self.drag_piece = None
            self.drag_possible = bool(self.interactive and self.controller and self.controller.on_left_press(sq))
            if not self.interactive and self.controller is None:
                self.clear_marks()
        elif e.button() == Qt.MouseButton.RightButton:
            self.right_start = sq
            self.right_cur = sq
            self.right_color = arrow_color_for(e.modifiers())
            self.update()

    def mouseMoveEvent(self, e):
        pos = e.position()
        self.hover_sq = self.sq_at(pos)
        if self.promo is not None:
            idx = self._promo_index(pos)
            if idx != self.promo_hover:
                self.promo_hover = idx
                self.update()
            return
        if self.left_down and self.drag_possible:
            if not self.dragging and math.hypot(pos.x() - self.press_pos.x(), pos.y() - self.press_pos.y()) > 6:
                self.dragging = True
                self.drag_sq = self.press_sq
                self.drag_piece = self.board.piece_at(self.press_sq)
            if self.dragging:
                self.drag_pos = pos
                self.update()
        if self.right_start is not None:
            self.right_color = arrow_color_for(e.modifiers())
            new = self.sq_at(pos)
            if new != self.right_cur:
                self.right_cur = new
                self.update()

    def mouseReleaseEvent(self, e):
        pos = e.position()
        if e.button() == Qt.MouseButton.LeftButton and self.left_down:
            dst = self.sq_at(pos)
            dragged, src = self.dragging, self.press_sq
            self.left_down = False
            self.dragging = False
            self.drag_sq = None
            self.drag_piece = None
            was_possible, self.drag_possible = self.drag_possible, False
            self.update()
            if self.controller and (was_possible or self.interactive):
                self.controller.on_left_release(src, dst, dragged)
        elif e.button() == Qt.MouseButton.RightButton and self.right_start is not None:
            start, end, color = self.right_start, self.sq_at(pos), self.right_color
            self.right_start = None
            self.right_cur = None
            self.update()
            if end is None:
                return
            if self.controller is not None and self.interactive:
                self.controller.on_right_release(start, end, color, self.mapToGlobal(pos.toPoint()))
            elif start != end:
                self.toggle_arrow(start, end, color)
            else:
                self.toggle_highlight(start)

    def leaveEvent(self, e):
        self.hover_sq = None
        super().leaveEvent(e)

    def resizeEvent(self, e):
        self.pix_cache.clear()
        self._bg_key = None
        super().resizeEvent(e)


# --------------------------------------------------------------- eval widgets
class EvalBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(30)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.wp = 50.0
        self.text = '0.0'
        self.flipped = False

    def set_value(self, wp, text, flipped=False):
        self.wp, self.text, self.flipped = wp, text, flipped
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(AA)
        w, h = self.width(), self.height()
        p.setPen(NoPen)
        p.setBrush(QColor('#403d39'))
        p.drawRoundedRect(0, 0, w, h, 4, 4)
        white_h = h * self.wp / 100.0
        p.setBrush(QColor('#f2f2f2'))
        if self.flipped:
            p.drawRoundedRect(QRectF(0, 0, w, white_h), 4, 4)
        else:
            p.drawRoundedRect(QRectF(0, h - white_h, w, white_h), 4, 4)
        f = QFont()
        f.setBold(True)
        f.setPixelSize(11)
        p.setFont(f)
        white_side_bottom = not self.flipped
        on_white = (self.wp >= 50) == white_side_bottom
        p.setPen(QColor('#262522') if self.wp >= 50 else QColor('#f2f2f2'))
        rect = QRectF(0, h - 20 if (self.wp >= 50) == white_side_bottom else 2, w, 18)
        p.drawText(rect, AlignCenter, self.text)


class EvalGraph(QWidget):
    ply_clicked = Signal(int)

    def __init__(self):
        super().__init__()
        self.setMinimumHeight(90)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.values = []        # white win % per position (index 0 = start)
        self.current = 0

    def set_data(self, values):
        self.values = list(values)
        self.update()

    def set_current(self, ply):
        self.current = ply
        self.update()

    def _x(self, i):
        n = max(1, len(self.values) - 1)
        return 4 + (self.width() - 8) * i / n

    def mousePressEvent(self, e):
        if len(self.values) > 1:
            n = len(self.values) - 1
            ply = int(round((e.position().x() - 4) / max(1, self.width() - 8) * n))
            self.ply_clicked.emit(max(0, min(n, ply)))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(AA)
        w, h = self.width(), self.height()
        p.setPen(NoPen)
        p.setBrush(QColor('#403d39'))
        p.drawRoundedRect(0, 0, w, h, 6, 6)
        if len(self.values) < 2:
            return
        path = QPainterPath()
        path.moveTo(self._x(0), h)
        for i, v in enumerate(self.values):
            path.lineTo(self._x(i), h * (1 - v / 100.0))
        path.lineTo(self._x(len(self.values) - 1), h)
        path.closeSubpath()
        p.setBrush(QColor(240, 240, 240, 235))
        p.drawPath(path)
        p.setPen(QPen(QColor(150, 150, 150, 160), 1))
        p.drawLine(0, h // 2, w, h // 2)
        p.setPen(QPen(QColor('#81b64c'), 2))
        x = self._x(self.current)
        p.drawLine(QPointF(x, 0), QPointF(x, h))


class CoachBubble(QFrame):
    """Coach picture + speech bubble."""

    def __init__(self, avatar_px=52):
        super().__init__()
        self.setObjectName('panel')
        row = QHBoxLayout(self)
        row.setContentsMargins(10, 8, 10, 8)
        row.setSpacing(10)
        self.avatar = AvatarLabel(avatar_px)
        row.addWidget(self.avatar, alignment=AlignTop)
        col = QVBoxLayout()
        col.setSpacing(2)
        self.name = QLabel('')
        self.name.setStyleSheet('font-weight:bold;font-size:13px;color:%s;' % THEME['accent'])
        self.text = QLabel('')
        self.text.setWordWrap(True)
        self.text.setStyleSheet('font-size:14px;')
        col.addWidget(self.name)
        col.addWidget(self.text, 1)
        row.addLayout(col, 1)

    def set_coach(self, name, pix):
        self.name.setText(name)
        self.avatar.set_avatar(pix, name[:1])

    def say(self, text, color=None):
        self.text.setText(text)
        self.setStyleSheet('QFrame#panel{border-left:5px solid %s;}' % color if color else '')


class RatingGraph(QWidget):
    """Line chart of the player's Elo over time."""

    def __init__(self):
        super().__init__()
        self.setMinimumHeight(170)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.points = []

    def set_points(self, points):
        self.points = list(points)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(AA)
        w, h = self.width(), self.height()
        p.setPen(NoPen)
        p.setBrush(QColor(THEME['panel']))
        p.drawRoundedRect(0, 0, w, h, 8, 8)
        if len(self.points) < 2:
            p.setPen(QColor(THEME['muted']))
            p.drawText(QRectF(0, 0, w, h), AlignCenter, tr('Play a few rated games to see your progress.'))
            return
        lo, hi = min(self.points), max(self.points)
        if hi - lo < 40:
            hi, lo = hi + 20, lo - 20
        pad_l, pad_r, pad_t, pad_b = 46, 16, 14, 18
        def pt(i, v):
            x = pad_l + (w - pad_l - pad_r) * i / (len(self.points) - 1)
            y = pad_t + (h - pad_t - pad_b) * (1 - (v - lo) / float(hi - lo))
            return QPointF(x, y)
        p.setPen(QPen(QColor(THEME['border']), 1))
        f = QFont()
        f.setPixelSize(11)
        p.setFont(f)
        for frac in (0.0, 0.5, 1.0):
            val = lo + (hi - lo) * frac
            y = pad_t + (h - pad_t - pad_b) * (1 - frac)
            p.drawLine(QPointF(pad_l, y), QPointF(w - pad_r, y))
            p.setPen(QColor(THEME['muted']))
            p.drawText(QRectF(2, y - 8, pad_l - 8, 16), AlignRight | AlignVCenter, str(int(val)))
            p.setPen(QPen(QColor(THEME['border']), 1))
        path = QPainterPath()
        path.moveTo(pt(0, self.points[0]))
        for i, v in enumerate(self.points):
            path.lineTo(pt(i, v))
        p.setBrush(NoBrush)
        p.setPen(QPen(QColor(THEME['accent']), 3))
        p.drawPath(path)
        last = pt(len(self.points) - 1, self.points[-1])
        p.setPen(NoPen)
        p.setBrush(QColor(THEME['accent']))
        p.drawEllipse(last, 5, 5)


# --------------------------------------------------------------- move table
class MoveTable(QTableWidget):
    ply_selected = Signal(int)

    def __init__(self):
        super().__init__(0, 3)
        self.setHorizontalHeaderLabels(['#', tr('White'), tr('Black')])
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(28)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.setColumnWidth(0, 38)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setShowGrid(False)
        self.cellClicked.connect(self._clicked)

    def clear_moves(self):
        self.setRowCount(0)

    def set_moves(self, items):
        """items: list of (text, colour_or_None[, QPixmap]) in ply order."""
        self.setRowCount(0)
        for i, item in enumerate(items):
            self.add_move(i + 1, item[0], item[1], item[2] if len(item) > 2 else None)

    def add_move(self, ply, text, color=None, icon=None):
        row, col = (ply - 1) // 2, 1 + (ply - 1) % 2
        if self.rowCount() <= row:
            self.setRowCount(row + 1)
            num = QTableWidgetItem(str(row + 1))
            num.setForeground(QColor(THEME['muted']))
            num.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.setItem(row, 0, num)
        item = QTableWidgetItem(text)
        if color:
            item.setForeground(QColor(color))
        if icon is not None:
            item.setIcon(QIcon(icon))
        self.setItem(row, col, item)
        self.scrollToBottom()

    def set_current(self, ply):
        self.clearSelection()
        if ply <= 0:
            return
        row, col = (ply - 1) // 2, 1 + (ply - 1) % 2
        if row < self.rowCount() and self.item(row, col) is not None:
            self.setCurrentCell(row, col)
            self.scrollToItem(self.item(row, col))

    def _clicked(self, row, col):
        if col in (1, 2) and self.item(row, col) is not None:
            self.ply_selected.emit(row * 2 + col)


# ----------------------------------------------------------------- dialogs
class MatchIntroDialog(QDialog):
    """chess.com style 'match found' card that shows both players before the game starts."""

    def __init__(self, parent, left, right, heading, seconds=3):
        super().__init__(parent, Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setModal(True)
        self.setFixedSize(620, 330)
        self.left_seconds = seconds
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        card = QFrame()
        card.setObjectName('introCard')
        outer.addWidget(card)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(24, 18, 24, 18)
        head = QLabel(heading)
        head.setAlignment(AlignCenter)
        head.setStyleSheet('font-size:15px;font-weight:bold;color:%s;letter-spacing:1px;' % THEME['muted'])
        lay.addWidget(head)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addLayout(self._player_box(left))
        vs = QLabel('VS')
        vs.setStyleSheet('font-size:34px;font-weight:900;color:%s;padding:0 26px;' % THEME['accent'])
        row.addWidget(vs)
        row.addLayout(self._player_box(right))
        row.addStretch(1)
        lay.addLayout(row, 1)
        self.count = QLabel('')
        self.count.setAlignment(AlignCenter)
        self.count.setStyleSheet('font-size:14px;color:%s;' % THEME['muted'])
        lay.addWidget(self.count)
        self.setStyleSheet('QFrame#introCard{background:%s;border:2px solid %s;border-radius:14px;}' % (THEME['panel'], THEME['accent']))
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._tick(first=True)
        self._timer.start(1000)

    def _player_box(self, info):
        name, rating, pix, color_text = info
        col = QVBoxLayout()
        col.setAlignment(AlignCenter)
        av = AvatarLabel(150)
        av.set_avatar(pix, name[:1])
        col.addWidget(av, alignment=AlignCenter)
        n = QLabel(name)
        n.setAlignment(AlignCenter)
        n.setStyleSheet('font-size:20px;font-weight:bold;')
        col.addWidget(n)
        r = QLabel(('%s Elo' % rating) if rating is not None else ' ')
        r.setAlignment(AlignCenter)
        r.setStyleSheet('font-size:14px;color:%s;' % THEME['muted'])
        col.addWidget(r)
        c = QLabel(color_text)
        c.setAlignment(AlignCenter)
        white = color_text == tr('White')
        c.setStyleSheet('font-size:12px;font-weight:bold;padding:3px 12px;border-radius:9px;background:%s;color:%s;' %
                        (('#f2f2f2', '#262522') if white else ('#111111', '#f2f2f2')))
        col.addWidget(c, alignment=AlignCenter)
        return col

    def _tick(self, first=False):
        if not first:
            self.left_seconds -= 1
        if self.left_seconds <= 0:
            self._timer.stop()
            self.accept()
            return
        self.count.setText(tr('Starting in {n}…  (click to skip)').format(n=self.left_seconds))

    def mousePressEvent(self, e):
        self._timer.stop()
        self.accept()


class GameOverDialog(QDialog):
    """Result card with the actions chess.com offers after a game."""

    def __init__(self, parent, title, subtitle, white, black, change_text, buttons, review_enabled=True):
        super().__init__(parent)
        self.setWindowTitle(tr('Game over'))
        self.setModal(True)
        self.setMinimumWidth(460)
        self.choice = 'close'
        lay = QVBoxLayout(self)
        lay.setContentsMargins(26, 22, 26, 22)
        lay.setSpacing(12)
        t = QLabel(title)
        t.setAlignment(AlignCenter)
        t.setStyleSheet('font-size:28px;font-weight:900;')
        lay.addWidget(t)
        s = QLabel(subtitle)
        s.setAlignment(AlignCenter)
        s.setStyleSheet('font-size:14px;color:%s;' % THEME['muted'])
        lay.addWidget(s)
        row = QHBoxLayout()
        row.addStretch(1)
        for info in (white, black):
            col = QVBoxLayout()
            av = AvatarLabel(84)
            av.set_avatar(info[2], info[0][:1])
            col.addWidget(av, alignment=AlignCenter)
            n = QLabel(info[0])
            n.setAlignment(AlignCenter)
            n.setStyleSheet('font-weight:bold;font-size:15px;')
            col.addWidget(n)
            r = QLabel(str(info[1]) if info[1] is not None else '')
            r.setAlignment(AlignCenter)
            r.setStyleSheet('color:%s;' % THEME['muted'])
            col.addWidget(r)
            row.addLayout(col)
            row.addSpacing(34)
        row.addStretch(1)
        lay.addLayout(row)
        if change_text:
            c = QLabel(change_text)
            c.setAlignment(AlignCenter)
            c.setStyleSheet('font-size:18px;font-weight:bold;color:%s;' % THEME['accent'])
            lay.addWidget(c)
        for key, label, primary in buttons:
            b = QPushButton(label)
            b.setObjectName('primary' if primary else '')
            b.setMinimumHeight(44)
            if key == 'review' and not review_enabled:
                b.setEnabled(False)
            b.clicked.connect(lambda checked=False, k=key: self._pick(k))
            lay.addWidget(b)

    def _pick(self, key):
        self.choice = key
        self.accept()


# ------------------------------------------------------------- rules dialog
STYLE_LABELS = {
    'standard': 'Standard (normal chess)',
    'queen': 'Queen movement',
    'rook': 'Rook movement',
    'bishop': 'Bishop movement',
    'knight': 'Knight movement',
    'amazon': 'Amazon (queen + knight)',
    'archbishop': 'Archbishop (bishop + knight)',
    'chancellor': 'Chancellor (rook + knight)',
    'pawn4': 'Pawn: up to 4 forward',
    'anywhere': 'Move anywhere',
}
STYLE_HELP = {
    'standard': 'Normal chess movement.',
    'queen': 'Moves like a queen. The piece keeps its own picture and type.',
    'rook': 'Moves like a rook.',
    'bishop': 'Moves like a bishop.',
    'knight': 'Jumps like a knight.',
    'amazon': 'The AMAZON moves like a queen AND a knight combined - the strongest fairy piece in chess.',
    'archbishop': 'Moves like a bishop and a knight combined.',
    'chancellor': 'Moves like a rook and a knight combined.',
    'pawn4': 'Moves like a pawn but can go up to 4 squares forward, capturing diagonally.',
    'anywhere': 'May jump to ANY square that is empty or holds an enemy piece (never a king). '
                'No move dots are shown, and these pieces do not give check.',
}
TYPE_ORDER = [chess.KING, chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN]
TYPE_NAMES = {chess.KING: 'King', chess.QUEEN: 'Queen', chess.ROOK: 'Rook', chess.BISHOP: 'Bishop',
              chess.KNIGHT: 'Knight', chess.PAWN: 'Pawn'}


class RulesDialog(QDialog):
    """Pick pieces (with their pictures), choose how they move, apply or reset."""

    def __init__(self, parent, rules, pieces, board, on_change):
        super().__init__(parent)
        from rules import STYLES
        self.styles = STYLES
        self.rules, self.pieces, self.board, self.on_change = rules, pieces, board, on_change
        self.setWindowTitle(tr('Custom pieces & rules'))
        self.setMinimumWidth(640)
        lay = QVBoxLayout(self)
        lay.setSpacing(10)
        h1 = QLabel(tr('1. Pick the pieces you want to change (you can select several)'))
        h1.setStyleSheet('font-weight:bold;font-size:14px;')
        lay.addWidget(h1)
        grid = QGridLayout()
        grid.setSpacing(6)
        self.buttons = {}
        for r, color in enumerate((chess.WHITE, chess.BLACK)):
            lab = QLabel(tr('White') if color else tr('Black'))
            lab.setStyleSheet('font-weight:bold;')
            grid.addWidget(lab, r, 0)
            for c, ptype in enumerate(TYPE_ORDER):
                b = QToolButton()
                b.setCheckable(True)
                b.setIcon(QIcon(pieces[(color, ptype)]))
                b.setIconSize(QSize(54, 54))
                b.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
                b.setFixedSize(92, 94)
                b.setObjectName('pieceButton')
                self.buttons[(color, ptype)] = b
                grid.addWidget(b, r, c + 1)
        lay.addLayout(grid)
        quick = QHBoxLayout()
        for text, fn in ((tr('All white'), lambda: self.select_where(lambda c, t: c)),
                         (tr('All black'), lambda: self.select_where(lambda c, t: not c)),
                         (tr('Everything'), lambda: self.select_where(lambda c, t: True)),
                         (tr('Clear selection'), lambda: self.select_where(lambda c, t: False))):
            qb = QPushButton(text)
            qb.clicked.connect(lambda checked=False, f=fn: f())
            quick.addWidget(qb)
        lay.addLayout(quick)
        h2 = QLabel(tr('2. Choose how they move'))
        h2.setStyleSheet('font-weight:bold;font-size:14px;')
        lay.addWidget(h2)
        self.style_box = QComboBox()
        for s in STYLES:
            self.style_box.addItem(tr(STYLE_LABELS[s]), s)
        self.style_box.currentIndexChanged.connect(self.update_help)
        lay.addWidget(self.style_box)
        self.help = QLabel('')
        self.help.setWordWrap(True)
        self.help.setStyleSheet('color:%s;' % THEME['muted'])
        lay.addWidget(self.help)
        prow = QHBoxLayout()
        prow.addWidget(QLabel(tr('No Capture:')))
        self.protect_box = QComboBox()
        self.protect_box.addItem(tr("Don't change"), 'keep')
        self.protect_box.addItem(tr('Protect these pieces on the board'), 'on')
        self.protect_box.addItem(tr('Remove protection'), 'off')
        prow.addWidget(self.protect_box, 1)
        lay.addLayout(prow)
        note = QLabel(tr('Tip: Ctrl + right-click a single piece on the board to toggle No Capture for just that piece.'))
        note.setWordWrap(True)
        note.setStyleSheet('color:%s;font-size:12px;' % THEME['muted'])
        lay.addWidget(note)
        lay.addWidget(self._section(tr('Active rules')))
        self.active = QListWidget()
        self.active.setMaximumHeight(120)
        self.active.setIconSize(QSize(28, 28))
        lay.addWidget(self.active)
        self.status = QLabel('')
        self.status.setStyleSheet('color:%s;font-weight:bold;' % THEME['accent'])
        lay.addWidget(self.status)
        row = QHBoxLayout()
        apply_b = QPushButton(tr('Apply'))
        apply_b.setObjectName('primary')
        apply_b.clicked.connect(self.apply)
        reset_sel = QPushButton(tr('Reset selected'))
        reset_sel.clicked.connect(self.reset_selected)
        reset_all = QPushButton(tr('Reset all rules'))
        reset_all.clicked.connect(self.reset_all)
        close_b = QPushButton(tr('Close'))
        close_b.clicked.connect(self.accept)
        for b in (apply_b, reset_sel, reset_all, close_b):
            row.addWidget(b)
        lay.addLayout(row)
        self.update_help()
        self.refresh()

    def _section(self, text):
        l = QLabel(text)
        l.setStyleSheet('font-weight:bold;font-size:14px;')
        return l

    def update_help(self):
        self.help.setText(tr(STYLE_HELP[self.style_box.currentData()]))

    def select_where(self, pred):
        for (c, t), b in self.buttons.items():
            b.setChecked(bool(pred(c, t)))

    def selected(self):
        return [k for k, b in self.buttons.items() if b.isChecked()]

    def apply(self):
        sel = self.selected()
        if not sel:
            self.status.setText(tr('Select at least one piece first.'))
            return
        style = self.style_box.currentData()
        mode = self.protect_box.currentData()
        for color, ptype in sel:
            self.rules.set_style(color, ptype, style)
        if mode != 'keep':
            squares = set(self.rules.no_capture)
            for sq, p in self.board.piece_map().items():
                if (p.color, p.piece_type) in sel:
                    if mode == 'on':
                        squares.add(sq)
                    else:
                        squares.discard(sq)
            self.rules.set_protected(squares)
        self.status.setText(tr('Applied.'))
        self.after_change()

    def reset_selected(self):
        sel = self.selected()
        if not sel:
            self.status.setText(tr('Select at least one piece first.'))
            return
        self.rules.reset_pieces(sel)
        squares = set(self.rules.no_capture)
        for sq, p in self.board.piece_map().items():
            if (p.color, p.piece_type) in sel:
                squares.discard(sq)
        self.rules.set_protected(squares)
        self.status.setText(tr('Selected pieces are back to normal.'))
        self.after_change()

    def reset_all(self):
        self.rules.reset()
        self.select_where(lambda c, t: False)
        self.status.setText(tr('All rules reset to standard chess.'))
        self.after_change()

    def after_change(self):
        self.refresh()
        self.on_change()

    def refresh(self):
        for (c, t), b in self.buttons.items():
            style = self.rules.moves.get((c, t), 'standard')
            b.setText(tr(STYLE_LABELS[style]).split(' (')[0] if style != 'standard' else tr('Standard'))
        self.active.clear()
        if not self.rules.moves and not self.rules.no_capture:
            self.active.addItem(tr('No custom rules: standard chess.'))
        for (c, t), style in sorted(self.rules.moves.items(), key=lambda kv: (not kv[0][0], TYPE_ORDER.index(kv[0][1]))):
            item = QListWidgetItem(QIcon(self.pieces[(c, t)]),
                                   '%s %s: %s' % (tr('White') if c else tr('Black'), tr(TYPE_NAMES[t]), tr(STYLE_LABELS[style])))
            self.active.addItem(item)
        if self.rules.no_capture:
            self.active.addItem(tr('{n} protected piece(s) (No Capture)').format(n=len(self.rules.no_capture)))
