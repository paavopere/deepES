import unittest
from src.board import Board
from src.pieces import King, Queen, Rook, Bishop, Knight, Pawn, Piece


class TestPieces(unittest.TestCase):
    def setUp(self):
        self.w_pawn = Pawn(Piece.C_WHITE)
        self.w_knight = Knight(Piece.C_WHITE)
        self.w_bishop = Bishop(Piece.C_WHITE)
        self.w_rook = Rook(Piece.C_WHITE)
        self.w_queen = Queen(Piece.C_WHITE)
        self.w_king = King(Piece.C_WHITE)
        self.b_pawn = Pawn(Piece.C_BLACK)
        self.b_knight = Knight(Piece.C_BLACK)
        self.b_bishop = Bishop(Piece.C_BLACK)
        self.b_rook = Rook(Piece.C_BLACK)
        self.b_queen = Queen(Piece.C_BLACK)
        self.b_king = King(Piece.C_BLACK)

    def test_capture_sets(self):
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
        self.assertEqual(repr(self.b_queen), "black Queen")


class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board()

    def test_init_success(self):
        self.assertEqual(len(self.board.squares), 64)
        self.assertEqual(len(self.board.pieces), 16)