import unittest
from src.board import Board
from src.pieces import King, Queen, Rook, Bishop, Knight, Pawn, Piece


class TestPieces(unittest.TestCase):
    def setUp(self):
        b = self.board = Board(setup_pieces=False)
        self.w_pawn = Pawn(Piece.C_WHITE, b)
        self.w_knight = Knight(Piece.C_WHITE, b)
        self.w_bishop = Bishop(Piece.C_WHITE, b)
        self.w_rook = Rook(Piece.C_WHITE, b)
        self.w_queen = Queen(Piece.C_WHITE, b)
        self.w_king = King(Piece.C_WHITE, b)
        self.b_pawn = Pawn(Piece.C_BLACK, b)
        self.b_knight = Knight(Piece.C_BLACK, b)
        self.b_bishop = Bishop(Piece.C_BLACK, b)
        self.b_rook = Rook(Piece.C_BLACK, b)
        self.b_queen = Queen(Piece.C_BLACK, b)
        self.b_king = King(Piece.C_BLACK, b)

    def test_capture_sets(self):
        """Test that capture sets are what we expected"""
        self.assertTrue(self.w_pawn.captures == {(1, 1), (-1, 1)})
        self.assertTrue(self.b_pawn.captures == {(1, -1), (-1, -1)})
        self.assertTrue(self.w_knight.captures == self.b_knight.captures
                        == {(1, 2), (-2, 1), (2, -1), (-1, 2), (2, 1), (-2, -1), (-1, -2), (1, -2)})
        self.assertTrue(self.w_king.captures == self.b_king.captures
                        == self.w_queen.captures == self.b_queen.captures
                        == {(0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, 0), (1, -1), (1, 1)})
        self.assertTrue(self.w_bishop.captures == self.b_bishop.captures
                        == {(1, 1), (1, -1), (-1, -1), (-1, 1)})
        self.assertTrue(self.w_rook.captures == self.b_rook.captures
                        == {(1, 0), (0, 1), (-1, 0), (0, -1)})

    def test_repr(self):
        """Test that we have an expected piece __repr__"""
        self.assertEqual(repr(self.b_queen), "black Queen")

    def test_unexpected_color(self):
        """Trying to initiate a piece with an unexpected color should raise ValueError"""
        with self.assertRaises(ValueError):
            Queen(color=123, board=self.board)

    def test_create_generic_piece(self):
        """Trying to initiate Piece() directly should raise TypeError"""
        with self.assertRaises(TypeError):
            Piece(Piece.C_BLACK, self.board)

    def test_location(self):
        """Test locations with the newly created pieces"""
        self.assertIs(self.w_rook.location, None)
        self.assertIs(self.w_knight.location, None)
        self.assertIs(self.b_pawn.location, None)
        self.assertIs(self.b_queen.location, None)

        # Put one of the pieces in a square and check location
        self.board.set_square(self.w_rook, (1, 1))
        self.assertEqual(self.w_rook.location, (1, 1))


class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board()

        self.magic_reference = (
            "['black Rook', 'black Knight', 'black Bishop', 'black Queen', 'black King', "
            "'black Bishop', 'black Knight', 'black Rook']\n['black Pawn', 'black Pawn', "
            "'black Pawn', 'black Pawn', 'black Pawn', 'black Pawn', 'black Pawn', 'black Pawn']\n"
            "['None', 'None', 'None', 'None', 'None', 'None', 'None', 'None']\n['None', 'None', "
            "'None', 'None', 'None', 'None', 'None', 'None']\n['None', 'None', 'None', 'None', "
            "'None', 'None', 'None', 'None']\n['None', 'None', 'None', 'None', 'None', 'None', "
            "'None', 'None']\n['white Pawn', 'white Pawn', 'white Pawn', 'white Pawn', "
            "'white Pawn', 'white Pawn', 'white Pawn', 'white Pawn']\n['white Rook', "
            "'white Knight', 'white Bishop', 'white Queen', 'white King', 'white Bishop', "
            "'white Knight', 'white Rook']")

    @staticmethod
    def magic_representation(board):
        """Return a string representation of pieces on board
         in a format similar to self.magic_reference"""
        return "\n".join([str(
            [repr(board.get_square((x, y))) for x in range(1, 9)]
        ) for y in range(1, 9)[::-1]])

    def test_init_squares(self):
        """Test that we have 64 squares on board"""
        self.assertEqual(len(self.board.squares), 64)

    def test_populate_pieces(self):
        """Test that pieces were populated correctly"""
        self.assertEqual(len(self.board.pieces_in_play), 32)
        for piece in self.board.pieces_in_play:
            self.assertIsInstance(piece, Piece)

        # Check that all pieces are in correct places through "magic reference"
        self.assertEqual(self.magic_representation(self.board), self.magic_reference)

    def test_unpopulated_board(self):
        """Test that we can create a board with no pieces"""
        self.assertEqual(len(Board(setup_pieces=False).pieces_in_play), 0)

    def test_location(self):
        """Test that Board.location method works as intended with valid inputs"""
        # identify some pieces created in setup
        black_king, white_queen = None, None
        for piece in self.board.pieces_in_play:
            if piece.__class__ == King and piece.color == Piece.C_BLACK:
                black_king = piece
            if piece.__class__ == Queen and piece.color == Piece.C_WHITE:
                white_queen = piece
        # assert their locations
        self.assertEqual(self.board.location(black_king), (5, 8))
        self.assertEqual(self.board.location(white_queen), (4, 1))

        # create a piece on this board without a location and check that its location is None
        new_piece = Knight(Piece.C_WHITE, self.board)
        self.assertIs(self.board.location(new_piece), None)

    def test_location_exceptions(self):
        # create a piece on a new board and check that calling its location on
        # this board raises ValueError
        foreign_piece = Pawn(Piece.C_BLACK, Board())
        with self.assertRaises(ValueError):
            self.board.location(foreign_piece)

        # check that a piece being in multiple locations raises AssertionError
        schrodingers_piece = Bishop(Piece.C_BLACK, self.board)
        self.board._squares[(1, 4)] = self.board._squares[(2, 4)] = schrodingers_piece
        with self.assertRaises(AssertionError):
            self.board.location(schrodingers_piece)

    def test_invalid_square_calls(self):
        """Test that getting or setting squares with unexpected x, y raise errors"""
        test_inputs = (
            (8, 9),
            (9, 8),
            (0, 1),
            (1, 0),
            (-1, -9),
            (1.2, 1),
            ("a", "b"),
            ("1", 2),
            (None, None)
        )
        for coord in test_inputs:
            with self.assertRaises(ValueError):
                self.board.get_square(coord)
            with self.assertRaises(ValueError):
                p = Bishop(Piece.C_BLACK, self.board)
                self.board.set_square(p, coord)

    def test_create_piece_in_square(self):
        # regular working case
        sq = (3, 4)
        p = self.board.create_piece_in_square(Pawn, Piece.C_BLACK, sq)
        self.assertIs(p, self.board.get_square(sq))

        # meaningless input
        with self.assertRaises(TypeError):
            self.board.create_piece_in_square(1, 2, 3, 4)

        # invalid square
        with self.assertRaises(ValueError):
            self.board.create_piece_in_square(Rook, Piece.C_BLACK, (9, 9), True)

        # occupied square after init
        sq = (1, 1)
        with self.assertRaises(AssertionError):
            self.board.create_piece_in_square(Rook, Piece.C_BLACK, sq)

        # previously occupied square with forceful
        p = self.board.create_piece_in_square(Rook, Piece.C_BLACK, sq, True)
        self.assertIs(p, self.board.get_square(sq))

    def test_some_moves(self):
        # white pawn 1 forward
        self.assertTrue(
            self.board.get_square((1, 2)).conduct_move((1, 3)))
        # black pawn 1 forward
        self.assertTrue(
            self.board.get_square((1, 7)).conduct_move((1, 6)))

        # white pawn 2 forward
        self.assertTrue(
            self.board.get_square((3, 2)).conduct_move((3, 4)))

    def test_illegal_move(self):
        # white pawn 3 forward fails
        with self.assertRaises(RuntimeError):
            self.board.get_square((2, 2)).conduct_move((2, 5))
