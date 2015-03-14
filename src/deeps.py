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

        self.square = None

        # Pieces that are not explicitly multi_move-enabled will have
        # multi_move=False
        self.multi_move = getattr(self, 'multi_move', False)
        # Pieces that do not have separate captures set will have moves set
        # double as the captures set
        self.captures = getattr(self, 'captures', getattr(self, 'moves', {}))

    def __repr__(self):
        return "{} {}".format("White" if self.color == self.C_WHITE else "Black",
                              self.__class__.__name__)


class King(Piece):
    def __init__(self, color):
        self.moves = {
            (x, y) for x in (-1, 0, 1) for y in (-1, 0, 1)
        } - {(0, 0)}
        super().__init__(color)
        #TODO: Implement castling
        #TODO: Implement check and checkmate


class Queen(Piece):
    def __init__(self, color):
        self.moves = {
            (x, y) for x in (-1, 0, 1) for y in (-1, 0, 1)
        } - {(0, 0)}
        self.multi_move = True
        super().__init__(color)


class Rook(Piece):
    def __init__(self, color):
        self.moves = {
            (1, 0), (0, 1), (-1, 0), (0, -1)
        }
        self.multi_move = True
        super().__init__(color)
        #TODO: Implement castling


class Bishop(Piece):
    def __init__(self, color):
        self.moves = {
            (x, y) for x in (-1, 1) for y in (-1, 1)
        }
        self.multi_move = True
        super().__init__(color)


class Knight(Piece):
    def __init__(self, color):
        self.moves = {
            (x, y) for x in (-2, 2) for y in (-1, 1)
        } | {
            (x, y) for x in (-1, 1) for y in (-2, 2)
        }
        super().__init__(color)


class Pawn(Piece):
    def __init__(self, color):
        if color == Piece.C_WHITE:
            self.moves = {(0, 1)}
            self.captures = {(1, 1), (-1, 1)}
        elif color == Piece.C_BLACK:
            self.moves = {(0, -1)}
            self.captures = {(1, -1), (-1, -1)}
        super().__init__(color)
        #TODO: Implement en passant


king = King(Piece.C_WHITE)
print(king.moves, type(king.moves))
knight = Knight(Piece.C_BLACK)
print(knight.moves, type(knight.moves))