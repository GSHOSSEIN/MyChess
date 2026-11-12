"""Interactive lessons. Step = dict(fen, text, task=None|'move'|'mate1', answers=[uci or destination square], show=square, arrows=[(a,b)], hint).
Positions are checked by tools/verify_lessons.py."""

START = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

LESSONS = [
    {'id': 'pieces', 'title': 'How the pieces move', 'level': 'Beginner', 'steps': [
        {'fen': START, 'text': "Welcome to the board! Each player starts with 16 pieces and White always moves first. "
                               "In this lesson you will learn how every piece moves, one at a time. Press Next."},
        {'fen': '7k/3p4/8/8/3R4/8/8/K7 w - - 0 1', 'show': 'd4', 'task': 'move', 'answers': ['d4d7'],
         'text': "The ROOK moves in straight lines: forward, backward and sideways, as far as nothing blocks it. "
                 "The dots show where it can go. Capture the black pawn on d7!",
         'hint': 'Move the rook straight up the d-file.'},
        {'fen': '7k/8/8/6p1/8/8/8/K1B5 w - - 0 1', 'show': 'c1', 'task': 'move', 'answers': ['c1g5'],
         'text': "The BISHOP moves diagonally and always stays on the same colour of square. Capture the pawn on g5!",
         'hint': 'Slide the bishop along the long diagonal.'},
        {'fen': '7k/8/5p2/8/4N3/8/8/K7 w - - 0 1', 'show': 'e4', 'task': 'move', 'answers': ['e4f6'],
         'text': "The KNIGHT jumps in an L-shape: two squares one way and one square sideways. It is the only piece that can jump over others. "
                 "Capture the pawn on f6!", 'hint': 'Two squares up and one to the right.'},
        {'fen': '8/p6k/8/8/3Q4/8/8/K7 w - - 0 1', 'show': 'd4', 'task': 'move', 'answers': ['d4a7'],
         'text': "The QUEEN is the strongest piece: she moves like a rook and a bishop combined. Capture the pawn on a7!",
         'hint': 'Use the diagonal towards the top-left corner.'},
        {'fen': '7k/8/8/8/8/4p3/4K3/8 w - - 0 1', 'show': 'e2', 'task': 'move', 'answers': ['e2e3'],
         'text': "The KING moves one square in any direction. He is the most important piece: if he is trapped, you lose. "
                 "The black pawn on e3 is not protected, so capture it!", 'hint': 'One step forward.'},
        {'fen': '7k/8/8/8/8/8/4P3/K7 w - - 0 1', 'show': 'e2', 'task': 'move', 'answers': ['e2e4'],
         'text': "PAWNS move forward one square, but from their starting square they may move two. Push the e-pawn two squares!",
         'hint': 'e2 to e4.'},
        {'fen': '7k/8/8/3p4/4P3/8/8/K7 w - - 0 1', 'show': 'e4', 'task': 'move', 'answers': ['e4d5'],
         'text': "Pawns capture DIAGONALLY, one square forward. Capture the pawn on d5!", 'hint': 'Take diagonally.'},
    ]},
    {'id': 'mate', 'title': 'Check, checkmate and stalemate', 'level': 'Beginner', 'steps': [
        {'fen': '4k3/8/8/8/8/8/4R3/K7 b - - 0 1', 'arrows': [('e2', 'e8')],
         'text': "When a king is attacked it is in CHECK, like the black king here. The player must get out of check: move the king, block, or capture the attacker."},
        {'fen': '6k1/5ppp/8/8/8/8/8/R3K3 w - - 0 1', 'task': 'mate1',
         'text': "CHECKMATE means the king is in check and cannot escape: the game is over. The black king is boxed in by its own pawns. Find the checkmate!",
         'hint': 'The rook can reach the back rank.'},
        {'fen': '7k/8/6K1/8/8/8/Q7/8 w - - 0 1', 'task': 'mate1',
         'text': "Your king helps to trap the enemy king. Find the checkmate!", 'hint': 'Check along the 8th rank.'},
        {'fen': '7k/R7/8/8/8/8/1R6/K7 w - - 0 1', 'task': 'mate1',
         'text': "Two rooks can mate by building a ladder: one rook cuts off a rank while the other gives check. Mate in one!",
         'hint': 'Bring the second rook to the back rank.'},
        {'fen': '7k/5Q2/6K1/8/8/8/8/8 b - - 0 1', 'arrows': [('f7', 'g8')],
         'text': "Careful! If the king is NOT in check but has no legal move, it is STALEMATE and the game is a draw. "
                 "Here Black to move has no squares and is not in check. Never stalemate when you are winning!"},
    ]},
    {'id': 'special', 'title': 'Special moves', 'level': 'Beginner', 'steps': [
        {'fen': 'r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1', 'task': 'move', 'answers': ['e1g1'], 'show': 'e1',
         'text': "CASTLING protects your king and activates a rook. To castle SHORT (kingside), move the king two squares towards the h-file rook; the rook jumps over. Castle short now!",
         'hint': 'King from e1 to g1.'},
        {'fen': 'r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1', 'task': 'move', 'answers': ['e1c1'], 'show': 'e1',
         'text': "To castle LONG (queenside), move the king two squares towards the a-file rook: e1 to c1 (you can also drag the king onto the a1 rook). "
                 "The squares between king and rook (b1, c1, d1) must be empty. Castle long now!", 'hint': 'King from e1 to c1.'},
        {'fen': 'rnbqkbnr/ppppp1pp/8/4Pp2/8/8/PPPP1PPP/RNBQKBNR w KQkq f6 0 3', 'task': 'move', 'answers': ['e5f6'], 'arrows': [('e5', 'f6')],
         'text': "EN PASSANT: if an enemy pawn jumps two squares and lands next to your pawn, you may capture it as if it had moved only one square - but only right away. "
                 "Black just played f7-f5. Capture en passant!", 'hint': 'Your e5 pawn captures on f6.'},
        {'fen': '8/4P3/8/8/8/8/k7/4K3 w - - 0 1', 'task': 'move', 'answers': ['e7e8q', 'e7e8r', 'e7e8b', 'e7e8n'],
         'text': "PROMOTION: a pawn that reaches the last rank becomes a queen, rook, bishop or knight. Promote the pawn!", 'hint': 'Push the pawn to e8.'},
    ]},
    {'id': 'tactics', 'title': 'Forks, pins and skewers', 'level': 'Intermediate', 'steps': [
        {'fen': 'r3k3/8/4N3/8/8/8/8/7K w - - 0 1', 'task': 'move', 'answers': ['e6c7'],
         'text': "A FORK attacks two pieces at once. Knights are great at it. Find the knight move that checks the king and attacks the rook!",
         'hint': 'Look at c7.'},
        {'fen': '4k3/8/2n5/8/8/8/8/K4B2 w - - 0 1', 'task': 'move', 'answers': ['f1b5'],
         'text': "A PIN attacks a piece that cannot move without exposing a more valuable piece behind it. Pin the knight on c6 to the king!",
         'hint': 'Bishop to b5.'},
        {'fen': '8/8/8/8/2k3q1/8/8/R6K w - - 0 1', 'task': 'move', 'answers': ['a1a4'],
         'text': "A SKEWER is a pin in reverse: attack the valuable piece first; when it moves away, you win what is behind it. Skewer the king and queen!",
         'hint': 'Check the king along the 4th rank.'},
        {'fen': '6rk/6pp/8/4N3/8/8/8/K7 w - - 0 1', 'task': 'mate1',
         'text': "The famous SMOTHERED MATE: a king surrounded by its own pieces can be mated by a knight. Find it!", 'hint': 'Knight to f7.'},
    ]},
    {'id': 'opening', 'title': 'Opening principles', 'level': 'Beginner', 'steps': [
        {'fen': START, 'arrows': [('e2', 'e4'), ('d2', 'd4')],
         'text': "Three golden rules for the opening: 1) fight for the CENTER (e4, d4, e5, d5), 2) DEVELOP your knights and bishops, 3) CASTLE to keep your king safe."},
        {'fen': START, 'task': 'move', 'answers': ['e2e4', 'd2d4', 'g1f3', 'c2c4'],
         'text': "Play a good first move that fights for the center.", 'hint': 'e4 or d4 are the classics.'},
        {'fen': 'rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2', 'task': 'move', 'answers': ['g1f3', 'b1c3'],
         'text': "Now develop a knight towards the center. Knights before bishops!", 'hint': 'Nf3 attacks the e5 pawn.'},
        {'fen': 'r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/2PP1N2/PP3PPP/RNBQK2R w KQkq - 0 6', 'task': 'move', 'answers': ['e1g1'],
         'text': "Your pieces are developed. Time to castle and tuck the king away!", 'hint': 'Castle short.'},
        {'fen': START,
         'text': "Also remember: don't move the same piece twice without a reason, don't bring the queen out too early, and don't grab pawns while your king is unsafe. Well done!"},
    ]},
    {'id': 'endgame', 'title': 'Endgame basics', 'level': 'Intermediate', 'steps': [
        {'fen': '7k/5Q2/6K1/8/8/8/8/8 w - - 0 1', 'task': 'mate1',
         'text': "In the ENDGAME the king becomes a fighter. King and queen can mate a lone king: use the queen to take away squares and bring your king close. Find the mate!",
         'hint': 'The queen is protected by your king.'},
        {'fen': '7k/8/6K1/8/8/8/8/R7 w - - 0 1', 'task': 'mate1',
         'text': "King and rook can mate too. Push the enemy king to the edge, keep your king opposite his, then check with the rook on the back rank. Mate in one!",
         'hint': 'Rook to a8.'},
        {'fen': '8/8/8/4k3/8/4K3/8/8 w - - 0 1', 'arrows': [('e3', 'e5')],
         'text': "OPPOSITION: kings can never touch, so when they face each other with one square between them, the player who must MOVE gives way. "
                 "Learning to win the opposition is the key to king and pawn endgames."},
    ]},
]
