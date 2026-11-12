"""Chess engines used by My Chess.

* UciEngine   - thin, thread-safe wrapper around Stockfish (python-chess)
* mini search - a small pure-python alpha-beta engine used when Stockfish is
                missing, for weak bots and for the basic game review
* compute_bot_move()  - runs on a worker thread, never touches the GUI
* analyse_game()      - per-position evaluations for the game review
"""
import glob
import math
import os
import random
import shutil
import sys
import threading
import time

import chess
import chess.engine

ROOT = os.path.dirname(os.path.abspath(__file__))


# ------------------------------------------------------------------ Stockfish
def _search_dirs():
    dirs = [ROOT, os.path.dirname(ROOT)]
    if getattr(sys, 'frozen', False):
        dirs.insert(0, os.path.dirname(sys.executable))
        if hasattr(sys, '_MEIPASS'):
            dirs.insert(1, sys._MEIPASS)
    return dirs


def _is_engine_file(path):
    if not os.path.isfile(path):
        return False
    low = path.lower()
    if low.endswith(('.md', '.txt', '.cpp', '.h', '.cff', '.sh', '.nnue', '.yml', '.json', '.rc', '.py')):
        return False
    if os.name == 'nt':
        return low.endswith('.exe')
    return os.access(path, os.X_OK)


def find_stockfish(saved=''):
    """Return a usable Stockfish executable path or ''."""
    cands = []
    if saved:
        cands.append(saved)
    for base in _search_dirs():
        for pat in ('stockfish/stockfish*', 'stockfish*', 'engines/stockfish*', 'engine/stockfish*'):
            cands.extend(sorted(glob.glob(os.path.join(base, pat))))
    found = shutil.which('stockfish')
    if found:
        cands.append(found)
    for c in cands:
        if _is_engine_file(c):
            return c
    return ''


class UciEngine:
    """One Stockfish process; all calls are serialised with a lock."""

    def __init__(self, path):
        self.path = path
        self.engine = None
        self.lock = threading.Lock()
        self._cfg = None

    def start(self):
        kwargs = {}
        if os.name == 'nt':
            kwargs['creationflags'] = 0x08000000        # CREATE_NO_WINDOW: no console flash
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.path, **kwargs)
        except TypeError:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.path)
        try:
            self.engine.configure({'Threads': max(1, min(4, (os.cpu_count() or 2) // 2)), 'Hash': 64})
        except Exception:
            pass
        return self

    def _configure(self, elo):
        cfg = ('full',) if elo >= 3000 else ('elo', int(elo))
        if cfg == self._cfg:
            return
        try:
            if elo >= 3000:
                self.engine.configure({'UCI_LimitStrength': False})
            else:
                self.engine.configure({'UCI_LimitStrength': True, 'UCI_Elo': max(1320, min(3190, int(elo)))})
        except Exception:
            try:
                self.engine.configure({'Skill Level': max(0, min(20, int((elo - 1300) / 90)))})
            except Exception:
                pass
        self._cfg = cfg

    def play(self, board, elo, seconds):
        with self.lock:
            self._configure(elo)
            return self.engine.play(board, chess.engine.Limit(time=seconds)).move

    def analyse(self, board, seconds, multipv=2):
        with self.lock:
            try:
                self.engine.configure({'UCI_LimitStrength': False})
                self._cfg = ('full',)
            except Exception:
                pass
            infos = self.engine.analyse(board, chess.engine.Limit(time=seconds), multipv=multipv)
        return infos if isinstance(infos, list) else [infos]

    def quit(self):
        eng, self.engine = self.engine, None
        if eng is not None:
            try:
                eng.quit()
            except Exception:
                try:
                    eng.close()
                except Exception:
                    pass


# ------------------------------------------------------------ built-in engine
VALUE = {chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330, chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 0}
MATE = 100000

# Piece-square tables, white's point of view, a8 first (simplified evaluation function)
_PAWN = [0, 0, 0, 0, 0, 0, 0, 0, 50, 50, 50, 50, 50, 50, 50, 50, 10, 10, 20, 30, 30, 20, 10, 10, 5, 5, 10, 25, 25, 10, 5, 5,
         0, 0, 0, 20, 20, 0, 0, 0, 5, -5, -10, 0, 0, -10, -5, 5, 5, 10, 10, -20, -20, 10, 10, 5, 0, 0, 0, 0, 0, 0, 0, 0]
_KNIGHT = [-50, -40, -30, -30, -30, -30, -40, -50, -40, -20, 0, 0, 0, 0, -20, -40, -30, 0, 10, 15, 15, 10, 0, -30,
           -30, 5, 15, 20, 20, 15, 5, -30, -30, 0, 15, 20, 20, 15, 0, -30, -30, 5, 10, 15, 15, 10, 5, -30,
           -40, -20, 0, 5, 5, 0, -20, -40, -50, -40, -30, -30, -30, -30, -40, -50]
_BISHOP = [-20, -10, -10, -10, -10, -10, -10, -20, -10, 0, 0, 0, 0, 0, 0, -10, -10, 0, 5, 10, 10, 5, 0, -10,
           -10, 5, 5, 10, 10, 5, 5, -10, -10, 0, 10, 10, 10, 10, 0, -10, -10, 10, 10, 10, 10, 10, 10, -10,
           -10, 5, 0, 0, 0, 0, 5, -10, -20, -10, -10, -10, -10, -10, -10, -20]
_KING = [-30, -40, -40, -50, -50, -40, -40, -30, -30, -40, -40, -50, -50, -40, -40, -30, -30, -40, -40, -50, -50, -40, -40, -30,
         -30, -40, -40, -50, -50, -40, -40, -30, -20, -30, -30, -40, -40, -30, -30, -20, -10, -20, -20, -20, -20, -20, -20, -10,
         20, 20, 0, 0, 0, 0, 20, 20, 20, 30, 10, 0, 0, 10, 30, 20]
PST = {chess.PAWN: _PAWN, chess.KNIGHT: _KNIGHT, chess.BISHOP: _BISHOP, chess.KING: _KING}


class _Timeout(Exception):
    pass


def evaluate(board):
    """Static evaluation in centipawns from the side to move's point of view."""
    total = 0
    for sq, piece in board.piece_map().items():
        v = VALUE[piece.piece_type]
        table = PST.get(piece.piece_type)
        if table is not None:
            idx = (7 - chess.square_rank(sq)) * 8 + chess.square_file(sq) if piece.color == chess.WHITE \
                else chess.square_rank(sq) * 8 + chess.square_file(sq)
            v += table[idx]
        total += v if piece.color == chess.WHITE else -v
    return total if board.turn == chess.WHITE else -total


def _order(board, moves):
    def key(m):
        victim = board.piece_at(m.to_square)
        score = 0
        if victim is not None:
            att = board.piece_at(m.from_square)
            score += 10 * VALUE[victim.piece_type] - (VALUE[att.piece_type] if att else 0) + 10000
        elif board.is_en_passant(m):
            score += 10000
        if m.promotion:
            score += 8000
        return -score
    return sorted(moves, key=key)


class _Search:
    def __init__(self, deadline):
        self.deadline = deadline
        self.nodes = 0

    def tick(self):
        self.nodes += 1
        if self.deadline is not None and (self.nodes & 255) == 0 and time.monotonic() > self.deadline:
            raise _Timeout()

    def quiesce(self, board, alpha, beta, depth):
        self.tick()
        stand = evaluate(board)
        if depth <= 0:
            return stand
        if stand >= beta:
            return stand
        alpha = max(alpha, stand)
        for m in _order(board, list(board.generate_legal_captures())):
            board.push(m)
            score = -self.quiesce(board, -beta, -alpha, depth - 1)
            board.pop()
            if score >= beta:
                return score
            alpha = max(alpha, score)
        return alpha

    def negamax(self, board, depth, alpha, beta, ply, qdepth):
        self.tick()
        moves = list(board.legal_moves)
        if not moves:
            return -MATE + ply if board.is_check() else 0
        if depth <= 0:
            return self.quiesce(board, alpha, beta, qdepth) if qdepth > 0 else evaluate(board)
        best = -MATE * 2
        for m in _order(board, moves):
            board.push(m)
            score = -self.negamax(board, depth - 1, -beta, -alpha, ply + 1, qdepth)
            board.pop()
            if score > best:
                best = score
            if best > alpha:
                alpha = best
            if alpha >= beta:
                break
        return best


def search(board, max_depth=2, seconds=0.5, qdepth=3, full=False):
    """Returns [(move, score_for_side_to_move)] best first, or [] if there is no legal move.
    full=True gives every root move an exact score (needed for noisy bots); otherwise only the
    top two moves are exact (enough for the review)."""
    work = board.copy(stack=False)
    moves = list(work.legal_moves)
    if not moves:
        return []
    deadline = time.monotonic() + seconds
    result = None
    for depth in range(1, max_depth + 1):
        s = _Search(None if depth == 1 else deadline)
        scored = []
        best = second = -MATE * 2
        try:
            for m in _order(work, moves):
                work.push(m)
                if full or len(scored) < 2:
                    score = -s.negamax(work, depth - 1, -MATE * 2, MATE * 2, 1, qdepth)
                else:
                    score = -s.negamax(work, depth - 1, -MATE * 2, -(second - 1), 1, qdepth)
                work.pop()
                scored.append((m, score))
                if score > best:
                    best, second = score, best
                elif score > second:
                    second = score
        except _Timeout:
            while len(work.move_stack) > 0:
                work.pop()
            break
        scored.sort(key=lambda t: -t[1])
        result = scored
    return result or [(moves[0], 0)]


# ------------------------------------------------------------------ bot moves
_SIGMA = [(100, 800), (250, 550), (400, 420), (550, 330), (700, 260), (850, 200), (1000, 150), (1200, 100), (1320, 70)]
_RANDOM = [(100, 0.50), (250, 0.25), (400, 0.15), (550, 0.10), (700, 0.06), (850, 0.04), (1000, 0.02), (1200, 0.01), (1320, 0.0)]


def _interp(table, x):
    if x <= table[0][0]:
        return table[0][1]
    for (x0, y0), (x1, y1) in zip(table, table[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / float(x1 - x0)
    return table[-1][1]


def _rules_pick(board, rules, moves, elo):
    """Move choice when house rules are active: simple material/safety heuristics."""
    mover = board.turn
    care = min(1.0, elo / 1500.0)
    test = board.copy(stack=False)
    best, best_score = None, -1e9
    for m in moves:
        piece = board.piece_at(m.from_square)
        victim = board.piece_at(m.to_square)
        gain = VALUE[victim.piece_type] / 100.0 if victim else 0.0
        if m.promotion:
            gain += 8
        penalty = 0.0
        mate_bonus = 0.0
        test.push(m)
        if rules.is_attacked(test, m.to_square, not mover):
            defended = rules.is_attacked(test, m.to_square, mover)
            val = VALUE[piece.piece_type] / 100.0 if piece else 1.0
            penalty = val * (0.5 if defended else 1.0)
        if rules.in_check(test):
            mate_bonus = 0.5
            if not rules.legal_moves(test):
                mate_bonus = 100.0
        test.pop()
        noise = random.gauss(0, 1.4 * (1 - care) + 0.25)
        score = gain - care * penalty + mate_bonus + noise
        if score > best_score:
            best, best_score = m, score
    return best


def compute_bot_move(board, rules, elo, think_range, uci=None):
    """Pick a move for the side to move. Blocks (sleeps) to look human; run in a worker thread."""
    t0 = time.monotonic()
    moves = rules.legal_moves(board)
    if not moves:
        return None
    think = random.uniform(*think_range)
    move = None
    if len(moves) == 1:
        move = moves[0]
    elif not rules.active and uci is not None and elo >= 1320:
        try:
            seconds = 0.12 + (elo - 1320) / 1870.0 * 1.1
            move = uci.play(board.copy(stack=False), elo, seconds)
            if move not in moves:
                move = None
        except Exception:
            move = None
    if move is None and not rules.active:
        if random.random() < _interp(_RANDOM, min(elo, 1320)):
            move = random.choice(moves)
        else:
            depth = 1 if elo < 700 else 2
            qd = 0 if elo < 500 else 3 if elo < 1320 else 4
            if elo >= 1320:
                depth = 3
            scored = search(board, max_depth=depth, seconds=1.4, qdepth=qd, full=True)
            sigma = _interp(_SIGMA, min(elo, 1320))
            move = max(scored, key=lambda t: t[1] + random.gauss(0, sigma))[0]
    if move is None:
        move = _rules_pick(board, rules, moves, elo) or random.choice(moves)
    left = think - (time.monotonic() - t0)
    if left > 0:
        time.sleep(left)
    return move


# ------------------------------------------------------------------- analysis
def _clamp_cp(cp):
    return max(-2000, min(2000, cp))


def analyse_game(start_fen, moves, engine_path, seconds=0.25, progress=None, cancel=None):
    """Evaluate every position of a game (white's point of view).

    Returns a list of n+1 dicts: cp, mate, best, second, second_cp, legal.
    Uses Stockfish when `engine_path` is set, otherwise the built-in mini engine."""
    board = chess.Board(start_fen) if start_fen else chess.Board()
    eng = None
    if engine_path:
        try:
            eng = UciEngine(engine_path).start()
        except Exception:
            eng = None
    out = []
    total = len(moves) + 1
    try:
        for i in range(total):
            if cancel is not None and cancel():
                return None
            out.append(_analyse_position(board, eng, seconds))
            if progress:
                progress(i + 1, total)
            if i < len(moves):
                board.push(moves[i])
    finally:
        if eng is not None:
            eng.quit()
    return out


def _analyse_position(board, eng, seconds):
    legal = board.legal_moves.count()
    if legal == 0:
        if board.is_check():
            cp = -2000 if board.turn == chess.WHITE else 2000
            mate = 0
        else:
            cp, mate = 0, None
        return {'cp': cp, 'mate': mate, 'best': '', 'second': '', 'second_cp': None, 'legal': 0}
    if eng is not None:
        try:
            infos = eng.analyse(board, seconds, multipv=2)
            top = infos[0]
            sc = top['score'].white()
            mate = sc.mate()
            cp = _clamp_cp(sc.score(mate_score=2000))
            best = top['pv'][0].uci() if top.get('pv') else ''
            second, second_cp = '', None
            if len(infos) > 1 and infos[1].get('pv'):
                second = infos[1]['pv'][0].uci()
                second_cp = _clamp_cp(infos[1]['score'].white().score(mate_score=2000))
            return {'cp': cp, 'mate': mate, 'best': best, 'second': second, 'second_cp': second_cp, 'legal': legal}
        except Exception:
            pass
    scored = search(board, max_depth=2, seconds=seconds + 0.2, qdepth=3, full=False)
    sign = 1 if board.turn == chess.WHITE else -1
    best_m, best_s = scored[0]
    mate = None
    if abs(best_s) > MATE - 100:
        n = (MATE - abs(best_s) + 1) // 2
        mate = n * (1 if best_s * sign > 0 else -1)
    out = {'cp': _clamp_cp(best_s * sign), 'mate': mate, 'best': best_m.uci(), 'second': '', 'second_cp': None, 'legal': legal}
    if len(scored) > 1:
        out['second'] = scored[1][0].uci()
        out['second_cp'] = _clamp_cp(scored[1][1] * sign)
    return out


def material_balance(board):
    """White minus black material in pawns (kings ignored)."""
    total = 0
    for piece in board.piece_map().values():
        v = VALUE[piece.piece_type] / 100.0
        total += v if piece.color == chess.WHITE else -v
    return total


def win_percent(cp):
    cp = max(-1500, min(1500, cp))
    return 50 + 50 * (2 / (1 + math.exp(-0.00368208 * cp)) - 1)
