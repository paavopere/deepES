from itertools import product
from enum import Enum


class Piece(Enum):
    KING = 'K'
    QUEEN = 'Q'
    BISHOP = 'B'
    KNIGHT = 'N'
    PAWN = 'P'


class Color(Enum):
    WHITE = 'w'
    BLACK = 'b'


class Position:
    def __init__(self, fen=None):
        if fen is None:
            fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

        self._board_array = self.board_array_from_fen_pieces(fen.split(' ')[0])
        self._active_color, self._castling_availability, self._en_passant_target = fen.split(' ')[1:4]
        self._halfmove_clock = int(fen.split(' ')[4])
        self._fullmove_number = int(fen.split(' ')[5])

        if self._active_color not in ('w', 'b'):
            raise ValueError('Unexpected active color: {}'.format(self._active_color))

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.fen()))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.fen() == self.fen()

    @staticmethod
    def board_array_from_fen_pieces(fen_pieces):
        """
        According to '1. Piece placement' in
        https://en.wikipedia.org/w/index.php?title=Forsyth%E2%80%93Edwards_Notation&oldid=707127024#Definition
        """
        fen_ranks = fen_pieces.split('/')

        position = []
        for fr in fen_ranks:
            rank = []
            for square in fr:
                if square.isdigit():
                    rank.extend('.' * int(square))
                else:
                    rank.append(square)
            position.append(tuple(rank))

        return tuple(position)

    @staticmethod
    def fen_pieces_from_board_array(board_array):
        fen_pieces = ''
        for rank in board_array:
            empties = 0
            for square in rank:
                if square == '.':
                    empties += 1
                else:
                    if empties >= 1:
                        fen_pieces += str(empties)
                        empties = 0
                    fen_pieces += square
            if empties > 0:
                fen_pieces += str(empties)
            fen_pieces += '/'
        fen_pieces = fen_pieces[:-1]
        return fen_pieces

    def basic_board(self):
        """Human-readable basic visualization of the board at this position"""
        return '\n'.join(''.join(piece for piece in rank) for rank in self._board_array)

    def fen(self):
        """Forsyth-Edwards notation string of the position"""
        return '{} {} {} {} {} {}'.format(self.fen_pieces_from_board_array(self._board_array), self._active_color,
                                          self._castling_availability, self._en_passant_target, self._halfmove_clock,
                                          self._fullmove_number)

    def move(self, move_str):
        new_en_passant_target = None
        reset_halfmove_clock = False
        remove_castling_availability = None

        # get moved piece
        piece = move_str[0] if move_str[0] in 'KQRBNP' else 'P'

        # get target square
        target = None
        possible_targets = (''.join(z) for z in product('abcdefgh', '12345678'))
        for possible_target in possible_targets:
            if possible_target in move_str:
                target = possible_target
                break

        # target indices
        file_index = list('abcdefgh').index(target[0])
        rank_index = list('87654321').index(target[1])

        if 'x' in move_str:
            raise NotImplementedError('captures not implemented')
        else:
            if self._board_array[rank_index][file_index] != '.':
                raise Exception('Illegal move: target occupied')

        # find original square
        if piece == 'P':
            orig_file_index = orig_rank_index = None

            if self._active_color == 'w':
                if rank_index == 0:
                    raise NotImplementedError('Promotion not implemented (white)')
                if self._board_array[rank_index + 1][file_index] == 'P':  # pawn one behind target
                    orig_file_index, orig_rank_index = file_index, rank_index + 1
                elif self._board_array[rank_index + 2][file_index] == 'P':  # pawn two behind target
                    orig_file_index, orig_rank_index = file_index, rank_index + 2
                    if '87654321'[orig_rank_index] != '2':  # unexpected origin for pawn that moves 2
                        raise Exception('Illegal move')
                    new_en_passant_target = 'abcdefgh'[file_index] + '87654321'[rank_index + 1]
                else:
                    raise Exception('Illegal move')
            elif self._active_color == 'b':
                if rank_index == 7:
                    raise NotImplementedError('Promotion not implemented (black)')
                if self._board_array[rank_index - 1][file_index] == 'p':  # pawn one behind target
                    orig_file_index, orig_rank_index = file_index, rank_index - 1
                elif self._board_array[rank_index - 2][file_index] == 'p':  # pawn two behind target
                    orig_file_index, orig_rank_index = file_index, rank_index - 2
                    if '87654321'[orig_rank_index] != '7':  # unexpected origin for pawn that moves 2
                        raise Exception('Illegal move')
                    new_en_passant_target = 'abcdefgh'[file_index] + '87654321'[rank_index - 1]
                else:
                    raise Exception('Illegal move')

            reset_halfmove_clock = True

        elif piece == 'R':
            orig_file_index = orig_rank_index = None

            # find rook on same rank
            for fi, sq in enumerate(self._board_array[rank_index]):
                if sq == ('R' if self._active_color == 'w' else 'r'):
                    orig_file_index, orig_rank_index = fi, rank_index

            # find rook on same file
            for ri, sq in enumerate(tuple(zip(*self._board_array))[file_index]):
                if sq == ('R' if self._active_color == 'w' else 'r'):
                    orig_file_index, orig_rank_index = file_index, ri

        else:
            raise NotImplementedError('moving non-pawns not implemented')

        # create new position

        new_board = [list(x) for x in self._board_array]
        # move piece
        new_board[orig_rank_index][orig_file_index] = '.'
        new_board[rank_index][file_index] = piece.upper() if self._active_color == 'w' else piece.lower()
        # read pieces to FEN
        new_fen_pieces = self.fen_pieces_from_board_array(new_board)
        # switch color
        new_active_color = 'b' if self._active_color == 'w' else 'w'
        # clear en passant if we didn't create new target
        new_en_passant_target = new_en_passant_target or '-'
        # increment numbers
        new_halfmove_clock = 0 if reset_halfmove_clock else self._halfmove_clock + 1
        new_fullmove_number = self._fullmove_number if self._active_color == 'w' else self._fullmove_number + 1

        if not remove_castling_availability:
            new_castling_availability = self._castling_availability
        else:
            raise NotImplementedError('Yet to figure out how castling is invalidated')

        # construct new FEN and create Position
        new_fen = '{} {} {} {} {} {}'.format(new_fen_pieces, new_active_color, new_castling_availability,
                                             new_en_passant_target, new_halfmove_clock, new_fullmove_number)
        return Position(fen=new_fen)


    @staticmethod
    def square_str_to_xy(square_str):
        """
        >>> Position.square_str_to_xy('a1')
        (0, 7)
        """
        return list('abcdefgh').index(square_str[0]), list('87654321').index(square_str[1])

    @staticmethod
    def square_xy_to_str(x, y):
        """
        >>> Position.square_xy_to_str(7, 3)
        'h5'
        """
        return 'abcdefgh'[x] + '87654321'[y]

    def find_pieces_xy(self, piece: Piece, color: Color) -> tuple:
        """
        >>> Position().find_pieces_xy(Piece.BISHOP, Color.WHITE)
        ((2, 7), (5, 7))
        """
        char = piece.value.upper() if color == Color.WHITE else piece.value.lower()
        return tuple((x, y) for x in range(8) for y in range(8) if self._board_array[y][x] == char)


    def pieces_that_can_move_here(self, piece, target, color):

        if piece == Piece.PAWN:
            char = Piece.PAWN.value.upper() if color == Color.WHITE else Piece.PAWN.value.lower()
            candidates_xy = [(x, y) for x in range(8) for y in range(8) if self._board_array[y][x] == char]
            pass

        raise NotImplementedError
