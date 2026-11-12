import base64
import os
import queue
import random
import sys
import time
import traceback

import chess
import chess.pgn
from PySide6.QtCore import Qt, QTimer, QBuffer, QIODevice, QSettings
from PySide6.QtGui import QPixmap, QIcon, QColor, QPalette
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel,
                               QPushButton, QStackedWidget, QMessageBox, QFileDialog)

import coaches
import i18n
import lan as lanmod
import store as storemod
import widgets
from engines import UciEngine, find_stockfish
from game import GamePage, time_control_by_name
from i18n import tr
from bots import bot_by_id
from editor_page import EditorPage
from learn_page import LessonPage
from pages import HomePage, BotsPage, LanPage, FriendsPage, HistoryPage, SettingsPage, ClickFrame
from puzzle_page import PuzzlePage
from review_page import ReviewPage
from rules import RuleSet
from themes import UI_THEMES, build_stylesheet
from widgets import SoundManager, PieceSets, AvatarLabel, round_pixmap, fallback_avatar, ASSETS

ROOT = os.path.dirname(os.path.abspath(__file__))
NAV = [('home', '♟', 'Play'), ('bots', '🤖', 'Bots'), ('puzzles', '🧩', 'Puzzles'), ('learn', '🎓', 'Learn'),
       ('positions', '📐', 'Positions'), ('lan', '🌐', 'LAN'), ('friends', '👥', 'Friends'),
       ('history', '📜', 'History'), ('settings', '⚙', 'Settings')]
MENU_PAGES = ('home', 'bots', 'puzzles', 'learn', 'positions', 'lan', 'friends', 'history', 'settings')
TRAINER_PAGES = ('game', 'review', 'learn', 'puzzles', 'positions')


class ChessApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('My Chess')
        self.resize(1320, 880)
        self.setMinimumSize(1060, 720)
        icon = os.path.join(ROOT, 'chess.ico')
        if os.path.exists(icon):
            self.setWindowIcon(QIcon(icon))
        first_run = not os.path.exists(os.path.join(storemod.DATA, 'profile.json'))
        self.store = storemod.Store()
        if first_run:
            self._import_legacy_settings()
        i18n.set_language(self.store.prefs.get('language', 'en'))
        if not self.store.prefs.get('sounds_v3'):                      # one-time: switch to the supplied sound pack
            if os.path.isdir(os.path.join(ASSETS, 'sounds', 'Your sounds')):
                self.store.prefs['sound_pack'] = 'Your sounds'
            self.store.prefs['sounds_v3'] = True
            self.store.save_prefs()
        self.piece_sets = PieceSets()
        self.sound = SoundManager(self.store.prefs.get('sound_pack', 'Default'))
        self.sound.enabled = bool(self.store.prefs.get('sound', True))
        self.sound.set_volume(int(self.store.prefs.get('volume', 70)))
        # services
        self._uci = None
        self._engine_path = find_stockfish(self.store.prefs.get('stockfish_path', ''))
        self._my_pix = None
        self._avatar_cache = {}
        self._coach_pix = {}
        self.lan = None
        self.peer = None
        self.lan_cfg = None
        self.discovered = {}
        self.disc_events = queue.Queue()
        self.discovery = lanmod.Discovery(self.disc_events)
        self.discovery.start()
        self.review_return = 'home'
        self.current_page = 'home'
        self.build_ui()
        self.apply_theme()
        self.event_timer = QTimer(self)
        self.event_timer.timeout.connect(self.poll_events)
        self.event_timer.start(60)

    def _import_legacy_settings(self):
        """Pick up the name / rating from the old version of the game once."""
        try:
            old = QSettings('MyChess', 'MyChessApp')
            name = old.value('player_name', '')
            if name:
                self.store.profile['username'] = str(name)[:20]
                self.store.profile['rating'] = int(old.value('player_rating', 800))
                self.store.save_profile()
        except Exception:
            pass

    # ------------------------------------------------------------------ UI
    def build_ui(self):
        central = QWidget()
        central.setObjectName('pageRoot')
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        nav = QFrame()
        nav.setObjectName('nav')
        nav.setFixedWidth(210)
        nl = QVBoxLayout(nav)
        nl.setContentsMargins(12, 16, 12, 12)
        nl.setSpacing(4)
        logo = QLabel('♞ MY CHESS')
        logo.setStyleSheet('font-size:22px;font-weight:900;padding:4px 8px 16px 8px;color:%s;' % widgets.THEME['accent'])
        nl.addWidget(logo)
        self.nav_buttons = {}
        for key, icon, label in NAV:
            b = QPushButton('%s   %s' % (icon, tr(label)))
            b.setObjectName('navButton')
            b.clicked.connect(lambda checked=False, k=key: self.show_page(k))
            nl.addWidget(b)
            self.nav_buttons[key] = b
        nl.addStretch(1)
        self.profile_card = ClickFrame()
        self.profile_card.setObjectName('card')
        pc = QHBoxLayout(self.profile_card)
        pc.setContentsMargins(8, 8, 8, 8)
        self.nav_avatar = AvatarLabel(40)
        pc.addWidget(self.nav_avatar)
        col = QVBoxLayout()
        col.setSpacing(0)
        self.nav_name = QLabel('')
        self.nav_name.setStyleSheet('font-weight:bold;')
        self.nav_elo = QLabel('')
        self.nav_elo.setObjectName('muted')
        col.addWidget(self.nav_name)
        col.addWidget(self.nav_elo)
        pc.addLayout(col, 1)
        self.profile_card.clicked.connect(lambda: self.show_page('settings'))
        nl.addWidget(self.profile_card)
        root.addWidget(nav)
        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)
        self.pages = {}
        for key, cls in (('home', HomePage), ('bots', BotsPage), ('lan', LanPage), ('friends', FriendsPage),
                         ('history', HistoryPage), ('settings', SettingsPage), ('game', GamePage), ('review', ReviewPage),
                         ('puzzles', PuzzlePage), ('learn', LessonPage), ('positions', EditorPage)):
            self.pages[key] = cls(self)
            self.stack.addWidget(self.pages[key])
        self.setCentralWidget(central)
        self.show_page(self.current_page if self.current_page in self.pages else 'home')

    def rebuild_ui(self):
        if self.current_page in ('game', 'review'):
            self.current_page = 'home'
        self.build_ui()
        self.apply_theme()

    def _mark_nav(self, name):
        for key, b in self.nav_buttons.items():
            b.setObjectName('navButtonActive' if key == name else 'navButton')
            b.style().unpolish(b)
            b.style().polish(b)

    def show_page(self, name):
        self.current_page = name
        self.stack.setCurrentWidget(self.pages[name])
        self._mark_nav(name)
        self.update_nav_profile()
        if name in MENU_PAGES:
            self.pages[name].refresh()

    def update_nav_profile(self):
        p = self.store.profile
        self.nav_avatar.set_avatar(self.my_pixmap(), p['username'][:1])
        self.nav_name.setText(p['username'])
        self.nav_elo.setText('%d Elo' % p['rating'])

    def refresh_pages(self):
        self.update_nav_profile()
        if self.current_page in MENU_PAGES:
            self.pages[self.current_page].refresh()

    # ------------------------------------------------------------ appearance
    def apply_theme(self):
        name = self.store.prefs.get('ui_theme', 'Chess.com Dark')
        t = UI_THEMES.get(name, UI_THEMES['Chess.com Dark'])
        widgets.set_theme(dict(t))
        self.apply_palette(t)
        self.setStyleSheet(build_stylesheet(t))
        self.apply_settings()

    def apply_palette(self, t):
        """Give EVERY widget (scroll areas, tab pages, dialogs, message boxes, popups) the theme colours,
        not only the ones the stylesheet names - this fixes unreadable text in some menus."""
        app = QApplication.instance()
        if app.style().objectName().lower() != 'fusion':
            app.setStyle('Fusion')
        pal = QPalette()
        c = QColor
        pal.setColor(QPalette.ColorRole.Window, c(t['bg']))
        pal.setColor(QPalette.ColorRole.WindowText, c(t['text']))
        pal.setColor(QPalette.ColorRole.Base, c(t['panel']))
        pal.setColor(QPalette.ColorRole.AlternateBase, c(t['panel2']))
        pal.setColor(QPalette.ColorRole.Text, c(t['text']))
        pal.setColor(QPalette.ColorRole.Button, c(t['panel2']))
        pal.setColor(QPalette.ColorRole.ButtonText, c(t['text']))
        pal.setColor(QPalette.ColorRole.BrightText, c('#ffffff'))
        pal.setColor(QPalette.ColorRole.ToolTipBase, c(t['panel']))
        pal.setColor(QPalette.ColorRole.ToolTipText, c(t['text']))
        pal.setColor(QPalette.ColorRole.Highlight, c(t['accent']))
        pal.setColor(QPalette.ColorRole.HighlightedText, c('#ffffff'))
        pal.setColor(QPalette.ColorRole.PlaceholderText, c(t['muted']))
        pal.setColor(QPalette.ColorRole.Link, c(t['accent']))
        for role in (QPalette.ColorRole.WindowText, QPalette.ColorRole.Text, QPalette.ColorRole.ButtonText):
            pal.setColor(QPalette.ColorGroup.Disabled, role, c(t['muted']))
        app.setPalette(pal)

    def apply_settings(self):
        pr = self.store.prefs
        self.sound.load_pack(pr.get('sound_pack', 'Default'))
        self.sound.enabled = bool(pr.get('sound', True))
        self.sound.set_volume(int(pr.get('volume', 70)))
        self.pages['game'].apply_prefs()
        boards = [self.pages['home'].preview] + [self.pages[k].bw for k in TRAINER_PAGES if k != 'game']
        for bw in boards:
            bw.light, bw.dark = self.light_color(), self.dark_color()
            bw.show_coords = pr.get('show_coordinates', True)
            bw.clear_cache()
        self.pages['positions'].refresh()

    def set_language(self, code):
        self.store.prefs['language'] = code
        self.store.save_prefs()
        game = self.pages['game']
        if game.board.move_stack and not game.finished:
            QMessageBox.information(self, 'My Chess',
                                    'The language will change after you finish the current game and restart My Chess.')
            return
        i18n.set_language(code)
        self.rebuild_ui()
        self.show_page('settings')

    def pieces(self):
        return self.piece_sets.load(self.store.prefs.get('piece_set', 'Classic'))

    def light_color(self):
        return QColor(self.store.prefs.get('light_square', '#EEEED2'))

    def dark_color(self):
        return QColor(self.store.prefs.get('dark_square', '#769656'))

    # --------------------------------------------------------------- avatars
    def my_pixmap(self):
        if self._my_pix is None:
            p = self.store.profile
            if p.get('avatar') == 'custom':
                path = self.store.custom_avatar_path()
            else:
                path = os.path.join(ASSETS, 'profiles', 'avatars', '%s.png' % p.get('avatar', 'avatar_01'))
            pix = QPixmap(path)
            self._my_pix = pix if not pix.isNull() else fallback_avatar(p['username'][:1], 256)
        return self._my_pix

    def invalidate_avatar(self):
        self._my_pix = None

    def bot_pixmap(self, bot):
        if bot.id not in self._avatar_cache:
            pix = QPixmap(bot.avatar_path(ASSETS))
            self._avatar_cache[bot.id] = pix if not pix.isNull() else fallback_avatar(bot.name[:1], 256)
        return self._avatar_cache[bot.id]

    def friend_pixmap(self, friend):
        if not friend:
            return None
        pix = QPixmap(self.store.friend_avatar_path(friend.get('id', '')))
        return pix if not pix.isNull() else fallback_avatar(friend.get('name', '?')[:1], 256)

    def coach(self):
        return coaches.coach_by_id(self.store.prefs.get('coach', 'levy'))

    def coach_pixmap(self, coach=None):
        coach = coach or self.coach()
        if coach.id not in self._coach_pix:
            pix = QPixmap(os.path.join(ASSETS, 'profiles', coach.avatar.replace('/', os.sep)))
            self._coach_pix[coach.id] = pix if not pix.isNull() else fallback_avatar(coach.name[:1], 256)
        return self._coach_pix[coach.id]

    def round_icon(self, pix, size, letter='?'):
        if pix is None or pix.isNull():
            return fallback_avatar(letter, size)
        return round_pixmap(pix, size)

    def avatar_b64(self):
        pix = self.my_pixmap().scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        buf = QBuffer()
        buf.open(QIODevice.OpenModeFlag.WriteOnly)
        pix.save(buf, 'PNG')
        return base64.b64encode(bytes(buf.data())).decode('ascii')

    # ---------------------------------------------------------------- engine
    def engine_path(self):
        return self._engine_path

    def set_engine_path(self, path):
        self.store.prefs['stockfish_path'] = path
        self.store.save_prefs()
        self.close_engine()
        self._engine_path = find_stockfish(path)

    def get_engine(self):
        if self._uci is not None and self._uci.engine is not None:
            return self._uci
        if not self._engine_path:
            return None
        try:
            self._uci = UciEngine(self._engine_path).start()
        except Exception:
            self._uci = None
            self._engine_path = ''
        return self._uci

    def close_engine(self):
        if self._uci is not None:
            self._uci.quit()
            self._uci = None

    # ----------------------------------------------------------- start games
    def me_info(self):
        p = self.store.profile
        return {'name': p['username'], 'rating': p['rating'], 'pix': self.my_pixmap(), 'id': p['id']}

    def odds_fen(self, odds, my_color):
        """Starting FEN with one piece removed ('bot:Q' = the bot starts without its queen, 'me:R' = I start without a rook)."""
        if not odds or odds == 'std':
            return None
        who, piece = odds.split(':')
        color = (not my_color) if who == 'bot' else my_color
        board = chess.Board()
        file_of = {'Q': 3, 'R': 0, 'B': 2, 'N': 1}[piece]
        board.remove_piece_at(chess.square(file_of, 0 if color == chess.WHITE else 7))
        board.castling_rights = board.clean_castling_rights()
        return board.fen()

    def start_bot_game(self, bot, elo, side, tc_name, odds='std', fen=None):
        self.lan_cancel(silent=True)
        color = {'white': chess.WHITE, 'black': chess.BLACK}.get(side) 
        if color is None:
            color = random.choice([chess.WHITE, chess.BLACK])
        me = self.me_info()
        opp = {'name': bot.name, 'rating': elo, 'pix': self.bot_pixmap(bot), 'id': ''}
        white, black = (me, opp) if color == chess.WHITE else (opp, me)
        self.show_page('game')
        self.pages['game'].start_game('bot', white, black, color, time_control_by_name(tc_name), bot=bot, bot_elo=elo,
                                      start_fen=fen or self.odds_fen(odds, color))

    def start_local_game(self, tc_name, start_fen=None):
        self.lan_cancel(silent=True)
        white = {'name': self.store.profile['username'], 'rating': None, 'pix': self.my_pixmap(), 'id': ''}
        black = {'name': tr('Player 2'), 'rating': None, 'pix': None, 'id': ''}
        self.show_page('game')
        self.pages['game'].start_game('local', white, black, chess.WHITE, time_control_by_name(tc_name), start_fen=start_fen)

    def start_custom_position(self, fen, opponent, side):
        """Play a position from the position editor against a bot ('local' = pass & play)."""
        if opponent == 'local':
            self.start_local_game('No limit', start_fen=fen)
            return
        bot = bot_by_id(opponent)
        self.start_bot_game(bot, bot.elo, side, 'No limit', fen=fen)

    def go_play_again(self):
        mode = self.pages['game'].mode
        if mode == 'lan':
            self.lan_cancel(silent=True)
            self.show_page('lan')
        elif mode == 'bot':
            self.show_page('bots')
        else:
            self.show_page('home')

    def on_game_finished(self, entry):
        self.update_nav_profile()

    # ------------------------------------------------------------------ review
    def open_review(self, entry):
        if entry.get('rules_used'):
            QMessageBox.information(self, tr('Game Review'), tr('Game review needs standard chess rules.'))
            return
        if self.current_page != 'review':
            self.review_return = self.current_page
        self.pages['review'].load(entry)
        self.stack.setCurrentWidget(self.pages['review'])
        self.current_page = 'review'
        self._mark_nav('')

    def go_back_from_review(self):
        self.pages['review'].cancel()
        back = self.review_return if self.review_return in self.pages and self.review_return != 'review' else 'home'
        self.show_page(back)

    def review_pgn_file(self):
        path, _ = QFileDialog.getOpenFileName(self, tr('Open PGN'), '', 'PGN (*.pgn);;All files (*)')
        if not path:
            return
        try:
            with open(path, encoding='utf-8', errors='replace') as f:
                game = chess.pgn.read_game(f)
            if game is None:
                raise ValueError(tr('No game found in that file.'))
            board = game.board()
            moves = [m.uci() for m in game.mainline_moves()]
            if not moves:
                raise ValueError(tr('That game has no moves.'))
            h = game.headers
            entry = {'moves': moves, 'start_fen': board.fen(), 'white': h.get('White', tr('White')),
                     'black': h.get('Black', tr('Black')), 'white_elo': _int_or_none(h.get('WhiteElo')),
                     'black_elo': _int_or_none(h.get('BlackElo')), 'color': 'white', 'result': h.get('Result', '*')}
        except Exception as e:
            QMessageBox.warning(self, tr('Open PGN'), str(e))
            return
        self.open_review(entry)

    # ------------------------------------------------------------------- LAN
    def hello_message(self):
        p = self.store.profile
        return {'t': 'hello', 'id': p['id'], 'name': p['username'], 'rating': p['rating'], 'avatar': self.avatar_b64(),
                'port': int(self.store.prefs.get('last_host_port', lanmod.DEFAULT_PORT)), 'ver': lanmod.PROTOCOL}

    def host_lan(self, port, tc_name, side):
        self.lan_cancel(silent=True)
        session = lanmod.LanSession()
        p = self.store.profile
        try:
            session.host(port, {'name': p['username'], 'rating': p['rating'], 'id': p['id'], 'tc': tc_name})
        except OSError as e:
            QMessageBox.warning(self, tr('LAN'), tr('Could not start hosting: {err}').format(err=e))
            return
        self.lan, self.peer = session, None
        self.lan_cfg = {'tc': tc_name, 'side': side}
        ip = lanmod.get_lan_ip() or '?'
        self.pages['lan'].set_hosting(True, tr('Waiting for a player to join…  {ip}:{port}').format(ip=ip, port=port))

    def join_lan(self, host, port):
        self.lan_cancel(silent=True)
        session = lanmod.LanSession()
        session.join(host, port)
        self.lan, self.peer, self.lan_cfg = session, None, None
        text = tr('Connecting to {host}:{port}…').format(host=host, port=port)
        self.pages['lan'].set_hosting(False, text)
        self.statusBar().showMessage(text, 6000)

    def lan_cancel(self, silent=False):
        if self.lan is not None:
            self.lan.close(notify_peer=True)
            self.lan = None
        self.peer = None
        self.lan_cfg = None
        if 'lan' in self.pages:
            self.pages['lan'].set_hosting(False, '')
        if not silent:
            self.statusBar().showMessage(tr('LAN stopped.'), 3000)

    def poll_events(self):
        while True:
            try:
                kind, data = self.disc_events.get_nowait()
            except queue.Empty:
                break
            if kind == 'found':
                self.discovered[(data['host'], data['port'])] = data
        for key in [k for k, v in self.discovered.items() if time.monotonic() - v['seen'] > 30]:
            del self.discovered[key]
        lan = self.lan
        if lan is None:
            return
        while lan is self.lan:
            try:
                item = lan.events.get_nowait()
            except queue.Empty:
                break
            kind = item[0]
            data = item[1] if len(item) > 1 else None
            if kind == 'connected':
                lan.send(self.hello_message())
                self.pages['lan'].set_hosting(False, tr('Connected. Setting up the game…'))
            elif kind == 'msg':
                self.on_lan_message(lan, data)
            elif kind == 'closed':
                game = self.pages['game']
                if game.mode == 'lan':
                    game.lan_closed(data)
                self.statusBar().showMessage(tr(data), 6000)
                self.pages['lan'].set_hosting(False, tr(data))
                self.lan = None
            elif kind == 'error':
                QMessageBox.warning(self, tr('LAN'), str(data))
                self.pages['lan'].set_hosting(False, '')
                self.lan = None

    def on_lan_message(self, lan, msg):
        t = msg.get('t')
        if t == 'hello':
            rating = msg.get('rating')
            self.peer = {'id': str(msg.get('id', '')), 'name': str(msg.get('name', 'Player'))[:20],
                         'rating': rating if isinstance(rating, int) else 800,
                         'port': msg.get('port', lanmod.DEFAULT_PORT), 'avatar': msg.get('avatar', '')}
            if lan.role == 'host' and self.lan_cfg:
                side = self.lan_cfg['side']
                host_white = (random.random() < 0.5) if side == 'random' else (side == 'white')
                tc = time_control_by_name(self.lan_cfg['tc'])
                lan.send({'t': 'start', 'host_white': host_white, 'tc': list(tc), 'rules': None})
                self.begin_lan_game(lan, host_white, tc, None)
        elif t == 'start' and lan.role == 'client' and self.peer:
            try:
                tc = (int(msg['tc'][0]), int(msg['tc'][1]))
            except (KeyError, IndexError, TypeError, ValueError):
                tc = (600, 0)
            self.begin_lan_game(lan, bool(msg.get('host_white', True)), tc, msg.get('rules'))
        elif t == 'friend_req' and self.peer:
            ask = QMessageBox.question(self, tr('Friends'),
                                       tr('{name} wants to add you as a friend. Accept?').format(name=self.peer['name']))
            if ask == QMessageBox.StandardButton.Yes:
                self.save_peer_as_friend(lan)
                lan.send({'t': 'friend_ok'})
        elif t == 'friend_ok' and self.peer:
            self.save_peer_as_friend(lan)
        else:
            game = self.pages['game']
            if game.mode == 'lan':
                game.lan_message(msg)

    def save_peer_as_friend(self, lan):
        peer = self.peer
        png = None
        try:
            if peer.get('avatar'):
                png = base64.b64decode(peer['avatar'])
                if len(png) > 300000:
                    png = None
        except ValueError:
            png = None
        self.store.add_friend(peer['id'], peer['name'], peer['rating'], host=lan.peer_ip,
                              port=peer.get('port', lanmod.DEFAULT_PORT), avatar_png=png)
        self.statusBar().showMessage(tr('{name} is now your friend.').format(name=peer['name']), 5000)
        self.pages['game'].refresh()

    def begin_lan_game(self, lan, host_white, tc, rules_json):
        peer = self.peer
        pix = QPixmap()
        if peer.get('avatar'):
            try:
                pix.loadFromData(base64.b64decode(peer['avatar']))
            except ValueError:
                pix = QPixmap()
        opp = {'name': peer['name'], 'rating': peer['rating'], 'pix': pix if not pix.isNull() else None, 'id': peer['id']}
        me = self.me_info()
        i_am_white = (lan.role == 'host') == bool(host_white)
        white, black = (me, opp) if i_am_white else (opp, me)
        rules = None
        if rules_json:
            rules = RuleSet()
            rules.load_json(rules_json)
        self.pages['lan'].set_hosting(False, '')
        self.show_page('game')
        self.pages['game'].start_game('lan', white, black, chess.WHITE if i_am_white else chess.BLACK, tuple(tc),
                                      lan=lan, rules=rules)

    # ------------------------------------------------------------------ close
    def closeEvent(self, event):
        try:
            self.pages['game'].stop()
            self.lan_cancel(silent=True)
            self.discovery.stop()
            self.close_engine()
        finally:
            event.accept()


def _int_or_none(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('My Chess')

    def hook(exc_type, exc, tb):
        text = ''.join(traceback.format_exception(exc_type, exc, tb))
        try:
            with open(os.path.join(storemod.DATA, 'error.log'), 'a', encoding='utf-8') as f:
                f.write(time.strftime('%Y-%m-%d %H:%M:%S\n') + text + '\n')
        except OSError:
            pass
        sys.__excepthook__(exc_type, exc, tb)
        try:
            QMessageBox(QMessageBox.Icon.Critical, 'My Chess',
                        'Something went wrong (details saved to error.log):\n\n' + text[-1200:]).exec()
        except Exception:
            pass
    sys.excepthook = hook
    w = ChessApp()
    w.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
