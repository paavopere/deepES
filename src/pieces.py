from abc import ABCMeta, abstractmethod


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

    def conduct_move(self, x, y):
        raise NotImplementedError

    def move_is_legal(self, x, y):
        raise NotImplementedError

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