from abc import ABCMeta, abstractmethod
from operator import sub, mul, add

class Piece(metaclass=ABCMeta):
    """
    A generic chess piece. Particular piece types inherit this class.
    """

    # Piece colors
    C_WHITE = 0
    C_BLACK = 1

    @abstractmethod
    def __init__(self, color, board):
        self.color = color
        if self.color not in (self.C_WHITE, self.C_BLACK):
            raise ValueError("Invalid color")

        self._board = board
        self._moves = None
        self._captures = None
        self._move_extends = False
        self._has_moved = False

    def __repr__(self):
        color_names = {
            self.C_BLACK: "black",
            self.C_WHITE: "white"
        }
        return "{} {}".format(color_names[self.color], self.__class__.__name__)

    def conduct_move(self, square):
        if not self.can_move_to_square(square):
            raise RuntimeError("Move is not legal.")
        else:
            # Empty original square
            self.board.set_square(None, self.location, forceful=True)
            # Place self onto the new square
            self.board.set_square(self, square)
            return True

    def can_move_to_square(self, target_square):
        if not target_square in self.board.squares:
            return False

        wanted_move = tuple(map(sub, target_square, self.location))
        if not (self.legal_regular_move(wanted_move) or self.legal_special_move(wanted_move)):
            return False
        return True

    def legal_regular_move(self, wanted_move):
        # Case where we "step once"
        if wanted_move in self._moves:
            return True

        # Case where we make an extended move; this is ugly.
        if self._move_extends:
            # Hard-coded range for what is the maximum distance we can move
            for i in range(1, 8):
                # find the step that we extend
                for mst in self._moves:
                    if tuple(map(mul, mst, (i, i))) == wanted_move:
                        # step found, check if locations in between are free
                        for j in range(1, i):
                            loc_in_between = tuple(map(add, self.location, map(mul, mst, (j, j))))
                            if not self.board.is_free(loc_in_between):
                                return False
                        return True

        # Criteria not satisfied
        return False

    def legal_special_move(self, move):
        """
        Return whether, considering environmental factors, input is a legal
        special move for this piece.

        Special move is something like double pawn move, en passant, castling,
        or promotion.

        The generic piece returns False; pieces
        with special moves shall override this.
        """
        return False

    @property
    def captures(self):
        # If there is no explicit capture set, moves will be used as the capture set
        if self._captures:
            return self._captures
        else:
            return self._moves

    @property
    def board(self):
        """
        Return the board object that this piece belongs to. If the piece is captured, it will still
        belong to the board (although its location is None).
        """
        return self._board

    @property
    def location(self):
        return self.board.location(self)

    @property
    def in_turn(self):
        return self.board.turn == self.color


class King(Piece):
    def __init__(self, color, board):
        super().__init__(color, board)

        self._moves = {
            (x, y) for x in (-1, 0, 1) for y in (-1, 0, 1)
        } - {(0, 0)}

        #TODO: Implement castling
        #TODO: Implement check and checkmate


class Queen(Piece):
    def __init__(self, color, board):
        super().__init__(color, board)

        self._move_extends = True

        self._moves = {
            (x, y) for x in (-1, 0, 1) for y in (-1, 0, 1)
        } - {(0, 0)}


class Rook(Piece):
    def __init__(self, color, board):
        super().__init__(color, board)

        self._move_extends = True

        self._moves = {
            (1, 0), (0, 1), (-1, 0), (0, -1)
        }

        #TODO: Implement castling


class Bishop(Piece):
    def __init__(self, color, board):
        super().__init__(color, board)

        self._move_extends = True

        self._moves = {
            (x, y) for x in (-1, 1) for y in (-1, 1)
        }


class Knight(Piece):
    def __init__(self, color, board):
        super().__init__(color, board)

        self._moves = {
            (x, y) for x in (-2, 2) for y in (-1, 1)
        } | {
            (x, y) for x in (-1, 1) for y in (-2, 2)
        }


class Pawn(Piece):
    def __init__(self, color, board):
        super().__init__(color, board)

        if color == Piece.C_WHITE:
            self._moves = {(0, 1)}
            self._captures = {(1, 1), (-1, 1)}
        elif color == Piece.C_BLACK:
            self._moves = {(0, -1)}
            self._captures = {(1, -1), (-1, -1)}

        #TODO: Implement en passant
        #TODO: Implement first move