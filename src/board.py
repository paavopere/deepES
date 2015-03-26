from src.pieces import King, Queen, Rook, Bishop, Knight, Pawn, Piece


class Board:
    """
    A chess board that is inhabited by pieces.
    """

    def __init__(self, setup_pieces=True):
        self._squares = {
            (x, y): None for x in range(1, 9) for y in range(1, 9)
        }

        if setup_pieces:
            self.setup()

    def setup(self):
        cool_pieces = (Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook)
        for i, p in enumerate(cool_pieces):
            self.set_square(p(Piece.C_WHITE, self), i + 1, 1)
            self.set_square(Pawn(Piece.C_WHITE, self), i + 1, 2)
            self.set_square(Pawn(Piece.C_BLACK, self), i + 1, 7)
            self.set_square(p(Piece.C_BLACK, self), i + 1, 8)

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
            occupant = self.get_square(*square)
            if occupant is piece:
                assert loc is None, "Same piece found in multiple coordinates"
                loc = square
        return loc

    def get_square(self, x, y):
        """Return the occupant of square (x, y)"""
        if not (isinstance(x, int) and isinstance(y, int) and 1 <= x <= 8 and 1 <= y <= 8):
            raise ValueError("Invalid coordinates ({}, {})".format(x, y))
        return self._squares[(x, y)]

    def set_square(self, piece, x, y):
        """Set the occupant of square (x, y)"""
        if not (isinstance(x, int) and isinstance(y, int) and 1 <= x <= 8 and 1 <= y <= 8):
            raise ValueError("Invalid coordinates ({}, {})".format(x, y))
        self._squares[(x, y)] = piece

    def create_piece(self, piece_class, color):
        if not issubclass(piece_class, Piece):
            raise TypeError("{} is not a piece class". format(piece_class))
        return piece_class(color, self)

    @property
    def squares(self):
        """Set of all squares of the board as 2-tuples (x, y)"""
        return self._squares.keys()

    @property
    def pieces(self):
        """Set of all pieces currently in play (occupying a square)"""
        found_pieces = set()
        for square in self.squares:
            occupant = self.get_square(*square)
            if occupant is not None:
                found_pieces.add(occupant)
        return found_pieces