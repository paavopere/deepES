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
        """Setup the chess board (initialize pieces). Fails with AssertionError if the board is
        not empty."""
        assert len(self.pieces_in_play) == 0, "Cannot setup board if there are already " \
                                              "pieces in play"

        cool_pieces = (Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook)
        for i, p in enumerate(cool_pieces):
            self.create_piece_in_square(p, Piece.C_WHITE, (i + 1, 1))
            self.create_piece_in_square(p, Piece.C_BLACK, (i + 1, 8))
            self.create_piece_in_square(Pawn, Piece.C_WHITE, (i + 1, 2))
            self.create_piece_in_square(Pawn, Piece.C_BLACK, (i + 1, 7))

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
        for sq in self.squares:
            occupant = self.get_square(sq)
            if occupant is piece:
                assert loc is None, "Same piece found in multiple coordinates"
                loc = sq
        return loc

    def get_square(self, square):
        """
        Get the occupant of square.
            square: tuple (or similar) containing (x, y)
            Return: Piece occupying square
        """
        x, y = square
        if not (isinstance(x, int) and isinstance(y, int) and 1 <= x <= 8 and 1 <= y <= 8):
            raise ValueError("Invalid coordinates ({}, {})".format(x, y))
        return self._squares[(x, y)]

    def set_square(self, piece, square, forceful=False):
        """
        Set the occupant of square.
            square: tuple (or similar) containing (x, y)
            forceful: bool, default False. Whether we want to put the piece here, regardless of
                whether another piece already occupies the square.
            Raise: AssertionError if called without forceful, and the square is occupied.
        """
        x, y = square
        if not (isinstance(x, int) and isinstance(y, int) and 1 <= x <= 8 and 1 <= y <= 8):
            raise ValueError("Invalid coordinates ({}, {})".format(x, y))
        if not forceful:
            assert self.is_free(square), "Square ({}, {}) is already occupied".format(*square)

        self._squares[(x, y)] = piece

    def create_piece(self, piece_class, color):
        """
        Create a piece of piece_class with a certain color.
            Return: the created piece object.
        """
        if not issubclass(piece_class, Piece):
            raise TypeError("{} is not a piece class". format(piece_class))
        return piece_class(color, self)

    def create_piece_in_square(self, piece_class, color, square, forceful=False):
        """
        Try to create a piece of piece_class with a certain color in a square.
            piece_class: class of the piece
            color: color of the piece
            square: tuple (or similar) containing (x, y)
            forceful: bool, default False. Whether we want to put the piece here, regardless of
                whether another piece already occupies the square.

            Return: the created piece object
            Raise: AssertionError if called without forceful, and the square is occupied.
        """
        p = self.create_piece(piece_class, color)
        try:
            self.set_square(p, square, forceful=forceful)
        except:
            # yes, the piece is 100% gone, regardless of gc, if set_square was not successful
            del p
            raise
        return p

    def is_free(self, square):
        """Return True if square is free, False otherwise"""
        return self.get_square(square) is None

    @property
    def squares(self):
        """Set of all squares of the board as 2-tuples (x, y)"""
        return self._squares.keys()

    @property
    def pieces_in_play(self):
        """Set of all pieces currently in play (occupying a square)"""
        found_pieces = set()
        for sq in self.squares:
            occupant = self.get_square(sq)
            if occupant is not None:
                found_pieces.add(occupant)
        return found_pieces