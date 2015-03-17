
from src.pieces import King, Queen, Rook, Bishop, Knight, Pawn, Piece


class Board(object):
    """
    Represents a chess board that is inhabited by pieces.
    """
    def __init__(self):
        self.squares = {
            (x, y): None for x in range(1, 9) for y in range(1, 9)
        }

        self.setup()

    def setup(self):
        cool_pieces = (Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook)
        for i, p in enumerate(cool_pieces):
            self.squares[i + 1, 1] = p(Piece.C_WHITE)
            self.squares[i + 1, 2] = Pawn(Piece.C_WHITE)
            self.squares[i + 1, 7] = Pawn(Piece.C_BLACK)
            self.squares[i + 1, 8] = p(Piece.C_BLACK)

print(Board().squares)