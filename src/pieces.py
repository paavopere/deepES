"""
A docstring
"""
#TODO: All docstrings dude


class Piece(object):
    # Piece colors
    C_WHITE = 0
    C_BLACK = 1

    def __init__(self, color):
        self.color = color
        assert self.color in (self.C_WHITE, self.C_BLACK)
        
        self._moves = None
        self._captures = None
        self._move_extends = False

        self._square = None

    def __repr__(self):
        color_names = {
            self.C_BLACK: "black",
            self.C_WHITE: "white"
        }
        return "{} {}".format(color_names[self.color], self.__class__.__name__)

    @property
    def captures(self):
        # If there is no explicit capture set, moves will be used as the capture set
        if self._captures:
            return self._captures
        else:
            return self._moves


class King(Piece):
    def __init__(self, color):
        super().__init__(color)

        self._moves = {
            (x, y) for x in (-1, 0, 1) for y in (-1, 0, 1)
        } - {(0, 0)}

        #TODO: Implement castling
        #TODO: Implement check and checkmate


class Queen(Piece):
    def __init__(self, color):
        super().__init__(color)

        self._move_extends = True

        self._moves = {
            (x, y) for x in (-1, 0, 1) for y in (-1, 0, 1)
        } - {(0, 0)}


class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)

        self._move_extends = True

        self._moves = {
            (1, 0), (0, 1), (-1, 0), (0, -1)
        }

        #TODO: Implement castling


class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)

        self._move_extends = True

        self._moves = {
            (x, y) for x in (-1, 1) for y in (-1, 1)
        }


class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)

        self._moves = {
            (x, y) for x in (-2, 2) for y in (-1, 1)
        } | {
            (x, y) for x in (-1, 1) for y in (-2, 2)
        }


class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)

        if color == Piece.C_WHITE:
            self._moves = {(0, 1)}
            self._captures = {(1, 1), (-1, 1)}
        elif color == Piece.C_BLACK:
            self._moves = {(0, -1)}
            self._captures = {(1, -1), (-1, -1)}

        #TODO: Implement en passant
        #TODO: Implement first move


king = King(Piece.C_WHITE)
print(king._moves, type(king._moves))
knight = Knight(Piece.C_BLACK)
print(knight._moves, type(knight._moves))
pawn = Pawn(Piece.C_WHITE)

print(king)
print(king._moves)
print(king.captures)
print(pawn._moves)
print(pawn.captures)