
from src.pieces import King, Queen, Rook, Bishop, Knight, Pawn, Piece


class Board(object):
    """
    A chess board that is inhabited by pieces.
    """
    def __init__(self, setup_pieces=True):
        self.squares = {
            (x, y): None for x in range(1, 9) for y in range(1, 9)
        }

        if setup_pieces:
            self.setup()

    def setup(self):
        cool_pieces = (Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook)
        for i, p in enumerate(cool_pieces):
            self.squares[i + 1, 1] = p(Piece.C_WHITE, self)
            self.squares[i + 1, 2] = Pawn(Piece.C_WHITE, self)
            self.squares[i + 1, 7] = Pawn(Piece.C_BLACK, self)
            self.squares[i + 1, 8] = p(Piece.C_BLACK, self)

    def location(self, piece):
        """
        The location of a piece on this board.

        Return: tuple (x, y) if the piece is found on this board.
        Return: None if the piece is not found on this board
        Raise: ValueError if this is not the piece's board.
        Raise: AssertionError if the piece is found in multiple coordinates.
        """
        if piece.board is not self:
            raise ValueError("This is not the piece's ({0}) board".format(piece))
        loc = None
        for square in self.squares:
            occupant = self.squares[square]
            if occupant is piece:
                assert loc is None, "Same piece found in multiple coordinates"
                loc = square
        return loc

    @property
    def pieces(self):
        """Set of all pieces currently in play (occupying a square)"""
        found_pieces = set()
        for square in self.squares:
            occupant = self.squares[square]
            if occupant is not None:
                found_pieces.add(occupant)
        return found_pieces