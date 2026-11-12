"""Bot roster (inspired by the chess.com bot ladder).

Avatars are looked up in assets/profiles/.  To use real pictures just replace
the PNG files (same name) - nothing else has to change.
"""
import os

# id, name, Elo, tier, avatar file (relative to assets/profiles), think time range (s), blurb
_ROWS = [
    ('zach',      'Zach',      100,  'Beginner',     'zach.png',          (0.5, 1.3), "Just learned how the pieces move. Mostly clicking and hoping."),
    ('martin',    'Martin',    250,  'Beginner',     'martin.png',        (0.6, 1.5), "Friendly beginner who loves to capture anything that looks free."),
    ('elani',     'Elani',     400,  'Beginner',     'bots/elani.png',    (0.6, 1.5), "Plays fast and happy. Forgets that you can capture back."),
    ('jimmy',     'Jimmy',     550,  'Beginner',     'bots/jimmy.png',    (0.6, 1.5), "Learned from videos. Great at the opening, lost after that."),
    ('nelson',    'Nelson',    700,  'Intermediate', 'bots/nelson.png',   (0.7, 1.6), "Careful and polite. Rarely hangs a queen anymore."),
    ('priya',     'Priya',     850,  'Intermediate', 'bots/priya.png',    (0.7, 1.7), "Loves attacking the king. Sometimes forgets her own."),
    ('antonio',   'Antonio',   1000, 'Intermediate', 'bots/antonio.png',  (0.8, 1.8), "Solid club player. Sets small traps and spots simple tactics."),
    ('wayne',     'Wayne',     1200, 'Intermediate', 'bots/wayne.png',    (0.8, 1.8), "Patient and positional. Slowly squeezes you."),
    ('isabel',    'Isabel',    1400, 'Advanced',     'bots/isabel.png',   (0.9, 2.0), "Tournament regular. Punishes every loose piece."),
    ('emir',      'Emir',      1600, 'Advanced',     'bots/emir.png',     (0.9, 2.0), "Tactical and sharp. Always looking for a combination."),
    ('sofia',     'Sofia',     1800, 'Advanced',     'bots/sofia.png',    (1.0, 2.2), "Strong endgames and very few mistakes."),
    ('arjun',     'Arjun',     2000, 'Master',       'bots/arjun.png',    (1.0, 2.2), "Candidate-master strength. Calculates deep lines."),
    ('olivia',    'Olivia',    2200, 'Master',       'bots/olivia.png',   (1.0, 2.3), "Fearless attacker with a perfect memory for theory."),
    ('viktor',    'Viktor',    2500, 'Master',       'bots/viktor.png',   (1.0, 2.4), "Grandmaster-level grinder. Do not expect gifts."),
    ('stockfish', 'Stockfish', 3190, 'Engine',       'stockfish.webp',    (0.6, 1.2), "The strongest engine in the world. Pick a level and good luck."),
]

TIERS = ['Beginner', 'Intermediate', 'Advanced', 'Master', 'Coach', 'Engine']
STOCKFISH_LEVELS = [('Easy', 1350), ('Medium', 2000), ('Hard', 2800), ('Maximum', 3190)]


class Bot:
    def __init__(self, bid, name, elo, tier, avatar, think, blurb):
        self.id = bid
        self.name = name
        self.elo = elo
        self.tier = tier
        self.avatar = avatar
        self.think = think
        self.blurb = blurb
        self.is_engine = (bid == 'stockfish')

    def avatar_path(self, assets_dir):
        return os.path.join(assets_dir, 'profiles', self.avatar.replace('/', os.sep))


BOTS = [Bot(*row) for row in _ROWS]
# every coach can also be played as a bot (strength = the coach's Elo)
from coaches import COACHES
_stockfish = BOTS.pop()          # keep Stockfish last
for _c in COACHES:
    BOTS.append(Bot('coach_' + _c.id, _c.name, _c.elo, 'Coach', _c.avatar, _c.think,
                    "Your coach, ready for a game. Plays at about %d Elo." % _c.elo))
BOTS.append(_stockfish)
_BY_ID = {b.id: b for b in BOTS}


def bot_by_id(bid):
    return _BY_ID.get(bid) or BOTS[1]
