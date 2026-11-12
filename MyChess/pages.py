"""Menu pages of My Chess (everything except the game and review screens)."""
import os
import time

import chess
from PySide6.QtCore import Qt, Signal, QTimer, QSize
from PySide6.QtGui import QPixmap, QIcon, QColor, QPainter
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QPushButton, QComboBox, QLineEdit,
                               QListWidget, QListWidgetItem, QScrollArea, QButtonGroup, QGridLayout, QGroupBox,
                               QCheckBox, QSlider, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
                               QAbstractItemView, QFileDialog, QMessageBox, QColorDialog, QApplication, QSpinBox)

import coaches
import lan as lanmod
from bots import BOTS, TIERS, STOCKFISH_LEVELS
from game import TIME_CONTROLS
from i18n import tr, LANGUAGES
from themes import BOARD_THEMES, UI_THEMES
from widgets import BoardWidget, AvatarLabel, RatingGraph, SoundManager, CoachBubble, THEME, ASSETS

AlignCenter = Qt.AlignmentFlag.AlignCenter
AlignTop = Qt.AlignmentFlag.AlignTop


class ClickFrame(QFrame):
    clicked = Signal()

    def mousePressEvent(self, e):
        self.clicked.emit()


def title_label(text):
    l = QLabel(text)
    l.setObjectName('pageTitle')
    return l


def muted_label(text, wrap=True):
    l = QLabel(text)
    l.setObjectName('muted')
    l.setWordWrap(wrap)
    return l


def primary_button(text, fn=None):
    b = QPushButton(text)
    b.setObjectName('primary')
    if fn:
        b.clicked.connect(lambda checked=False: fn())
    return b


def tc_combo(current):
    box = QComboBox()
    for name, base, inc in TIME_CONTROLS:
        box.addItem(tr(name) if name == 'No limit' else name, name)
    idx = box.findData(current)
    box.setCurrentIndex(idx if idx >= 0 else 7)
    return box


def page_root(page):
    page.setObjectName('pageRoot')
    lay = QVBoxLayout(page)
    lay.setContentsMargins(26, 18, 26, 18)
    lay.setSpacing(12)
    return lay


# ====================================================================== HOME
class HomePage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        root = QHBoxLayout(self)
        root.setContentsMargins(26, 18, 26, 18)
        root.setSpacing(34)
        self.preview = BoardWidget(app.pieces)
        self.preview.interactive = False
        self.preview.setMinimumSize(380, 380)
        root.addWidget(self.preview, 3)
        right = QVBoxLayout()
        right.setSpacing(10)
        right.addWidget(title_label(tr('Play Chess')))
        right.addWidget(muted_label(tr('Your chess game, your rules.')))
        right.addSpacing(6)
        self.tc = tc_combo(app.store.prefs.get('time_control', '10 min'))
        self.tc.currentIndexChanged.connect(self._tc_changed)
        right.addWidget(QLabel(tr('Time control')))
        right.addWidget(self.tc)
        right.addWidget(primary_button('🤖  ' + tr('Play Bots'), lambda: app.show_page('bots')))
        right.addWidget(primary_button('🌐  ' + tr('Play a Friend (LAN)'), lambda: app.show_page('lan')))
        right.addWidget(primary_button('♟  ' + tr('Pass & Play'), lambda: app.start_local_game(self.tc.currentData())))
        b = QPushButton('📂  ' + tr('Review a game (PGN)'))
        b.clicked.connect(lambda: app.review_pgn_file())
        right.addWidget(b)
        self.coach_card = CoachBubble(64)
        right.addWidget(self.coach_card)
        crow = QHBoxLayout()
        lb = QPushButton('🎓  ' + tr('Lessons'))
        lb.clicked.connect(lambda: app.show_page('learn'))
        pb = QPushButton('🧩  ' + tr('Puzzles'))
        pb.clicked.connect(lambda: app.show_page('puzzles'))
        eb = QPushButton('📐  ' + tr('Positions'))
        eb.clicked.connect(lambda: app.show_page('positions'))
        for b_ in (lb, pb, eb):
            crow.addWidget(b_)
        right.addLayout(crow)
        self.card = QFrame()
        self.card.setObjectName('panel')
        cl = QHBoxLayout(self.card)
        cl.setContentsMargins(14, 12, 14, 12)
        self.avatar = AvatarLabel(64)
        cl.addWidget(self.avatar)
        col = QVBoxLayout()
        self.name = QLabel('')
        self.name.setStyleSheet('font-size:18px;font-weight:bold;')
        self.elo = QLabel('')
        self.record = QLabel('')
        self.record.setObjectName('muted')
        col.addWidget(self.name)
        col.addWidget(self.elo)
        col.addWidget(self.record)
        cl.addLayout(col, 1)
        right.addWidget(self.card)
        right.addWidget(QLabel(tr('Recent games')))
        self.recent = QListWidget()
        self.recent.setMaximumHeight(150)
        self.recent.itemDoubleClicked.connect(self._open_recent)
        right.addWidget(self.recent)
        right.addStretch(1)
        root.addLayout(right, 2)
        self.entries = []

    def _tc_changed(self):
        self.app.store.prefs['time_control'] = self.tc.currentData()
        self.app.store.save_prefs()

    def refresh(self):
        s = self.app.store
        c = self.app.coach()
        self.coach_card.set_coach(tr('Your coach: {name}').format(name=c.name), self.app.coach_pixmap())
        self.coach_card.say(tr('Tip of the day:') + ' ' + tr(coaches.tip_of_the_day()))
        self.avatar.set_avatar(self.app.my_pixmap(), s.profile['username'][:1])
        self.name.setText(s.profile['username'])
        self.elo.setText('%d Elo' % s.profile['rating'])
        w = d = l = 0
        for h in s.history:
            o = h.get('outcome')
            w += o == 'win'
            d += o == 'draw'
            l += o == 'loss'
        self.record.setText(tr('Record: {w} W / {d} D / {l} L').format(w=w, d=d, l=l))
        self.recent.clear()
        self.entries = list(reversed(s.history[-5:]))
        for h in self.entries:
            icon = {'win': '✅', 'loss': '❌', 'draw': '➖'}.get(h.get('outcome'), '')
            self.recent.addItem('%s  %s' % (icon, h.get('opponent', {}).get('name', '?')))
        bt = self.app.store.prefs
        self.preview.light = self.app.light_color()
        self.preview.dark = self.app.dark_color()
        self.preview.show_coords = bt.get('show_coordinates', True)
        self.preview.board = chess.Board()
        self.preview.clear_cache()

    def _open_recent(self, item):
        i = self.recent.row(item)
        if 0 <= i < len(self.entries):
            self.app.open_review(self.entries[i])


# ======================================================================= BOTS
class BotsPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.sel = BOTS[1]
        self.cards = {}
        root = QHBoxLayout(self)
        root.setContentsMargins(26, 18, 26, 18)
        root.setSpacing(20)
        left = QVBoxLayout()
        left.addWidget(title_label(tr('Play Bots')))
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        il = QVBoxLayout(inner)
        il.setSpacing(6)
        for tier in TIERS:
            head = QLabel(tr(tier).upper())
            head.setObjectName('muted')
            head.setStyleSheet('font-weight:bold;letter-spacing:1px;margin-top:8px;')
            il.addWidget(head)
            for bot in [b for b in BOTS if b.tier == tier]:
                il.addWidget(self._card(bot))
        il.addStretch(1)
        scroll.setWidget(inner)
        left.addWidget(scroll, 1)
        root.addLayout(left, 3)

        detail = QFrame()
        detail.setObjectName('panel')
        detail.setFixedWidth(360)
        dl = QVBoxLayout(detail)
        dl.setContentsMargins(20, 20, 20, 20)
        dl.setSpacing(8)
        self.big = AvatarLabel(150)
        dl.addWidget(self.big, alignment=AlignCenter)
        self.dname = QLabel('')
        self.dname.setAlignment(AlignCenter)
        self.dname.setStyleSheet('font-size:24px;font-weight:800;')
        dl.addWidget(self.dname)
        self.delo = QLabel('')
        self.delo.setAlignment(AlignCenter)
        self.delo.setStyleSheet('font-size:15px;font-weight:bold;')
        dl.addWidget(self.delo)
        self.dblurb = muted_label('')
        self.dblurb.setAlignment(AlignCenter)
        dl.addWidget(self.dblurb)
        self.level_label = QLabel(tr('Stockfish level'))
        self.level = QComboBox()
        for name, elo in STOCKFISH_LEVELS:
            self.level.addItem('%s (%d)' % (tr(name), elo), elo)
        self.level.setCurrentIndex(1)
        dl.addWidget(self.level_label)
        dl.addWidget(self.level)
        dl.addWidget(QLabel(tr('Play as')))
        row = QHBoxLayout()
        self.side_group = QButtonGroup(self)
        self.side_buttons = {}
        for key, text in (('white', '♔ ' + tr('White')), ('random', '🎲 ' + tr('Random')), ('black', '♚ ' + tr('Black'))):
            b = QPushButton(text)
            b.setObjectName('sideChoice')
            b.setCheckable(True)
            self.side_group.addButton(b)
            self.side_buttons[key] = b
            row.addWidget(b)
        self.side_buttons['random'].setChecked(True)
        dl.addLayout(row)
        dl.addWidget(QLabel(tr('Time control')))
        self.tc = tc_combo(app.store.prefs.get('time_control', '10 min'))
        dl.addWidget(self.tc)
        dl.addWidget(QLabel(tr('Starting position')))
        self.odds = QComboBox()
        for text, key in ((tr('Standard'), 'std'), (tr('Bot starts without its queen'), 'bot:Q'),
                          (tr('Bot starts without a rook'), 'bot:R'), (tr('Bot starts without a bishop'), 'bot:B'),
                          (tr('Bot starts without a knight'), 'bot:N'), (tr('I start without my queen'), 'me:Q'),
                          (tr('I start without a rook'), 'me:R'), (tr('I start without a knight'), 'me:N')):
            self.odds.addItem(text, key)
        dl.addWidget(self.odds)
        self.play = primary_button(tr('Play'), self.start)
        dl.addSpacing(6)
        dl.addWidget(self.play)
        self.engine_note = muted_label('')
        dl.addWidget(self.engine_note)
        dl.addStretch(1)
        root.addWidget(detail)
        self.select(self.sel)

    def _card(self, bot):
        card = ClickFrame()
        card.setObjectName('card')
        lay = QHBoxLayout(card)
        lay.setContentsMargins(10, 8, 14, 8)
        av = AvatarLabel(54)
        av.set_avatar(self.app.bot_pixmap(bot), bot.name[:1])
        lay.addWidget(av)
        col = QVBoxLayout()
        col.setSpacing(1)
        n = QLabel('%s  ·  %s' % (bot.name, ('%d–3190' % 1320) if bot.is_engine else bot.elo))
        n.setStyleSheet('font-weight:bold;font-size:15px;')
        col.addWidget(n)
        b = muted_label(tr(bot.blurb), wrap=False)
        col.addWidget(b)
        lay.addLayout(col, 1)
        card.clicked.connect(lambda bt=bot: self.select(bt))
        self.cards[bot.id] = card
        return card

    def select(self, bot):
        self.sel = bot
        for bid, card in self.cards.items():
            card.setObjectName('cardSelected' if bid == bot.id else 'card')
            card.style().unpolish(card)
            card.style().polish(card)
        self.big.set_avatar(self.app.bot_pixmap(bot), bot.name[:1])
        self.dname.setText(bot.name)
        self.delo.setText(tr('{tier}  ·  {elo} Elo').format(tier=tr(bot.tier), elo=bot.elo if not bot.is_engine else '1320–3190'))
        self.dblurb.setText(tr(bot.blurb))
        self.level.setVisible(bot.is_engine)
        self.level_label.setVisible(bot.is_engine)
        self.refresh()

    def refresh(self):
        has = bool(self.app.engine_path())
        if self.sel.is_engine and not has:
            self.engine_note.setText(tr('Stockfish was not found. The built-in engine will play instead (see Settings).'))
        elif self.sel.elo >= 1320 and not has:
            self.engine_note.setText(tr('Tip: install/locate Stockfish in Settings for full strength at this level.'))
        else:
            self.engine_note.setText('')

    def start(self):
        side = [k for k, b in self.side_buttons.items() if b.isChecked()][0]
        elo = self.level.currentData() if self.sel.is_engine else self.sel.elo
        self.app.store.prefs['time_control'] = self.tc.currentData()
        self.app.store.save_prefs()
        self.app.start_bot_game(self.sel, elo, side, self.tc.currentData(), self.odds.currentData())


# ======================================================================== LAN
class LanPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        root = page_root(self)
        root.addWidget(title_label(tr('Play a Friend (LAN)')))
        root.addWidget(muted_label(tr('Both computers must be on the same Wi-Fi / network. One player hosts, the other joins. '
                                      'If Windows asks, allow My Chess on Private networks.')))
        cols = QHBoxLayout()
        cols.setSpacing(18)
        root.addLayout(cols, 1)
        # ---- host
        host = QFrame()
        host.setObjectName('panel')
        hl = QVBoxLayout(host)
        hl.setContentsMargins(18, 16, 18, 16)
        hl.setSpacing(8)
        h = QLabel(tr('Host a game'))
        h.setStyleSheet('font-size:18px;font-weight:bold;')
        hl.addWidget(h)
        ip_row = QHBoxLayout()
        self.ip = QLabel('')
        self.ip.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.ip.setStyleSheet('font-size:16px;font-weight:bold;')
        copy = QPushButton(tr('Copy'))
        copy.clicked.connect(lambda: QApplication.clipboard().setText(self.ip.text()))
        ip_row.addWidget(QLabel(tr('Your address:')))
        ip_row.addWidget(self.ip, 1)
        ip_row.addWidget(copy)
        hl.addLayout(ip_row)
        hl.addWidget(QLabel(tr('Port')))
        self.port = QLineEdit(str(app.store.prefs.get('last_host_port', lanmod.DEFAULT_PORT)))
        hl.addWidget(self.port)
        hl.addWidget(QLabel(tr('Time control')))
        self.tc = tc_combo(app.store.prefs.get('time_control', '10 min'))
        hl.addWidget(self.tc)
        hl.addWidget(QLabel(tr('You play')))
        self.side = QComboBox()
        self.side.addItem(tr('White'), 'white')
        self.side.addItem(tr('Black'), 'black')
        self.side.addItem(tr('Random'), 'random')
        hl.addWidget(self.side)
        self.host_btn = primary_button(tr('Host game'), self.start_host)
        hl.addWidget(self.host_btn)
        self.cancel_btn = QPushButton(tr('Stop hosting'))
        self.cancel_btn.clicked.connect(self.stop_host)
        self.cancel_btn.setVisible(False)
        hl.addWidget(self.cancel_btn)
        self.status = muted_label('')
        hl.addWidget(self.status)
        hl.addStretch(1)
        cols.addWidget(host, 1)
        # ---- join
        join = QFrame()
        join.setObjectName('panel')
        jl = QVBoxLayout(join)
        jl.setContentsMargins(18, 16, 18, 16)
        jl.setSpacing(8)
        j = QLabel(tr('Join a game'))
        j.setStyleSheet('font-size:18px;font-weight:bold;')
        jl.addWidget(j)
        jl.addWidget(muted_label(tr('Games on your network appear here automatically:')))
        self.found = QListWidget()
        self.found.itemDoubleClicked.connect(self.join_selected)
        jl.addWidget(self.found, 1)
        jl.addWidget(primary_button(tr('Join selected game'), self.join_selected))
        jl.addWidget(muted_label(tr('…or type the host address:')))
        row = QHBoxLayout()
        self.manual_ip = QLineEdit()
        self.manual_ip.setPlaceholderText(tr('Host IP, e.g. 192.168.1.20'))
        self.manual_port = QLineEdit(str(lanmod.DEFAULT_PORT))
        self.manual_port.setFixedWidth(80)
        row.addWidget(self.manual_ip, 1)
        row.addWidget(self.manual_port)
        jl.addLayout(row)
        b = QPushButton(tr('Join'))
        b.clicked.connect(self.join_manual)
        jl.addWidget(b)
        cols.addWidget(join, 1)
        self.keys = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_found)
        self.timer.start(1000)

    def refresh(self):
        self.ip.setText(lanmod.get_lan_ip() or tr('(not connected to a network)'))
        self.refresh_found()

    def set_hosting(self, hosting, text=''):
        self.host_btn.setVisible(not hosting)
        self.cancel_btn.setVisible(hosting)
        self.status.setText(text)

    def start_host(self):
        try:
            port = int(self.port.text())
            if not 1024 <= port <= 65535:
                raise ValueError(tr('Port must be between 1024 and 65535.'))
        except ValueError as e:
            QMessageBox.warning(self, tr('LAN'), str(e))
            return
        self.app.store.prefs['last_host_port'] = port
        self.app.store.prefs['time_control'] = self.tc.currentData()
        self.app.store.save_prefs()
        self.app.host_lan(port, self.tc.currentData(), self.side.currentData())

    def stop_host(self):
        self.app.lan_cancel()

    def refresh_found(self):
        now = time.monotonic()
        found = [f for f in self.app.discovered.values() if now - f['seen'] < 4.0 and f.get('id') != self.app.store.profile['id']]
        keys = [(f['host'], f['port']) for f in found]
        if keys == self.keys:
            return
        self.keys = keys
        self.found.clear()
        for f in found:
            star = '★ ' if self.app.store.find_friend(f.get('id')) else ''
            rating = (' (%s)' % f['rating']) if f.get('rating') else ''
            item = QListWidgetItem('%s%s%s   —   %s:%d   %s' % (star, f['name'], rating, f['host'], f['port'], f.get('tc', '')))
            item.setData(Qt.ItemDataRole.UserRole, (f['host'], f['port']))
            self.found.addItem(item)
        if not found:
            self.found.addItem(tr('No games found yet…'))
            self.found.item(0).setFlags(Qt.ItemFlag.NoItemFlags)

    def join_selected(self, *args):
        item = self.found.currentItem()
        data = item.data(Qt.ItemDataRole.UserRole) if item else None
        if not data:
            QMessageBox.information(self, tr('LAN'), tr('Select a game from the list first.'))
            return
        self.app.join_lan(data[0], data[1])

    def join_manual(self):
        host = self.manual_ip.text().strip()
        if not host:
            QMessageBox.information(self, tr('LAN'), tr('Enter the host computer IP address.'))
            return
        try:
            port = int(self.manual_port.text())
        except ValueError:
            QMessageBox.warning(self, tr('LAN'), tr('Port must be a number.'))
            return
        self.app.join_lan(host, port)


# ===================================================================== FRIENDS
class FriendsPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        root = page_root(self)
        root.addWidget(title_label(tr('Friends')))
        root.addWidget(muted_label(tr('Add a friend during a LAN game with the "Add friend" button. '
                                      'Friends are saved on this computer with their last address, so you can challenge them again.')))
        row = QHBoxLayout()
        row.setSpacing(18)
        self.list = QListWidget()
        self.list.setIconSize(QSize(44, 44))
        self.list.currentRowChanged.connect(self.show_detail)
        row.addWidget(self.list, 2)
        det = QFrame()
        det.setObjectName('panel')
        det.setMinimumWidth(320)
        dl = QVBoxLayout(det)
        dl.setContentsMargins(20, 20, 20, 20)
        self.av = AvatarLabel(110)
        dl.addWidget(self.av, alignment=AlignCenter)
        self.name = QLabel('')
        self.name.setAlignment(AlignCenter)
        self.name.setStyleSheet('font-size:22px;font-weight:800;')
        dl.addWidget(self.name)
        self.info = muted_label('')
        self.info.setAlignment(AlignCenter)
        dl.addWidget(self.info)
        self.h2h = QLabel('')
        self.h2h.setAlignment(AlignCenter)
        dl.addWidget(self.h2h)
        self.addr = QLineEdit()
        self.addr.setPlaceholderText(tr('Address (IP:port)'))
        dl.addWidget(self.addr)
        self.challenge = primary_button(tr('Challenge'), self.do_challenge)
        dl.addWidget(self.challenge)
        self.save_btn = QPushButton(tr('Save address'))
        self.save_btn.clicked.connect(self.save_addr)
        dl.addWidget(self.save_btn)
        self.remove = QPushButton(tr('Remove friend'))
        self.remove.clicked.connect(self.do_remove)
        dl.addWidget(self.remove)
        dl.addStretch(1)
        row.addWidget(det, 1)
        root.addLayout(row, 1)
        self.ids = []

    def refresh(self):
        st = self.app.store
        self.list.blockSignals(True)
        self.list.clear()
        self.ids = []
        now = time.monotonic()
        online = {f.get('id') for f in self.app.discovered.values() if now - f['seen'] < 4.0}
        for f in st.friends:
            pix = self.app.friend_pixmap(f)
            icon = QIcon(self.app.round_icon(pix, 44, f.get('name', '?')))
            status = tr('hosting now') if f['id'] in online else ''
            item = QListWidgetItem(icon, '%s  (%s)   %s' % (f.get('name', '?'), f.get('rating', '?'), status))
            self.list.addItem(item)
            self.ids.append(f['id'])
        self.list.blockSignals(False)
        if st.friends:
            self.list.setCurrentRow(0)
        self.show_detail(self.list.currentRow())

    def current(self):
        r = self.list.currentRow()
        if 0 <= r < len(self.ids):
            return self.app.store.find_friend(self.ids[r])
        return None

    def show_detail(self, row):
        f = self.current()
        has = f is not None
        for w in (self.challenge, self.save_btn, self.remove, self.addr):
            w.setEnabled(has)
        if not has:
            self.av.set_avatar(None, '?')
            self.name.setText(tr('No friends yet'))
            self.info.setText('')
            self.h2h.setText('')
            self.addr.setText('')
            return
        self.av.set_avatar(self.app.friend_pixmap(f), f.get('name', '?')[:1])
        self.name.setText(f.get('name', '?'))
        self.info.setText('%s Elo' % f.get('rating', '?'))
        w, d, l = self.app.store.head_to_head(opponent_id=f['id'])
        self.h2h.setText(tr('Head to head: {w} W / {d} D / {l} L').format(w=w, d=d, l=l))
        self.addr.setText('%s:%s' % (f.get('host', ''), f.get('port', lanmod.DEFAULT_PORT)))

    def parse_addr(self):
        text = self.addr.text().strip()
        host, _, port = text.partition(':')
        try:
            return host.strip(), int(port) if port else lanmod.DEFAULT_PORT
        except ValueError:
            return host.strip(), lanmod.DEFAULT_PORT

    def save_addr(self):
        f = self.current()
        if f:
            f['host'], f['port'] = self.parse_addr()
            self.app.store.save_friends()

    def do_challenge(self):
        f = self.current()
        if not f:
            return
        # a friend who is hosting right now is found by id, otherwise use the saved address
        now = time.monotonic()
        for info in self.app.discovered.values():
            if info.get('id') == f['id'] and now - info['seen'] < 4.0:
                self.app.join_lan(info['host'], info['port'])
                return
        host, port = self.parse_addr()
        if not host:
            QMessageBox.information(self, tr('Friends'), tr('No address saved for this friend yet.'))
            return
        self.app.join_lan(host, port)

    def do_remove(self):
        f = self.current()
        if f and QMessageBox.question(self, tr('Friends'), tr('Remove {name} from your friends?').format(name=f.get('name', '?'))) == QMessageBox.StandardButton.Yes:
            self.app.store.remove_friend(f['id'])
            self.refresh()


# ===================================================================== HISTORY
class HistoryPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        root = page_root(self)
        root.addWidget(title_label(tr('Match History')))
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([tr('Date'), tr('Opponent'), tr('Color'), tr('Result'), tr('Moves'), tr('Mode'), 'Elo'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.verticalHeader().setDefaultSectionSize(34)
        self.table.cellDoubleClicked.connect(lambda r, c: self.review())
        tabs = QTabWidget()
        root.addWidget(tabs, 1)
        games = QWidget()
        gl = QVBoxLayout(games)
        gl.setContentsMargins(0, 8, 0, 0)
        gl.addWidget(self.table, 1)
        row = QHBoxLayout()
        self.review_btn = primary_button(tr('Game Review'), self.review)
        self.export_btn = QPushButton(tr('Export PGN'))
        self.export_btn.clicked.connect(self.export)
        self.del_btn = QPushButton(tr('Delete'))
        self.del_btn.clicked.connect(self.delete)
        for b in (self.review_btn, self.export_btn, self.del_btn):
            row.addWidget(b)
        row.addStretch(1)
        gl.addLayout(row)
        tabs.addTab(games, tr('Games'))
        stats = QWidget()
        sl = QVBoxLayout(stats)
        sl.setContentsMargins(0, 8, 0, 0)
        sl.setSpacing(10)
        cards = QHBoxLayout()
        self.stat_values = {}
        for key, caption in (('games', tr('Games')), ('winrate', tr('Win rate')), ('record', tr('Wins / Draws / Losses')),
                             ('peak', tr('Peak Elo')), ('streak', tr('Best win streak'))):
            card = QFrame()
            card.setObjectName('panel')
            cv = QVBoxLayout(card)
            cv.setContentsMargins(14, 10, 14, 10)
            val = QLabel('-')
            val.setStyleSheet('font-size:24px;font-weight:900;')
            cap = QLabel(caption)
            cap.setObjectName('muted')
            cv.addWidget(val)
            cv.addWidget(cap)
            cards.addWidget(card)
            self.stat_values[key] = val
        sl.addLayout(cards)
        sl.addWidget(QLabel(tr('Elo progress')))
        self.graph = RatingGraph()
        sl.addWidget(self.graph)
        sl.addWidget(QLabel(tr('Achievements')))
        self.ach = QListWidget()
        sl.addWidget(self.ach, 1)
        tabs.addTab(stats, tr('Stats'))
        self.entries = []

    def refresh(self):
        self.entries = list(reversed(self.app.store.history))
        self.table.setRowCount(len(self.entries))
        for r, h in enumerate(self.entries):
            opp = h.get('opponent', {})
            date = time.strftime('%Y-%m-%d %H:%M', time.localtime(h.get('date', 0)))
            outcome = h.get('outcome', '')
            text = {'win': tr('Win'), 'loss': tr('Loss'), 'draw': tr('Draw')}.get(outcome, '')
            change = h.get('change')
            vals = [date, '%s (%s)' % (opp.get('name', '?'), opp.get('rating')) if opp.get('rating') is not None else opp.get('name', '?'),
                    tr('White') if h.get('color') == 'white' else tr('Black'), text, str((h.get('plies', 0) + 1) // 2),
                    {'bot': tr('Bot'), 'lan': 'LAN', 'local': tr('Pass & Play')}.get(h.get('mode'), ''),
                    ('%+d' % change) if change is not None else '—']
            for c, v in enumerate(vals):
                item = QTableWidgetItem(v)
                if c == 3:
                    item.setForeground(QColor({'win': '#81b64c', 'loss': '#ca3431'}.get(outcome, '#a3a19f')))
                self.table.setItem(r, c, item)
        self.update_buttons()
        self.update_stats()

    def update_stats(self):
        hist = self.app.store.history
        wins = sum(1 for h in hist if h.get('outcome') == 'win')
        draws = sum(1 for h in hist if h.get('outcome') == 'draw')
        losses = sum(1 for h in hist if h.get('outcome') == 'loss')
        games = len(hist)
        streak = best = 0
        for h in hist:
            streak = streak + 1 if h.get('outcome') == 'win' else 0
            best = max(best, streak)
        rated_points = [h['rating_after'] for h in hist if h.get('rated') and 'rating_after' in h]
        peak = max([self.app.store.profile['rating']] + rated_points)
        self.stat_values['games'].setText(str(games))
        self.stat_values['winrate'].setText('%d%%' % round(100.0 * wins / games) if games else '-')
        self.stat_values['record'].setText('%d / %d / %d' % (wins, draws, losses))
        self.stat_values['peak'].setText(str(peak))
        self.stat_values['streak'].setText(str(best))
        self.graph.set_points(([800] + rated_points) if rated_points else [])
        standard = [h for h in hist if h.get('start_fen', chess.STARTING_FEN) == chess.STARTING_FEN and not h.get('rules_used')]
        beaten = [h.get('opponent', {}).get('rating') or 0 for h in standard if h.get('outcome') == 'win' and h.get('opponent', {}).get('bot')]
        top_bot = max(beaten) if beaten else 0
        ach = [
            (tr('First Win'), tr('Win your first game'), wins >= 1),
            (tr('Getting Started'), tr('Play 10 games'), games >= 10),
            (tr('Regular'), tr('Play 50 games'), games >= 50),
            (tr('Hat Trick'), tr('Win 3 games in a row'), best >= 3),
            (tr('Giant Slayer'), tr('Beat a bot rated 1000 or higher'), top_bot >= 1000),
            (tr('Bot Crusher'), tr('Beat a bot rated 1600 or higher'), top_bot >= 1600),
            (tr('Master Slayer'), tr('Beat a bot rated 2200 or higher'), top_bot >= 2200),
            (tr('Quick Strike'), tr('Win by checkmate in 20 moves or fewer'),
             any(h.get('outcome') == 'win' and h.get('reason') == 'checkmate' and h.get('plies', 99) <= 40 for h in hist)),
            (tr('Black Belt'), tr('Win a game as Black'), any(h.get('outcome') == 'win' and h.get('color') == 'black' for h in hist)),
            (tr('Peacemaker'), tr('Draw a game'), draws >= 1),
            (tr('Climber'), tr('Reach 1000 Elo'), peak >= 1000),
            (tr('Social'), tr('Add a friend'), len(self.app.store.friends) >= 1),
            (tr('Rule Bender'), tr('Play a game with custom rules'), any(h.get('rules_used') for h in hist)),
        ]
        self.ach.clear()
        for title, desc, done in ach:
            item = QListWidgetItem(('✔  ' if done else '○  ') + title + '  —  ' + desc)
            item.setForeground(QColor('#81b64c' if done else '#8a8886'))
            self.ach.addItem(item)

    def update_buttons(self):
        has = self.table.currentRow() >= 0 or self.table.rowCount() > 0
        for b in (self.review_btn, self.export_btn, self.del_btn):
            b.setEnabled(has)

    def current(self):
        r = self.table.currentRow()
        if r < 0 and self.entries:
            r = 0
        return self.entries[r] if 0 <= r < len(self.entries) else None

    def review(self):
        h = self.current()
        if not h:
            return
        if h.get('rules_used'):
            QMessageBox.information(self, tr('Game Review'), tr('Game review needs standard chess rules.'))
            return
        self.app.open_review(h)

    def export(self):
        h = self.current()
        if not h:
            return
        path, _ = QFileDialog.getSaveFileName(self, tr('Save game as PGN'), 'game.pgn', 'PGN (*.pgn)')
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(h.get('pgn', ''))
            except OSError as e:
                QMessageBox.warning(self, tr('Export PGN'), str(e))

    def delete(self):
        h = self.current()
        if h and QMessageBox.question(self, tr('Match History'), tr('Delete this game from your history?')) == QMessageBox.StandardButton.Yes:
            self.app.store.delete_history(h['id'])
            self.refresh()
            self.app.refresh_pages()


# ==================================================================== SETTINGS
class SettingsPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.loading = True
        root = page_root(self)
        root.addWidget(title_label(tr('Settings')))
        tabs = QTabWidget()
        root.addWidget(tabs, 1)
        tabs.addTab(self._profile_tab(), tr('Profile'))
        tabs.addTab(self._coach_tab(), tr('Coach'))
        tabs.addTab(self._appearance_tab(), tr('Appearance'))
        tabs.addTab(self._game_tab(), tr('Game'))
        tabs.addTab(self._engine_tab(), tr('Engine'))
        self.loading = False

    def _scroll(self, widget):
        s = QScrollArea()
        s.setWidgetResizable(True)
        s.setWidget(widget)
        return s

    # ---- profile
    def _profile_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(12)
        st = self.app.store
        top = QHBoxLayout()
        self.pavatar = AvatarLabel(110)
        top.addWidget(self.pavatar)
        col = QVBoxLayout()
        col.addWidget(QLabel(tr('Username')))
        self.username = QLineEdit(st.profile['username'])
        self.username.setMaxLength(20)
        self.username.editingFinished.connect(self.save_username)
        col.addWidget(self.username)
        self.elo_label = QLabel('')
        self.elo_label.setStyleSheet('font-weight:bold;')
        col.addWidget(self.elo_label)
        reset = QPushButton(tr('Reset Elo to 800'))
        reset.clicked.connect(self.reset_elo)
        col.addWidget(reset)
        top.addLayout(col, 1)
        lay.addLayout(top)
        b = QPushButton(tr('Upload profile picture…'))
        b.clicked.connect(self.choose_picture)
        lay.addWidget(b)
        lay.addWidget(QLabel(tr('…or pick an avatar:')))
        grid = QGridLayout()
        folder = os.path.join(ASSETS, 'profiles', 'avatars')
        names = sorted(f[:-4] for f in os.listdir(folder) if f.endswith('.png')) if os.path.isdir(folder) else []
        for i, name in enumerate(names):
            btn = QPushButton()
            btn.setIcon(QIcon(self.app.round_icon(QPixmap(os.path.join(folder, name + '.png')), 64, name)))
            btn.setIconSize(QSize(64, 64))
            btn.setFixedSize(76, 76)
            btn.clicked.connect(lambda checked=False, n=name: self.pick_preset(n))
            grid.addWidget(btn, i // 6, i % 6)
        lay.addLayout(grid)
        lay.addStretch(1)
        self.update_profile_view()
        return self._scroll(w)

    def update_profile_view(self):
        p = self.app.store.profile
        self.pavatar.set_avatar(self.app.my_pixmap(), p['username'][:1])
        self.elo_label.setText(tr('Your rating: {elo} Elo  ·  {n} rated games').format(elo=p['rating'], n=p.get('games', 0)))

    def save_username(self):
        if self.loading:
            return
        name = self.username.text().strip()
        if name:
            self.app.store.profile['username'] = name
            self.app.store.save_profile()
            self.update_profile_view()
            self.app.refresh_pages()

    def reset_elo(self):
        self.app.store.profile['rating'] = 800
        self.app.store.profile['games'] = 0
        self.app.store.save_profile()
        self.update_profile_view()
        self.app.refresh_pages()

    def pick_preset(self, name):
        self.app.store.profile['avatar'] = name
        self.app.store.save_profile()
        self.app.invalidate_avatar()
        self.update_profile_view()
        self.app.refresh_pages()

    def choose_picture(self):
        path, _ = QFileDialog.getOpenFileName(self, tr('Choose a picture'), '', 'Images (*.png *.jpg *.jpeg *.bmp *.webp)')
        if not path:
            return
        pix = QPixmap(path)
        if pix.isNull():
            QMessageBox.warning(self, tr('Profile'), tr('That picture could not be loaded.'))
            return
        side = min(pix.width(), pix.height())
        pix = pix.copy((pix.width() - side) // 2, (pix.height() - side) // 2, side, side).scaled(
            256, 256, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        pix.save(self.app.store.custom_avatar_path(), 'PNG')
        self.app.store.profile['avatar'] = 'custom'
        self.app.store.save_profile()
        self.app.invalidate_avatar()
        self.update_profile_view()
        self.app.refresh_pages()

    # ---- coach
    def _coach_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(10)
        lay.addWidget(muted_label(tr('Pick the coach who teaches you in Lessons, Puzzles, Game Review and live tips. '
                                     'You can change your coach here at any time.')))
        self.coach_cards = {}
        grid = QGridLayout()
        grid.setSpacing(10)
        for i, c in enumerate(coaches.COACHES):
            card = ClickFrame()
            card.setObjectName('card')
            cl = QHBoxLayout(card)
            cl.setContentsMargins(10, 8, 12, 8)
            av = AvatarLabel(64)
            av.set_avatar(self.app.coach_pixmap(c), c.name[:1])
            cl.addWidget(av)
            col = QVBoxLayout()
            n = QLabel(c.name)
            n.setStyleSheet('font-weight:bold;font-size:15px;')
            b = muted_label(tr(c.blurb))
            col.addWidget(n)
            col.addWidget(b)
            cl.addLayout(col, 1)
            card.clicked.connect(lambda cid=c.id: self.pick_coach(cid))
            self.coach_cards[c.id] = card
            grid.addWidget(card, i // 2, i % 2)
        lay.addLayout(grid)
        self.live_coach_check = QCheckBox(tr('Live coach tips during bot games'))
        self.live_coach_check.setChecked(bool(self.app.store.prefs.get('coach_live', True)))
        self.live_coach_check.toggled.connect(lambda on: self.set_pref('coach_live', on))
        lay.addWidget(self.live_coach_check)
        lay.addWidget(muted_label(tr('Coach comments are generic coaching lines, not quotes from the real people.')))
        lay.addStretch(1)
        self.mark_coach()
        return self._scroll(w)

    def mark_coach(self):
        current = self.app.store.prefs.get('coach', 'levy')
        for cid, card in self.coach_cards.items():
            card.setObjectName('cardSelected' if cid == current else 'card')
            card.style().unpolish(card)
            card.style().polish(card)

    def pick_coach(self, cid):
        self.app.store.prefs['coach'] = cid
        self.app.store.save_prefs()
        self.mark_coach()
        self.app.sound.play('notify')

    # ---- appearance
    def _appearance_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(10)
        pr = self.app.store.prefs

        def combo(items, current, handler):
            c = QComboBox()
            for text, data in items:
                c.addItem(text, data)
            i = c.findData(current)
            c.setCurrentIndex(max(0, i))
            c.currentIndexChanged.connect(lambda idx, cb=c: None if self.loading else handler(cb.currentData()))
            return c
        lay.addWidget(QLabel(tr('Language')))
        lay.addWidget(combo([(n, k) for k, n in LANGUAGES.items()], pr['language'], self.set_language))
        lay.addWidget(QLabel(tr('App theme')))
        lay.addWidget(combo([(k, k) for k in UI_THEMES], pr['ui_theme'], self.set_ui_theme))
        lay.addWidget(QLabel(tr('Board theme')))
        self.board_box = combo([(k, k) for k in BOARD_THEMES] + [(tr('Custom'), 'Custom')], pr['board_theme'], self.set_board_theme)
        lay.addWidget(self.board_box)
        row = QHBoxLayout()
        lb = QPushButton(tr('Light squares…'))
        lb.clicked.connect(lambda: self.pick_color(True))
        db = QPushButton(tr('Dark squares…'))
        db.clicked.connect(lambda: self.pick_color(False))
        row.addWidget(lb)
        row.addWidget(db)
        lay.addLayout(row)
        lay.addWidget(QLabel(tr('Piece set')))
        self.piece_box = combo([(n, n) for n in self.app.piece_sets.names()], pr['piece_set'], self.set_piece_set)
        lay.addWidget(self.piece_box)
        self.preview = QLabel('')
        lay.addWidget(self.preview)
        lay.addWidget(muted_label(tr('Add your own piece set: create a folder in assets/piece_sets with wP.png … wK.png and bP.png … bK.png.')))
        lay.addStretch(1)
        self.update_preview()
        return self._scroll(w)

    def update_preview(self):
        pieces = self.app.pieces()
        size = 40
        out = QPixmap(size * 6, size * 2)
        out.fill(Qt.GlobalColor.transparent)
        p = QPainter(out)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        for r, color in enumerate((chess.WHITE, chess.BLACK)):
            for c, t in enumerate((chess.KING, chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN)):
                p.fillRect(c * size, r * size, size, size, QColor(self.app.light_color() if (r + c) % 2 == 0 else self.app.dark_color()))
                p.drawPixmap(c * size, r * size, pieces[(color, t)].scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        p.end()
        self.preview.setPixmap(out)

    def set_language(self, code):
        QTimer.singleShot(0, lambda: self.app.set_language(code))     # rebuilds the UI, so never from inside this widget's own signal

    def set_ui_theme(self, name):
        self.app.store.prefs['ui_theme'] = name
        self.app.store.save_prefs()
        self.app.apply_theme()

    def set_board_theme(self, name):
        pr = self.app.store.prefs
        pr['board_theme'] = name
        if name in BOARD_THEMES:
            pr['light_square'], pr['dark_square'] = BOARD_THEMES[name]
        self.app.store.save_prefs()
        self.app.apply_settings()
        self.update_preview()

    def pick_color(self, light):
        pr = self.app.store.prefs
        key = 'light_square' if light else 'dark_square'
        c = QColorDialog.getColor(QColor(pr[key]), self, tr('Choose square color'))
        if c.isValid():
            pr[key] = c.name()
            pr['board_theme'] = 'Custom'
            i = self.board_box.findData('Custom')
            self.loading = True
            self.board_box.setCurrentIndex(max(0, i))
            self.loading = False
            self.app.store.save_prefs()
            self.app.apply_settings()
            self.update_preview()

    def set_piece_set(self, name):
        self.app.store.prefs['piece_set'] = name
        self.app.store.save_prefs()
        self.app.apply_settings()
        self.update_preview()

    # ---- game
    def _game_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(10)
        pr = self.app.store.prefs

        def check(text, key):
            c = QCheckBox(text)
            c.setChecked(bool(pr.get(key, True)))
            c.toggled.connect(lambda on, k=key: self.set_pref(k, on))
            return c
        lay.addWidget(check(tr('Move sounds'), 'sound'))
        lay.addWidget(QLabel(tr('Sound pack')))
        self.pack_box = QComboBox()
        for name in SoundManager.packs():
            self.pack_box.addItem(name, name)
        i = self.pack_box.findData(pr.get('sound_pack', 'Default'))
        self.pack_box.setCurrentIndex(max(0, i))
        self.pack_box.currentIndexChanged.connect(lambda idx: self.set_pref('sound_pack', self.pack_box.currentData()))
        lay.addWidget(self.pack_box)
        lay.addWidget(muted_label(tr('Add your own sounds: put move.wav, capture.wav, check.wav … in a new folder inside assets/sounds.')))
        lay.addWidget(QLabel(tr('Volume')))
        vol = QSlider(Qt.Orientation.Horizontal)
        vol.setRange(0, 100)
        vol.setValue(int(pr.get('volume', 70)))
        vol.valueChanged.connect(lambda v: self.set_pref('volume', v))
        lay.addWidget(vol)
        lay.addWidget(check(tr('Piece animations'), 'animations'))
        lay.addWidget(check(tr('Show legal move dots'), 'show_legal_moves'))
        lay.addWidget(check(tr('Show board coordinates'), 'show_coordinates'))
        lay.addWidget(check(tr('Pass & Play: flip the board for each player'), 'auto_flip'))
        lay.addStretch(1)
        return self._scroll(w)

    def set_pref(self, key, value):
        if self.loading:
            return
        self.app.store.prefs[key] = value
        self.app.store.save_prefs()
        self.app.apply_settings()
        if key in ('sound_pack', 'volume'):
            self.app.sound.play('capture')

    # ---- engine
    def _engine_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(10)
        lay.addWidget(muted_label(tr('Stockfish powers the strong bots and the Game Review. It is found automatically in the "stockfish" '
                                     'folder next to the game. You can also pick the executable yourself.')))
        self.engine_label = QLabel('')
        self.engine_label.setWordWrap(True)
        self.engine_label.setStyleSheet('font-weight:bold;')
        lay.addWidget(self.engine_label)
        b = QPushButton(tr('Choose Stockfish executable…'))
        b.clicked.connect(self.choose_engine)
        lay.addWidget(b)
        lay.addStretch(1)
        self.update_engine_label()
        return w

    def update_engine_label(self):
        path = self.app.engine_path()
        self.engine_label.setText(tr('Stockfish: {path}').format(path=path) if path else tr('Stockfish not found: the built-in engine is used.'))

    def choose_engine(self):
        path, _ = QFileDialog.getOpenFileName(self, tr('Select Stockfish executable'), '', 'Executable (*.exe);;All files (*)')
        if path:
            self.app.set_engine_path(path)
            self.update_engine_label()

    def refresh(self):
        self.update_profile_view()
        self.update_engine_label()
