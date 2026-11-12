"""Turns engine evaluations into chess.com-style move ratings and coach comments."""
import math

import chess

from engines import VALUE, win_percent
from i18n import tr

LABEL_STYLE = {          # label: (colour, symbol)
    'brilliant':  ('#1baca6', '!!'),
    'great':      ('#5c8bb0', '!'),
    'best':       ('#81b64c', '★'),
    'excellent':  ('#96bc4b', '✓'),
    'good':       ('#a0b58b', '✓'),
    'book':       ('#a88865', 'B'),
    'forced':     ('#8e8e8e', '→'),
    'inaccuracy': ('#f7c631', '?!'),
    'mistake':    ('#e58f2a', '?'),
    'miss':       ('#ee6055', '×'),
    'blunder':    ('#ca3431', '??'),
}
LABEL_ORDER = ['brilliant', 'great', 'best', 'excellent', 'good', 'book', 'inaccuracy', 'mistake', 'miss', 'blunder']
LABEL_NAME = {
    'brilliant': 'Brilliant', 'great': 'Great', 'best': 'Best', 'excellent': 'Excellent', 'good': 'Good',
    'book': 'Book', 'forced': 'Forced', 'inaccuracy': 'Inaccuracy', 'mistake': 'Mistake', 'miss': 'Miss',
    'blunder': 'Blunder',
}
PIECE_NAMES = {chess.PAWN: 'pawn', chess.KNIGHT: 'knight', chess.BISHOP: 'bishop',
               chess.ROOK: 'rook', chess.QUEEN: 'queen', chess.KING: 'king'}


def label_name(label):
    return tr(LABEL_NAME[label])


def is_sacrifice(board, move):
    """True if the moved piece can be taken for a net loss of about two pawns or more."""
    piece = board.piece_at(move.from_square)
    if piece is None or piece.piece_type in (chess.PAWN, chess.KING):
        return False
    value = VALUE[piece.piece_type]
    victim = board.piece_at(move.to_square)
    gain = VALUE[victim.piece_type] if victim else 0
    test = board.copy(stack=False)
    test.push(move)
    sq = move.to_square
    attackers = test.attackers(not piece.color, sq)
    if not attackers:
        return False
    cheapest = min((VALUE[test.piece_at(a).piece_type] or 20000) for a in attackers)
    defended = bool(test.attackers(piece.color, sq))
    loss = (value - gain) if not defended else (value - cheapest - gain if cheapest < value else 0)
    return loss >= 200


def _safe_san(board, move):
    try:
        return board.san(move)
    except Exception:
        return move.uci()


def review_game(start_fen, moves, evals):
    """moves: list of chess.Move.  evals: output of engines.analyse_game (len(moves)+1)."""
    board = chess.Board(start_fen) if start_fen else chess.Board()
    out = []
    prev_label = {chess.WHITE: None, chess.BLACK: None}
    for i, mv in enumerate(moves):
        before, after = evals[i], evals[i + 1]
        mover = board.turn
        sign = 1 if mover == chess.WHITE else -1
        wp_before = win_percent(before['cp'] * sign)
        wp_after = win_percent(after['cp'] * sign)
        uci = mv.uci()
        san = _safe_san(board, mv)
        best_uci = before['best']
        best_san = ''
        if best_uci:
            try:
                best_san = _safe_san(board, chess.Move.from_uci(best_uci))
            except ValueError:
                best_san = best_uci
        is_best = (uci == best_uci)
        loss = 0.0 if is_best else max(0.0, wp_before - wp_after)

        if before['legal'] == 1:
            label = 'forced'
        elif is_best:
            label = 'best'
        elif loss <= 2:
            label = 'excellent'
        elif loss <= 5:
            label = 'good'
        elif loss <= 10:
            label = 'inaccuracy'
        elif loss <= 20:
            label = 'mistake'
        else:
            label = 'blunder'

        if label in ('best', 'excellent', 'good') and i < 10 and loss <= 3 and abs(before['cp']) <= 90 \
                and uci in (best_uci, before['second']):
            label = 'book'
        if label == 'best' and before['second_cp'] is not None and before['legal'] > 1:
            wp_second = win_percent(before['second_cp'] * sign)
            if wp_before - wp_second >= 12 and 12 < wp_before < 92:
                label = 'great'
        if label in ('best', 'excellent', 'great') and loss <= 2.5 and wp_after >= 45 and wp_before < 92 \
                and is_sacrifice(board, mv):
            label = 'brilliant'
        opp = not mover
        if label in ('inaccuracy', 'mistake') and wp_before >= 62 and prev_label[opp] in ('inaccuracy', 'mistake', 'blunder'):
            label = 'miss'

        san_after_board = board.copy(stack=False)
        san_after_board.push(mv)
        checkmate = san_after_board.is_checkmate()
        threat_piece = threat_san = ''
        reply = after['best']
        if reply and label in ('mistake', 'blunder', 'miss'):
            try:
                rm = chess.Move.from_uci(reply)
                victim = san_after_board.piece_at(rm.to_square)
                if victim is not None and VALUE[victim.piece_type] >= 300 and victim.color == mover:
                    threat_piece = PIECE_NAMES[victim.piece_type]
                    threat_san = _safe_san(san_after_board, rm)
            except ValueError:
                pass
        acc = max(0.0, min(100.0, 103.1668 * math.exp(-0.04354 * loss) - 3.1669))
        out.append({
            'ply': i + 1, 'color': mover, 'san': san, 'uci': uci, 'label': label, 'loss': loss,
            'best_uci': best_uci, 'best_san': best_san, 'wp_before': wp_before, 'wp_after': wp_after,
            'cp_after': after['cp'], 'mate_after': after['mate'], 'accuracy': acc, 'checkmate': checkmate,
            'threat_piece': threat_piece, 'threat_san': threat_san,
            'missed_mate': before['mate'] is not None and before['mate'] * sign > 0 and
                           not (after['mate'] is not None and after['mate'] * sign > 0),
            'mate_n': abs(before['mate']) if before['mate'] else 0,
        })
        prev_label[mover] = label
        board.push(mv)
    return out


def summarize(reviews, color):
    counts = {k: 0 for k in LABEL_STYLE}
    accs = []
    for r in reviews:
        if r['color'] == color:
            counts[r['label']] += 1
            accs.append(r['accuracy'])
    acc = sum(accs) / len(accs) if accs else 100.0
    return counts, acc


def coach_text(r):
    """One or two sentences like a coach would say about the move."""
    san = r['san']
    label = r['label']
    if r['checkmate']:
        return tr('{san} is checkmate! Well played.').format(san=san)
    base = {
        'brilliant': tr('{san} is brilliant! A bold sacrifice that really works.'),
        'great': tr('{san} is a great move: the only move that keeps your position strong.'),
        'best': tr('{san} is the best move.'),
        'excellent': tr('{san} is an excellent move.'),
        'good': tr('{san} is a good move.'),
        'book': tr('{san} is a book move.'),
        'forced': tr('{san} is forced: it was your only legal move.'),
        'inaccuracy': tr('{san} is an inaccuracy.'),
        'mistake': tr('{san} is a mistake.'),
        'miss': tr('{san} misses a chance to take advantage.'),
        'blunder': tr('{san} is a blunder.'),
    }[label].format(san=san)
    extra = []
    if label in ('inaccuracy', 'mistake', 'miss', 'blunder') and r['best_san']:
        if r['missed_mate'] and r['mate_n']:
            extra.append(tr('You could have mated in {n} with {best}.').format(n=r['mate_n'], best=r['best_san']))
        else:
            extra.append(tr('{best} was better.').format(best=r['best_san']))
    if r['threat_piece']:
        extra.append(tr('Now {reply} wins your {piece}.').format(reply=r['threat_san'], piece=tr(r['threat_piece'])))
    return ' '.join([base] + extra)
