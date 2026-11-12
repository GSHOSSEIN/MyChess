"""House rules on top of python-chess.

A RuleSet holds
  * a movement style per (colour, piece type)   - 'standard' means normal chess
  * a set of protected ("No Capture") squares

and generates the legal moves / check state with those rules applied.  With no
rules active everything falls through to python-chess, which is much faster.

Movement styles
  standard  normal chess
  queen / rook / bishop / knight   the piece moves like that piece
  amazon      queen + knight combined   (archbishop = bishop + knight, chancellor = rook + knight)
  pawn4     moves like a pawn, but up to 4 squares forward
  anywhere  may jump to ANY square that is empty or holds an enemy piece
            (never captures a king).  "Anywhere" pieces do not give check.
"""
import chess

STYLES = ['standard', 'queen', 'rook', 'bishop', 'knight', 'amazon', 'archbishop', 'chancellor', 'pawn4', 'anywhere']
# sliding directions / knight jumps per style (amazon = queen + knight, archbishop = bishop + knight, chancellor = rook + knight)
DIAGONAL_STYLES = ('queen', 'bishop', 'amazon', 'archbishop')
STRAIGHT_STYLES = ('queen', 'rook', 'amazon', 'chancellor')
KNIGHT_STYLES = ('knight', 'amazon', 'archbishop', 'chancellor')

ROOK_DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
BISHOP_DIRS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
KNIGHT_JUMPS = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]
PROMOTIONS = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]


def _on_board(f, r):
    return 0 <= f < 8 and 0 <= r < 8


class RuleSet:
    def __init__(self):
        self.moves = {}            # (color, piece_type) -> style
        self.no_capture = set()    # protected squares
        self._ver = 0
        self._key = None
        self._val = []

    # ------------------------------------------------------------ bookkeeping
    def copy(self):
        r = RuleSet()
        r.moves = dict(self.moves)
        r.no_capture = set(self.no_capture)
        return r

    @property
    def active(self):
        return bool(self.moves) or bool(self.no_capture)

    def _touch(self):
        self._ver += 1

    def style_of(self, piece):
        return self.moves.get((piece.color, piece.piece_type), 'standard')

    def set_style(self, color, ptype, style):
        if style == 'standard' or style not in STYLES:
            self.moves.pop((color, ptype), None)
        else:
            self.moves[(color, ptype)] = style
        self._touch()

    def reset(self):
        self.moves.clear()
        self.no_capture.clear()
        self._touch()

    def reset_pieces(self, keys):
        for k in keys:
            self.moves.pop(k, None)
        self._touch()

    def set_protected(self, squares):
        self.no_capture = set(squares)
        self._touch()

    def protect(self, sq, on=True):
        if on:
            self.no_capture.add(sq)
        else:
            self.no_capture.discard(sq)
        self._touch()

    def toggle_protect(self, sq):
        self.protect(sq, sq not in self.no_capture)

    def begin_move(self, move):
        """Call BEFORE board.push(move). Returns a token for end_move()."""
        flag = move.from_square in self.no_capture
        self.no_capture.discard(move.from_square)
        self.no_capture.discard(move.to_square)
        self._touch()
        return flag

    def end_move(self, move, flag):
        """Call AFTER board.push(move): the protection follows the piece."""
        if flag:
            self.no_capture.add(move.to_square)
        self._touch()

    def to_json(self):
        return {'moves': [[int(c), int(t), s] for (c, t), s in self.moves.items()],
                'no_capture': sorted(self.no_capture)}

    def load_json(self, data):
        self.moves = {}
        self.no_capture = set()
        try:
            for c, t, s in data.get('moves', []):
                if s in STYLES and s != 'standard':
                    self.moves[(bool(c), int(t))] = s
            for sq in data.get('no_capture', []):
                if 0 <= int(sq) < 64:
                    self.no_capture.add(int(sq))
        except (TypeError, ValueError, AttributeError):
            self.moves = {}
            self.no_capture = set()
        self._touch()

    # ----------------------------------------------------------- attack map
    def is_attacked(self, board, target, by_color):
        """Is `target` attacked by `by_color`, honouring custom movement?
        Protected pieces still attack; protection only stops them being taken."""
        tf, tr = chess.square_file(target), chess.square_rank(target)
        for frm, piece in board.piece_map().items():
            if piece.color != by_color:
                continue
            style = self.moves.get((piece.color, piece.piece_type), 'standard')
            if style == 'standard':
                if target in board.attacks(frm):
                    return True
                continue
            if style == 'anywhere':
                continue
            ff, fr = chess.square_file(frm), chess.square_rank(frm)
            df, dr = tf - ff, tr - fr
            if style == 'pawn4':
                direction = 1 if piece.color == chess.WHITE else -1
                if dr == direction and abs(df) == 1:
                    return True
                continue
            if style in KNIGHT_STYLES and sorted((abs(df), abs(dr))) == [1, 2]:
                return True
            diagonal = abs(df) == abs(dr) and df != 0
            straight = (df == 0) != (dr == 0)
            if not ((diagonal and style in DIAGONAL_STYLES) or (straight and style in STRAIGHT_STYLES)):
                continue
            sf = 0 if df == 0 else (1 if df > 0 else -1)
            sr = 0 if dr == 0 else (1 if dr > 0 else -1)
            f, r = ff + sf, fr + sr
            blocked = False
            while (f, r) != (tf, tr):
                if board.piece_at(chess.square(f, r)) is not None:
                    blocked = True
                    break
                f += sf
                r += sr
            if not blocked:
                return True
        return False

    def in_check(self, board):
        if not self.active:
            return board.is_check()
        king = board.king(board.turn)
        return king is not None and self.is_attacked(board, king, not board.turn)

    # -------------------------------------------------------- move generation
    def legal_moves(self, board):
        key = (board.board_fen(), board.turn, board.castling_rights, board.ep_square, self._ver)
        if key != self._key:
            self._val = self._compute(board)
            self._key = key
        return self._val

    def _capture_ok(self, board, move):
        target = board.piece_at(move.to_square)
        if target is not None:
            if target.color == board.turn or target.piece_type == chess.KING:
                return False
            if move.to_square in self.no_capture:
                return False
        elif board.is_en_passant(move):
            cap_sq = move.to_square + (-8 if board.turn == chess.WHITE else 8)
            if cap_sq in self.no_capture:
                return False
        return True

    def _compute(self, board):
        if not self.active:
            return list(board.legal_moves)
        mover = board.turn
        opponent = not mover
        test = board.copy(stack=False)
        result = []
        seen = set()
        for frm, piece in list(board.piece_map().items()):
            if piece.color != mover:
                continue
            for move in self._piece_moves(board, frm, piece, opponent):
                if not self._capture_ok(board, move):
                    continue
                key = (move.from_square, move.to_square, move.promotion)
                if key in seen:
                    continue
                seen.add(key)
                test.push(move)
                king = test.king(mover)
                safe = king is None or not self.is_attacked(test, king, opponent)
                test.pop()
                if safe:
                    result.append(move)
        return result

    def _piece_moves(self, board, frm, piece, opponent):
        style = self.moves.get((piece.color, piece.piece_type), 'standard')
        out = []
        if style == 'standard':
            for m in board.generate_pseudo_legal_moves(from_mask=1 << frm):
                if piece.piece_type == chess.KING and board.is_castling(m):
                    mid = (m.from_square + m.to_square) // 2
                    if self.is_attacked(board, frm, opponent) or self.is_attacked(board, mid, opponent):
                        continue
                out.append(m)
            return out
        f0, r0 = chess.square_file(frm), chess.square_rank(frm)
        last_rank = 7 if piece.color == chess.WHITE else 0

        def add(to_sq):
            target = board.piece_at(to_sq)
            if target is not None and (target.color == piece.color or target.piece_type == chess.KING):
                return False
            if piece.piece_type == chess.PAWN and chess.square_rank(to_sq) == last_rank:
                for p in PROMOTIONS:
                    out.append(chess.Move(frm, to_sq, promotion=p))
            else:
                out.append(chess.Move(frm, to_sq))
            return target is None            # True -> a ray may continue

        if style == 'anywhere':
            for sq in range(64):
                if sq != frm:
                    add(sq)
        elif style == 'pawn4':
            direction = 1 if piece.color == chess.WHITE else -1
            for i in range(1, 5):
                r = r0 + direction * i
                if not _on_board(f0, r) or board.piece_at(chess.square(f0, r)) is not None:
                    break
                add(chess.square(f0, r))
            for df in (-1, 1):
                f, r = f0 + df, r0 + direction
                if _on_board(f, r):
                    sq = chess.square(f, r)
                    target = board.piece_at(sq)
                    if target is not None and target.color != piece.color:
                        add(sq)
        else:
            if style in KNIGHT_STYLES:
                for df, dr in KNIGHT_JUMPS:
                    f, r = f0 + df, r0 + dr
                    if _on_board(f, r):
                        add(chess.square(f, r))
            dirs = []
            if style in STRAIGHT_STYLES:
                dirs += ROOK_DIRS
            if style in DIAGONAL_STYLES:
                dirs += BISHOP_DIRS
            for df, dr in dirs:
                f, r = f0 + df, r0 + dr
                while _on_board(f, r):
                    if not add(chess.square(f, r)):
                        break
                    f += df
                    r += dr
        return out

    # ----------------------------------------------------------- UI helpers
    def targets_from(self, board, src):
        return {m.to_square for m in self.legal_moves(board) if m.from_square == src}

    def premove_targets(self, board, src):
        """Where could this piece go if it were its owner's turn? (loose estimate)"""
        piece = board.piece_at(src)
        if piece is None:
            return set()
        own = {sq for sq, p in board.piece_map().items() if p.color == piece.color}
        style = self.moves.get((piece.color, piece.piece_type), 'standard')
        if style != 'standard':
            return {sq for sq in range(64) if sq != src and sq not in own}
        tb = board.copy(stack=False)
        tb.turn = piece.color
        tb.ep_square = None
        return {m.to_square for m in tb.generate_pseudo_legal_moves(from_mask=1 << src)}

    def hides_markers(self, board, src):
        piece = board.piece_at(src)
        return piece is not None and self.moves.get((piece.color, piece.piece_type)) == 'anywhere'

    def game_state(self, board):
        """None while the game goes on, otherwise (kind, winner_colour_or_None)."""
        if not self.legal_moves(board):
            if self.in_check(board):
                return ('checkmate', not board.turn)
            return ('stalemate', None)
        if not self.active:
            if board.is_insufficient_material():
                return ('insufficient', None)
            if board.halfmove_clock >= 100:
                return ('fifty', None)
            if board.is_repetition(3):
                return ('repetition', None)
        return None
