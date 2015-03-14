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
        
        self.moves = None
        self.captures = None
        self.move_extends = False

        self.square = None

    def __repr__(self):
        return "{} {}".format("White" if self.color == self.C_WHITE else "Black",
                              self.__class__.__name__)


class King(Piece):
    def __init__(self, color):
        super().__init__(color)

        self.moves = {
            (x, y) for x in (-1, 0, 1) for y in (-1, 0, 1)
        } - {(0, 0)}

        #TODO: Implement castling
        #TODO: Implement check and checkmate


class Queen(Piece):
    def __init__(self, color):
        super().__init__(color)

        self.move_extends = True

        self.moves = {
            (x, y) for x in (-1, 0, 1) for y in (-1, 0, 1)
        } - {(0, 0)}


class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)

        self.move_extends = True

        self.moves = {
            (1, 0), (0, 1), (-1, 0), (0, -1)
        }

        #TODO: Implement castling


class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)

        self.move_extends = True

        self.moves = {
            (x, y) for x in (-1, 1) for y in (-1, 1)
        }


class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)

        self.moves = {
            (x, y) for x in (-2, 2) for y in (-1, 1)
        } | {
            (x, y) for x in (-1, 1) for y in (-2, 2)
        }


class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)

        if color == Piece.C_WHITE:
            self.moves = {(0, 1)}
            self.captures = {(1, 1), (-1, 1)}
        elif color == Piece.C_BLACK:
            self.moves = {(0, -1)}
            self.captures = {(1, -1), (-1, -1)}

        #TODO: Implement en passant
        #TODO: Implement first move


king = King(Piece.C_WHITE)
print(king.moves, type(king.moves))
knight = Knight(Piece.C_BLACK)
print(knight.moves, type(knight.moves))