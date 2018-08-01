from itertools import product
from enum import Enum
from typing import Tuple, Optional, Set, FrozenSet


class Piece(Enum):
    KING = 'K'
    QUEEN = 'Q'
    ROOK = 'R'
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

        fen_color = fen.split(' ')[1]
        try:
            self._active_color = {'w': Color.WHITE, 'b': Color.BLACK}[fen_color]
        except KeyError:
            raise KeyError('Unexpected active color {}'.format(fen_color))

        self._castling_availability, self._en_passant_target = fen.split(' ')[2:4]
        self._halfmove_clock = int(fen.split(' ')[4])
        self._fullmove_number = int(fen.split(' ')[5])

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
        return '{} {} {} {} {} {}'.format(self.fen_pieces_from_board_array(self._board_array), self._active_color.value,
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
        targ_x, targ_y = self.square_str_to_xy(target)

        if 'x' in move_str:
            raise NotImplementedError('captures not implemented')
        else:
            if self._board_array[targ_y][targ_x] != '.':
                raise Exception('Illegal move: target occupied')

        orig_x = orig_y = None

        # find original square

        if piece == 'P':
            candidate_origins = self.find_pieces(Piece.PAWN, self._active_color)
            found = False
            for co in candidate_origins:
                if target in self.candidate_targets_from(co):
                    if found:
                        raise Exception('Ambiguous move')
                    orig_x, orig_y = self.square_str_to_xy(co)
                    found = True
            if not found:
                raise Exception('Illegal move')

            # set en-passant targets if pawn moved 2
            if orig_y == 6 and targ_y == 4 and self._active_color == Color.WHITE:
                new_en_passant_target = self.square_xy_to_str(orig_x, orig_y - 1)
            if orig_y == 1 and targ_y == 3 and self._active_color == Color.BLACK:
                new_en_passant_target = self.square_xy_to_str(orig_x, orig_y + 1)

            # all pawn moves reset halfmove clock
            reset_halfmove_clock = True

            # promotion
            if targ_y in (0, 7):
                # TODO implement promotion when it's actually specified
                raise Exception('Illegal move: must promote upon advancing to final rank')

        elif piece == 'R':
            orig_x = orig_y = None

            # find rook on same rank
            for fi, sq in enumerate(self._board_array[targ_y]):
                if sq == ('R' if self._active_color == Color.WHITE else 'r'):
                    orig_x, orig_y = fi, targ_y

            # find rook on same file
            for ri, sq in enumerate(tuple(zip(*self._board_array))[targ_x]):
                if sq == ('R' if self._active_color == Color.WHITE else 'r'):
                    orig_x, orig_y = targ_x, ri

        else:
            raise NotImplementedError('moving other pieces not implemented')

        # create new position

        new_board = [list(x) for x in self._board_array]
        # move piece
        new_board[orig_y][orig_x] = '.'
        new_board[targ_y][targ_x] = piece.upper() if self._active_color == Color.WHITE else piece.lower()
        # read pieces to FEN
        new_fen_pieces = self.fen_pieces_from_board_array(new_board)
        # switch color
        new_active_color = 'b' if self._active_color == Color.WHITE else 'w'
        # clear en passant if we didn't create new target
        new_en_passant_target = new_en_passant_target or '-'
        # increment numbers
        new_halfmove_clock = 0 if reset_halfmove_clock else self._halfmove_clock + 1
        new_fullmove_number = self._fullmove_number if self._active_color == Color.WHITE else self._fullmove_number + 1

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

    def find_pieces_xy(self, piece: Piece, color: Color) -> FrozenSet[tuple]:
        """
        >>> ps = Position().find_pieces_xy(Piece.BISHOP, Color.WHITE)
        >>> ps == {(2, 7), (5, 7)}
        True
        """
        char = piece.value.upper() if color == Color.WHITE else piece.value.lower()
        return frozenset((x, y) for x in range(8) for y in range(8) if self._board_array[y][x] == char)

    def find_pieces(self, piece: Piece, color: Color) -> FrozenSet[tuple]:
        """
        >>> ps = Position().find_pieces(Piece.BISHOP, Color.WHITE)
        >>> ps == {'c1', 'f1'}
        True
        """
        return frozenset(self.square_xy_to_str(*xy) for xy in self.find_pieces_xy(piece, color))

    def pieces_that_can_move_here(self, piece: Piece, target: str, color: Color) -> Tuple[str]:
        """Current locations of pieces that can move to target."""
        raise NotImplementedError

    def _look_xy(self, x, y) -> str:
        return self._board_array[y][x]

    def _look_sq(self, square_str) -> str:
        return self._look_xy(*self.square_str_to_xy(square_str))

    def _empty_xy(self, x, y) -> bool:
        return self._look_xy(x, y) == '.'

    def candidate_targets_from(self, origin: str) -> Optional[FrozenSet[str]]:
        """
        Return candidate targets for the piece in the given square.
        "Candidate targets" meaning squares where the piece could move if we do not take into account checks.

        Empty origin square returns None, and a non-empty square with no targets returns an empty tuple.
        """
        char = self._look_sq(origin)
        if char == '.':
            return

        piece_type = Piece(char.upper())
        color = Color.WHITE if char.isupper() else Color.BLACK

        candidates = set()

        x, y = self.square_str_to_xy(origin)

        if piece_type == Piece.PAWN:
            start_y = 6 if color == Color.WHITE else 1
            ydir = -1 if color == Color.WHITE else 1

            # moves straight ahead
            if self._empty_xy(x, y + ydir):
                candidates.add(self.square_xy_to_str(x, y + ydir))
                if y == start_y and self._empty_xy(x, y + 2*ydir):  # rank 2
                    candidates.add(self.square_xy_to_str(x, y + 2*ydir))

            # capturing moves
            for capt_xy in ((x-1, y+ydir), (x+1, y+ydir)):
                try:
                    if self._look_xy(*capt_xy).islower() and color == Color.WHITE:
                        candidates.add(self.square_xy_to_str(*capt_xy))
                    if self._look_xy(*capt_xy).isupper() and color == Color.BLACK:
                        candidates.add(self.square_xy_to_str(*capt_xy))
                except IndexError:
                    pass  # this happens when we go over the edge of the board

                if self._en_passant_target != '-' and capt_xy == self.square_str_to_xy(self._en_passant_target):
                    candidates.add(self._en_passant_target)

        elif piece_type == Piece.KNIGHT:
            pass

        return frozenset(candidates)


def parse_move(move_str: str):
    """
    Given a move in algebraic notation, return a dict describing it.

    >>> parse_move('Qe5') == {'target': 'e5', 'piece': 'Q'}
    True

    >>> parse_move('0-0-0') == {'castle': 'queenside'}
    True

    >>> parse_move('0-0') == {'castle': 'kingside'}
    True

    >>> parse_move('exd5') == {'piece': 'P', 'orig_file': 'e', 'capture': True, 'target': 'd5'}
    True

    >>> parse_move('Ze5') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: ...

    >>> parse_move('dxe8=Q+') == {
    ...     'piece': 'P', 'orig_file': 'd', 'capture': True, 'target': 'e8', 'promote': 'Q', 'check': True}
    True

    >>> parse_move('Be3xd4+') == {
    ...     'piece': 'B', 'orig_file': 'e', 'orig_rank': '3', 'capture': True, 'target': 'd4', 'check': True}
    True

    >>> parse_move('e3#') == {'piece': 'P', 'target': 'e3', 'checkmate': True}
    True

    >>> parse_move('e3+#') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: ...

    >>> parse_move(('e', '3')) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    TypeError: ...

    >>> parse_move('0-0-0-0') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: ...

    >>> parse_move('exxd4') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: ...

    >>> parse_move('ee6xd4') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: ...

    >>> parse_move('R4xe5') == {'piece': 'R', 'target': 'e5', 'orig_rank': '4', 'capture': True}
    True

    >>> parse_move('R4e5') == {'piece': 'R', 'target': 'e5', 'orig_rank': '4'}
    True

    >>> parse_move('Rae5') == {'piece': 'R', 'target': 'e5', 'orig_file': 'a'}
    True

    >>> parse_move('Bd4e5') == {'piece': 'B', 'target': 'e5', 'orig_rank': '4', 'orig_file': 'd'}
    True

    >>> parse_move('Bd4xe5') == {'piece': 'B', 'target': 'e5', 'orig_rank': '4', 'orig_file': 'd', 'capture': True}
    True

    >>> parse_move('Bzxd4') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: ...

    >>> parse_move('e8=Z') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: ...

    >>> parse_move('e3$$$') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: ...

    >>> parse_move('dxe8=Q') == {
    ...     'piece': 'P', 'orig_file': 'd', 'capture': True, 'target': 'e8', 'promote': 'Q'}
    True
    """

    d = dict()

    # let's make sure you don't pass lists or something stupid here
    if not isinstance(move_str, str):
        raise TypeError('Expected string')

    # castling
    if move_str[0] in 'O0':
        if move_str in ('O-O', '0-0'):
            castle_side = 'kingside'
        elif move_str in ('O-O-O', '0-0-0'):
            castle_side = 'queenside'
        else:
            raise ValueError('Unable to parse this one')
        return dict(castle=castle_side)


    # get piece
    if move_str[0] in 'KQRBNP':
        d['piece'] = move_str[0]
        move_str = move_str[1:]
    elif move_str[0] in 'abcdefgh':
        d['piece'] = 'P'
    else:
        raise ValueError('Unable to parse this one')

    # captures
    if 'x' in move_str:
        if move_str.count('x') != 1:
            raise ValueError('Unable to parse this one')
        d['capture'] = True
        move_str = move_str.replace('x', '')

        # before_x, move_str = move_str.split('x')
        # if len(before_x) == 2:
        #     d['orig_file'], d['orig_rank'] = before_x
        # else:
        #     if len(before_x) != 1:
        #         raise ValueError('Unable to parse this one')
        #     if before_x in 'abcdefgh':
        #         d['orig_file'] = before_x
        #     elif before_x in '12345678':
        #         d['orig_rank'] = before_x
        #     else:
        #         raise ValueError('Unable to parse this one')

    # find last 12345678 from string; that should be the target rank
    target_rank_index = None
    for i, c in reversed(tuple(enumerate(move_str))):
        if c in '12345678':
            target_rank_index = i
            break
    d['target'] = move_str[target_rank_index-1:target_rank_index+1]

    before_target, after_target = move_str[:target_rank_index-1], move_str[target_rank_index+1:]

    # disambiguating origin before target
    if before_target == '':
        pass
    elif len(before_target) == 1:
        if before_target in 'abcdefgh':
            d['orig_file'] = before_target
        elif before_target in '12345678':
            d['orig_rank'] = before_target
        else:
            raise ValueError('Unable to parse this one')
    elif len(before_target) == 2:
        d['orig_file'], d['orig_rank'] = before_target
    else:
        raise ValueError('Unable to parse this one')

    # whatever happens after the target square
    if after_target == '':
        pass
    elif after_target[0] in '+#=':
        # promotion
        if after_target[0] == '=':
            if after_target[1] in 'KQRBN':
                d['promote'] = after_target[1]
            else:
                raise ValueError('Unable to parse this one')
            remains = after_target[2:]
        else:
            remains = after_target
        # check/mate
        if remains == '+':
            d['check'] = True
        elif remains == '#':
            d['checkmate'] = True
        elif remains == '':
            pass
        else:
            raise ValueError('Unable to parse this one')
    else:
        raise ValueError('Unable to parse this one')

    return d
