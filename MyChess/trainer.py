"""Interactive board controller used by the Lessons and Puzzles pages."""
import chess


class TrainerController:
    """Plugs into BoardWidget (click / drag moves, promotion picker, arrows).  `on_move(move)` is called
    with every legal move the student tries; the page decides if it is right and then calls apply()."""

    def __init__(self, bw, on_move):
        self.bw = bw
        self.on_move = on_move
        self.board = chess.Board()
        self.selected = None
        self.enabled = True
        self.show_square = None
        bw.controller = self
        bw.interactive = True

    # ------------------------------------------------------------ state
    def set_board(self, board, last_move=None, flipped=None):
        self.board = board
        self.selected = None
        self.bw.clear_marks()
        self.bw.hint_arrows = []
        self.bw.promo = None
        self.bw.stop_animation()
        if flipped is not None:
            self.bw.flipped = flipped
            self.bw.clear_cache()
        self.last = last_move
        self.refresh()

    def refresh(self):
        markers = {}
        sel = self.selected if self.selected is not None else self.show_square
        if sel is not None:
            piece = self.board.piece_at(sel)
            if piece is not None and piece.color == self.board.turn:
                for m in self.board.legal_moves:
                    if m.from_square == sel:
                        markers[m.to_square] = 'capture' if (self.board.piece_at(m.to_square) or self.board.is_en_passant(m)) else 'dot'
        self.bw.selected = self.selected
        self.bw.markers = markers
        self.bw.markers_premove = False
        check = self.board.king(self.board.turn) if self.board.is_check() else None
        self.bw.set_position(self.board, getattr(self, 'last', None), check)

    def apply(self, move, animate=True):
        """Play `move` on the board (with animation) and refresh."""
        b = self.board
        piece = b.piece_at(move.from_square)
        items, ghosts = [], []
        if piece is not None:
            items.append(((piece.color, piece.piece_type), move.from_square, move.to_square))
            if piece.piece_type == chess.KING and b.is_castling(move):
                rank = chess.square_rank(move.from_square)
                kingside = chess.square_file(move.to_square) > chess.square_file(move.from_square)
                items.append(((piece.color, chess.ROOK), chess.square(7 if kingside else 0, rank), chess.square(5 if kingside else 3, rank)))
            else:
                cap = move.to_square
                if piece.piece_type == chess.PAWN and b.is_en_passant(move):
                    cap += -8 if piece.color == chess.WHITE else 8
                victim = b.piece_at(cap)
                if victim is not None:
                    ghosts.append(((victim.color, victim.piece_type), cap))
        b.push(move)
        self.last = move
        self.selected = None
        self.bw.clear_marks()
        self.bw.hint_arrows = []
        if animate and items:
            self.bw.start_animation(items, ghosts)
        self.refresh()

    # ----------------------------------------------------- BoardWidget API
    def targets(self, src):
        return {m.to_square for m in self.board.legal_moves if m.from_square == src}

    def on_left_press(self, sq):
        self.bw.clear_marks()
        self._consumed = False
        self._was_selected = (self.selected == sq)
        if not self.enabled:
            return False
        if self.selected is not None and sq != self.selected and sq in self.targets(self.selected):
            src = self.selected
            self._consumed = True
            self.try_move(src, sq)
            return False
        if self.selected is not None and castle_target(self.board, self.selected, sq) != sq:
            src = self.selected                       # king selected, then own rook clicked = castle
            self._consumed = True
            self.try_move(src, sq)
            return False
        piece = self.board.piece_at(sq)
        if piece is not None and piece.color == self.board.turn:
            self.selected = sq
            self.refresh()
            return True
        self.selected = None
        self.refresh()
        return False

    def on_left_release(self, src, dst, dragged):
        if getattr(self, '_consumed', False):
            self._consumed = False
            return
        if not self.enabled:
            return
        if dragged:
            if dst is not None and dst != src and src is not None:
                self.try_move(src, dst)
            else:
                self.refresh()
            return
        if dst == src and getattr(self, '_was_selected', False):
            self.selected = None
            self.refresh()

    def on_right_release(self, start, end, color, global_pos):
        if start != end:
            self.bw.toggle_arrow(start, end, color)
        else:
            self.bw.toggle_highlight(start)

    def on_promotion(self, src, dst, ptype):
        if ptype is None:
            self.refresh()
            return
        move = chess.Move(src, dst, promotion=ptype)
        if move in self.board.legal_moves:
            self.selected = None
            self.on_move(move)
        else:
            self.refresh()

    # ------------------------------------------------------------ helpers
    def try_move(self, src, dst):
        piece = self.board.piece_at(src)
        if piece is None or piece.color != self.board.turn:
            self.refresh()
            return
        dst = castle_target(self.board, src, dst)          # king dropped onto its own rook = castle
        cands = [m for m in self.board.legal_moves if m.from_square == src and m.to_square == dst]
        if not cands:
            self.selected = None
            self.refresh()
            return
        if cands[0].promotion:
            self.selected = None
            self.bw.begin_promotion(src, dst, piece.color)
            self.refresh()
            return
        self.selected = None
        self.on_move(cands[0])


def castle_target(board, src, dst):
    """If the king is dragged/clicked onto one of its own rooks, return the castling destination square."""
    piece = board.piece_at(src)
    target = board.piece_at(dst)
    if piece is not None and target is not None and piece.piece_type == chess.KING and target.piece_type == chess.ROOK \
            and target.color == piece.color and chess.square_rank(src) == chess.square_rank(dst):
        kingside = chess.square_file(dst) > chess.square_file(src)
        cand = chess.square(6 if kingside else 2, chess.square_rank(src))
        if chess.Move(src, cand) in board.legal_moves:
            return cand
    return dst
