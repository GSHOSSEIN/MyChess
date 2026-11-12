"""Small JSON based storage for My Chess (profile, friends, history, preferences)."""
import json
import os
import sys
import time
import uuid

APP_NAME = 'MyChess'


def data_dir():
    if os.name == 'nt':
        base = os.environ.get('APPDATA') or os.path.expanduser('~')
    elif sys.platform == 'darwin':
        base = os.path.expanduser('~/Library/Application Support')
    else:
        base = os.environ.get('XDG_DATA_HOME') or os.path.expanduser('~/.local/share')
    path = os.path.join(base, APP_NAME)
    os.makedirs(os.path.join(path, 'avatars'), exist_ok=True)
    return path


DATA = data_dir()
MAX_HISTORY = 300

DEFAULT_PREFS = {
    'language': 'en',
    'ui_theme': 'Chess.com Dark',
    'board_theme': 'Green',
    'light_square': '#EEEED2',
    'dark_square': '#769656',
    'piece_set': 'Classic',
    'sound': True,
    'sound_pack': 'Your sounds',
    'coach': 'levy',
    'coach_live': True,
    'auto_flip': True,
    'volume': 70,
    'animations': True,
    'show_legal_moves': True,
    'show_coordinates': True,
    'time_control': '10 min',
    'stockfish_path': '',
    'last_host_port': 8765,
}

DEFAULT_PROFILE = {
    'id': '',
    'username': 'Player',
    'rating': 800,
    'avatar': 'avatar_01',      # preset id, or 'custom'
    'games': 0,
}


def _path(name):
    return os.path.join(DATA, name + '.json')


def load_json(name, default):
    try:
        with open(_path(name), 'r', encoding='utf-8') as f:
            value = json.load(f)
        if isinstance(default, dict) and isinstance(value, dict):
            merged = dict(default)
            merged.update(value)
            return merged
        return value
    except (OSError, ValueError):
        return json.loads(json.dumps(default))


def save_json(name, value):
    tmp = _path(name) + '.tmp'
    try:
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(value, f, ensure_ascii=False, indent=1)
        os.replace(tmp, _path(name))
    except OSError:
        pass


class Store:
    def __init__(self):
        self.prefs = load_json('prefs', DEFAULT_PREFS)
        self.profile = load_json('profile', DEFAULT_PROFILE)
        self.friends = load_json('friends', [])
        self.history = load_json('history', [])
        if not isinstance(self.friends, list):
            self.friends = []
        if not isinstance(self.history, list):
            self.history = []
        if not self.profile.get('id'):
            self.profile['id'] = uuid.uuid4().hex
            self.save_profile()

    # ---- saving
    def save_prefs(self):
        save_json('prefs', self.prefs)

    def save_profile(self):
        save_json('profile', self.profile)

    def save_friends(self):
        save_json('friends', self.friends)

    def save_history(self):
        save_json('history', self.history[-MAX_HISTORY:])

    # ---- avatars
    def custom_avatar_path(self):
        return os.path.join(DATA, 'avatars', 'me.png')

    def friend_avatar_path(self, fid):
        return os.path.join(DATA, 'avatars', 'friend_' + ''.join(c for c in fid if c.isalnum()) + '.png')

    # ---- friends
    def find_friend(self, fid):
        for f in self.friends:
            if f.get('id') == fid:
                return f
        return None

    def add_friend(self, fid, name, rating, host='', port=8765, avatar_png=None):
        if not fid or fid == self.profile.get('id'):
            return False
        f = self.find_friend(fid)
        if f is None:
            f = {'id': fid, 'added': time.time()}
            self.friends.append(f)
        f.update({'name': name, 'rating': rating, 'host': host, 'port': port})
        if avatar_png:
            try:
                with open(self.friend_avatar_path(fid), 'wb') as fh:
                    fh.write(avatar_png)
            except OSError:
                pass
        self.save_friends()
        return True

    def remove_friend(self, fid):
        self.friends = [f for f in self.friends if f.get('id') != fid]
        self.save_friends()
        try:
            os.remove(self.friend_avatar_path(fid))
        except OSError:
            pass

    # ---- history
    def add_history(self, entry):
        entry = dict(entry)
        entry.setdefault('id', uuid.uuid4().hex)
        entry.setdefault('date', time.time())
        self.history.append(entry)
        self.save_history()
        return entry

    def delete_history(self, entry_id):
        self.history = [h for h in self.history if h.get('id') != entry_id]
        self.save_history()

    def head_to_head(self, opponent_id=None, name=None):
        wins = draws = losses = 0
        for h in self.history:
            opp = h.get('opponent', {})
            if (opponent_id and opp.get('id') == opponent_id) or (name and opp.get('name') == name):
                r = h.get('outcome')
                if r == 'win':
                    wins += 1
                elif r == 'draw':
                    draws += 1
                elif r == 'loss':
                    losses += 1
        return wins, draws, losses


def expected_score(me, opp):
    return 1.0 / (1.0 + 10 ** ((opp - me) / 400.0))


def elo_change(me, opp, score, games_played=0):
    """score: 1 win, 0.5 draw, 0 loss.  Bigger steps for the first games."""
    k = 40 if games_played < 10 else 24 if me < 2000 else 16
    return int(round(k * (score - expected_score(me, opp))))
