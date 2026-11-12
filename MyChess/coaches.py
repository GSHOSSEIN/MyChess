"""Coaches: pictures + teaching tone.  Every coach can also be played against as a bot (see bots.py).
The comments are generic coaching lines (they are NOT quotes from the real people).  The playing strengths
are rough estimates - change `elo` below if you want a coach stronger or weaker."""
import datetime
import random


class Coach:
    def __init__(self, cid, name, avatar, tone, blurb, elo, think=(0.8, 1.8)):
        self.id, self.name, self.avatar, self.tone, self.blurb, self.elo, self.think = cid, name, avatar, tone, blurb, elo, think


COACHES = [
    Coach('levy', 'Levy', 'coaches/levy.png', 'playful', 'Upbeat and energetic coach who makes every lesson fun.', 2400),
    Coach('magnus', 'Magnus', 'coaches/magnus.png', 'direct', 'Calm, precise coach. Short comments, no fluff.', 2830, (1.0, 2.2)),
    Coach('hikaru', 'Hikaru', 'coaches/hikaru.png', 'direct', 'Fast, confident coach who loves tactics and speed.', 2790, (0.6, 1.4)),
    Coach('botez', 'Botez Sisters', 'coaches/botez.png', 'warm', 'Friendly duo who cheer you on and explain the ideas.', 2000),
    Coach('david', 'David', 'coaches/david.png', 'warm', 'Patient teacher: explains the plan behind every move.', 1500),
    Coach('drwolf', 'Dr. Wolf', 'coaches/drwolf.png', 'wise', 'The wise old professor. Solid advice and classic principles.', 1000),
    Coach('mittens', 'Mittens', 'coaches/mittens.png', 'cat', 'A very serious cat. Purrs when you play well.', 600, (0.5, 1.3)),
]
_BY_ID = {c.id: c for c in COACHES}


def coach_by_id(cid):
    return _BY_ID.get(cid) or COACHES[0]


TONES = {
    'warm': {
        'hello': ["Hi! I'm your coach. Let's play some good chess together.", "Welcome back! Ready to improve today?"],
        'great': ["Beautiful move!", "Yes, that's exactly the idea!", "Excellent work!"],
        'good': ["Nice one.", "Good thinking.", "That works well."],
        'bad': ["Let's look at that one again.", "Careful here.", "Not the best, but we can learn from it."],
        'blunder': ["Oh no, that one hurts. Don't worry, it happens to everyone.", "That's a big slip. Take a breath and keep going."],
        'puzzle_ok': ["You got it! Great job.", "Solved! Lovely."],
        'puzzle_bad': ["Not quite. Look at the checks first.", "Close! Try another idea."],
        'lesson_ok': ["Perfect!", "Exactly right!"],
        'lesson_bad': ["Almost! Try again.", "Not that one. Look at the hint."],
    },
    'direct': {
        'hello': ["Let's get to work.", "Focus. Play your best moves."],
        'great': ["Strong move.", "Correct. Precisely played.", "That is the best idea."],
        'good': ["Fine.", "Acceptable move.", "Solid."],
        'bad': ["That gives away part of your advantage.", "There was something better.", "Inaccurate."],
        'blunder': ["That is a serious mistake.", "That loses material or the game. Be careful."],
        'puzzle_ok': ["Correct.", "Solved."],
        'puzzle_bad': ["Wrong. Check all the forcing moves.", "No. Look again."],
        'lesson_ok': ["Correct.", "Right."],
        'lesson_bad': ["Wrong. Try again.", "Not that. Read the instruction."],
    },
    'playful': {
        'hello': ["Let's goooo! Time to learn some chess!", "Ready? Let's have some fun with the pieces!"],
        'great': ["WOW! That's a great move!", "Chef's kiss. Beautiful!", "Yes! That is how it's done!"],
        'good': ["Nice, nice, nice.", "Good one!", "I like that."],
        'bad': ["Hmm, I'm not sure about that one...", "Ooh, careful with that!", "That's a bit loose."],
        'blunder': ["Oh no no no no. That's a blunder!", "Yikes! That one hurts!"],
        'puzzle_ok': ["BOOM! Solved it!", "Nailed it!"],
        'puzzle_bad': ["Ooh, not quite! Try again!", "Nope! Look for the check!"],
        'lesson_ok': ["Yes! Perfect!", "Nailed it!"],
        'lesson_bad': ["Oops, not that one. Try again!", "Almost! Give it another shot."],
    },
    'wise': {
        'hello': ["Welcome, my student. Let us study the board.", "Patience and principles win games."],
        'great': ["Wisely played.", "A master's move.", "You are learning well."],
        'good': ["A sound move.", "That follows the principles.", "Good."],
        'bad': ["Hmm. Remember the principles of development and safety.", "A hasty move. Think again.", "There was a better way."],
        'blunder': ["Alas, a grave error. Even masters fall; learn from it.", "A costly slip, my friend."],
        'puzzle_ok': ["Well solved.", "You see clearly now."],
        'puzzle_bad': ["No. Look for forcing moves: checks, captures, threats.", "Think again, my student."],
        'lesson_ok': ["Correct. Well done.", "Yes. That is the way."],
        'lesson_bad': ["Not so. Read the hint again.", "Look more carefully."],
    },
    'cat': {
        'hello': ["Meow. Let's play chess.", "Purr... I mean, hello! Let's begin."],
        'great': ["Purrrr! Excellent move!", "Meow! That was great!"],
        'good': ["Mrrp. Good move.", "Nice. *purrs*"],
        'bad': ["Hmm... *tilts head*", "Meow? Are you sure about that?"],
        'blunder': ["MEOW! That's a blunder!", "*knocks piece off the table* Nooo!"],
        'puzzle_ok': ["Purrfect! Solved!", "Meow! You did it!"],
        'puzzle_bad': ["Mrow... not quite. Try again.", "*stares* Look for the check."],
        'lesson_ok': ["Purrfect!", "Meow! Correct!"],
        'lesson_bad': ["Mrow. Not that one.", "Try again, human."],
    },
}

GOOD_LABELS = ('best', 'excellent', 'good', 'book', 'forced')
GREAT_LABELS = ('brilliant', 'great')
BAD_LABELS = ('inaccuracy', 'mistake', 'miss')


def line(tone, kind):
    pool = TONES.get(tone, TONES['warm']).get(kind) or ['']
    return random.choice(pool)


def label_line(tone, label):
    """A short tone sentence for a move rating (empty for ordinary moves so the text isn't cluttered)."""
    if label in GREAT_LABELS:
        return line(tone, 'great')
    if label == 'blunder':
        return line(tone, 'blunder')
    if label in BAD_LABELS:
        return line(tone, 'bad')
    if label == 'best' and random.random() < 0.5:
        return line(tone, 'good')
    return ''


TIPS = [
    "Control the center with pawns and pieces early in the game.",
    "Develop your knights and bishops before moving the queen.",
    "Castle early to protect your king.",
    "Before every move, ask: what is my opponent threatening?",
    "Look for checks, captures and threats, in that order.",
    "Don't move the same piece twice in the opening without a reason.",
    "Knights on the rim are dim: place them near the center.",
    "Rooks belong on open files.",
    "A pinned piece cannot move without exposing something more valuable.",
    "In the endgame, activate your king.",
    "Trade pieces when you are ahead in material.",
    "Passed pawns must be pushed, but support them with your king.",
    "Before you take a pawn, check that you aren't walking into a tactic.",
    "Every pawn move creates weaknesses: make them count.",
    "If you see a good move, look for a better one.",
    "Don't forget stalemate when you are winning!",
    "Bishops love open positions, knights love closed ones.",
    "Make sure all your pieces are defended.",
    "Back-rank mate is the most common trap: give your king an escape square.",
    "Practice puzzles every day: pattern recognition wins games.",
]


def tip_of_the_day():
    return TIPS[datetime.date.today().toordinal() % len(TIPS)]
