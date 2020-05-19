from itertools import product
from enum import Enum
from typing import Optional, FrozenSet


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
        return '{} {} {} {} {} {}'.format(
            self.fen_pieces_from_board_array(self._board_array),
            self._active_color.value,
            self._castling_availability,
            self._en_passant_target,
            self._halfmove_clock,
            self._fullmove_number,
        )

    def move(self, move_str):
        new_en_passant_target = None
        reset_halfmove_clock = False
        remove_castling_availability = None

        parsed = parse_move(move_str)

        if parsed['castle'] is not None:
            raise NotImplementedError('castling not implemented')
        if parsed['promote'] is not None:
            raise NotImplementedError('promotion not implemented')

        piece = Piece(parsed['piece'])
        target = parsed['target']
        targ_x, targ_y = self.square_str_to_xy(target)

        # origin coordinates can be None, or they can be specified in move string
        orig_x = orig_y = None
        if parsed['orig_file'] is not None:
            orig_x = list('abcdefgh').index(parsed['orig_file'])
        if parsed['orig_rank'] is not None:
            orig_y = list('87654321').index(parsed['orig_rank'])

        if parsed['capture']:
            raise NotImplementedError('captures not implemented')
        else:
            if not self._empty_xy(targ_x, targ_y):
                raise Exception('Illegal move: target occupied')

        possible_origins = set(
            self.pieces_that_can_move_here(
                target=target, piece=piece, color=self._active_color
            )
        )

        # if origin rank/file was specified, discard possible origins that do not match
        remove_origins = set()
        if orig_x is not None:
            for po in possible_origins:
                if self.square_str_to_xy(po)[0] != orig_x:
                    remove_origins.add(po)
        if orig_y is not None:
            for po in possible_origins:
                if self.square_str_to_xy(po)[1] != orig_y:
                    remove_origins.add(po)
        possible_origins -= remove_origins

        # if we have an unambiguous origin at this point, we're good
        if len(possible_origins) == 0:
            raise Exception('Illegal move: no possible origins')
        elif len(possible_origins) > 1:
            raise Exception('Illegal move: ambiguous origin')
        else:
            orig_x, orig_y = self.square_str_to_xy(possible_origins.pop())

        if piece == Piece.PAWN:
            # set en-passant targets if pawn moved 2
            if orig_y == 6 and targ_y == 4 and self._active_color == Color.WHITE:
                new_en_passant_target = self.square_xy_to_str(orig_x, orig_y - 1)
            if orig_y == 1 and targ_y == 3 and self._active_color == Color.BLACK:
                new_en_passant_target = self.square_xy_to_str(orig_x, orig_y + 1)
            # all pawn moves reset halfmove clock
            reset_halfmove_clock = True
            # promotion
            if targ_y in (0, 7) and parsed['promote'] is None:
                # TODO implement promotion when it's actually specified
                raise Exception(
                    'Illegal move: must promote upon advancing to final rank'
                )

        # All king moves and rook moves from corners set the `remove_castling_availability`
        # variable, regardless of whether it's already been removed. This works assuming that we
        # haven't set up impossible positions and do not care about carrying over the impossible
        # castling availability.
        if piece == Piece.KING:
            remove_castling_availability = (
                'KQ' if self._active_color == Color.WHITE else 'kq'
            )
        if piece == Piece.ROOK:
            origin_effect_on_castling = dict(a1='Q', h1='K', a8='q', h8='k')
            remove_castling_availability = origin_effect_on_castling.get(
                self.square_xy_to_str(orig_x, orig_y)
            )

        # create new position

        new_board = [list(x) for x in self._board_array]
        # move piece
        new_board[orig_y][orig_x] = '.'
        new_board[targ_y][targ_x] = (
            piece.value.upper()
            if self._active_color == Color.WHITE
            else piece.value.lower()
        )
        # read pieces to FEN
        new_fen_pieces = self.fen_pieces_from_board_array(new_board)
        # switch color
        new_active_color = 'b' if self._active_color == Color.WHITE else 'w'
        # clear en passant if we didn't create new target
        new_en_passant_target = new_en_passant_target or '-'
        # increment numbers
        new_halfmove_clock = 0 if reset_halfmove_clock else self._halfmove_clock + 1
        new_fullmove_number = (
            self._fullmove_number
            if self._active_color == Color.WHITE
            else self._fullmove_number + 1
        )

        if not remove_castling_availability:
            new_castling_availability = self._castling_availability
        else:
            new_castling_availability = (
                ''.join(
                    char
                    for char in self._castling_availability
                    if char not in remove_castling_availability
                )
                or '-'
            )

        # construct new FEN and create Position
        new_fen = '{} {} {} {} {} {}'.format(
            new_fen_pieces,
            new_active_color,
            new_castling_availability,
            new_en_passant_target,
            new_halfmove_clock,
            new_fullmove_number,
        )
        return Position(fen=new_fen)

    @staticmethod
    def square_str_to_xy(square_str):
        """
        >>> Position.square_str_to_xy('a1')
        (0, 7)
        """
        return (
            list('abcdefgh').index(square_str[0]),
            list('87654321').index(square_str[1]),
        )

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
        return frozenset(
            (x, y)
            for x in range(8)
            for y in range(8)
            if self._board_array[y][x] == char
        )

    def find_pieces(self, piece: Piece, color: Color) -> FrozenSet[str]:
        """
        >>> ps = Position().find_pieces(Piece.BISHOP, Color.WHITE)
        >>> ps == {'c1', 'f1'}
        True
        """
        return frozenset(
            self.square_xy_to_str(*xy) for xy in self.find_pieces_xy(piece, color)
        )

    def pieces_that_can_move_here(
        self, piece: Piece, target: str, color: Color
    ) -> FrozenSet[str]:
        """Current locations of pieces that can move to target, not taking checks into account."""
        origins = set()
        candidate_origins = self.find_pieces(piece, color)
        for co in candidate_origins:
            if target in self.candidate_targets_from(co):
                origins.add(co)
        return frozenset(origins)

    def _look_xy(self, x, y) -> str:
        """Find character occupying xy"""
        return self._board_array[y][x]

    def _look_sq(self, square_str) -> str:
        """Find character occupying square"""
        return self._look_xy(*self.square_str_to_xy(square_str))

    def _empty_xy(self, x, y) -> bool:
        """Is xy empty?"""
        return self._look_xy(x, y) == '.'

    @staticmethod
    def _xy_on_board(x, y) -> bool:
        """Does xy exist on board?"""
        return 0 <= x <= 7 and 0 <= y <= 7

    def candidate_targets_from(self, origin: str) -> Optional[FrozenSet[str]]:
        """
        Return candidate targets for the piece in the given square. "Candidate targets" meaning
        squares where the piece could move if we do not take into account checks.

        Empty origin square returns None, and a non-empty square with no targets returns an
        empty frozenset.
        """
        char = self._look_sq(origin)
        if char == '.':
            return

        piece_type = Piece(char.upper())
        color = Color.WHITE if char.isupper() else Color.BLACK

        candidates = set()

        x, y = self.square_str_to_xy(origin)

        # chains of positions a bishop, rook or queen moves in a single direction
        horizontal_pos = ((d, 0) for d in range(1, 8))
        horizontal_neg = ((-d, 0) for d in range(1, 8))
        vertical_pos = ((0, d) for d in range(1, 8))
        vertical_neg = ((0, -d) for d in range(1, 8))
        diagonal_pos_pos = ((d, d) for d in range(1, 8))
        diagonal_pos_neg = ((d, -d) for d in range(1, 8))
        diagonal_neg_pos = ((-d, d) for d in range(1, 8))
        diagonal_neg_neg = ((-d, -d) for d in range(1, 8))

        if piece_type == Piece.PAWN:
            start_y = 6 if color == Color.WHITE else 1
            dy = -1 if color == Color.WHITE else 1

            # moves straight ahead
            if self._empty_xy(x, y + dy):
                candidates.add(self.square_xy_to_str(x, y + dy))
                if y == start_y and self._empty_xy(x, y + 2 * dy):  # rank 2
                    candidates.add(self.square_xy_to_str(x, y + 2 * dy))

            # capturing moves
            for pxy in ((x - 1, y + dy), (x + 1, y + dy)):
                if self._xy_on_board(*pxy):
                    if self._look_xy(*pxy).islower() and color == Color.WHITE:
                        candidates.add(self.square_xy_to_str(*pxy))
                    if self._look_xy(*pxy).isupper() and color == Color.BLACK:
                        candidates.add(self.square_xy_to_str(*pxy))

                if self._en_passant_target != '-' and pxy == self.square_str_to_xy(
                    self._en_passant_target
                ):
                    candidates.add(self._en_passant_target)

        elif piece_type == Piece.KNIGHT:
            possible_xys = (
                (x + 1, y + 2),
                (x + 1, y - 2),
                (x + 2, y + 1),
                (x + 2, y - 1),
                (x - 1, y + 2),
                (x - 1, y - 2),
                (x - 2, y + 1),
                (x - 2, y - 1),
            )
            for pxy in possible_xys:
                if not self._xy_on_board(*pxy):
                    continue
                if self._empty_xy(*pxy):
                    candidates.add(self.square_xy_to_str(*pxy))
                # capturing moves
                elif (self._look_xy(*pxy).islower() and color == Color.WHITE) or (
                    self._look_xy(*pxy).isupper() and color == Color.BLACK
                ):
                    candidates.add(self.square_xy_to_str(*pxy))

        elif piece_type == Piece.BISHOP:
            for direction_displacement_seq in (
                diagonal_pos_pos,
                diagonal_pos_neg,
                diagonal_neg_pos,
                diagonal_neg_neg,
            ):
                for dx, dy in direction_displacement_seq:
                    pxy = x + dx, y + dy
                    if not self._xy_on_board(*pxy):
                        break
                    if self._empty_xy(*pxy):
                        candidates.add(self.square_xy_to_str(*pxy))
                    else:
                        if (self._look_xy(*pxy).islower() and color == Color.WHITE) or (
                            self._look_xy(*pxy).isupper() and color == Color.BLACK
                        ):
                            candidates.add(self.square_xy_to_str(*pxy))
                        break

        elif piece_type == Piece.ROOK:
            for direction_displacement_seq in (
                horizontal_pos,
                horizontal_neg,
                vertical_pos,
                vertical_neg,
            ):
                for dx, dy in direction_displacement_seq:
                    pxy = x + dx, y + dy
                    if not self._xy_on_board(*pxy):
                        break
                    if self._empty_xy(*pxy):
                        candidates.add(self.square_xy_to_str(*pxy))
                    else:
                        if (self._look_xy(*pxy).islower() and color == Color.WHITE) or (
                            self._look_xy(*pxy).isupper() and color == Color.BLACK
                        ):
                            candidates.add(self.square_xy_to_str(*pxy))
                        break

        elif piece_type == Piece.QUEEN:
            for direction_displacement_seq in (
                horizontal_pos,
                horizontal_neg,
                vertical_pos,
                vertical_neg,
                diagonal_pos_pos,
                diagonal_pos_neg,
                diagonal_neg_pos,
                diagonal_neg_neg,
            ):
                for dx, dy in direction_displacement_seq:
                    pxy = x + dx, y + dy
                    if not self._xy_on_board(*pxy):
                        break
                    if self._empty_xy(*pxy):
                        candidates.add(self.square_xy_to_str(*pxy))
                    else:
                        if (self._look_xy(*pxy).islower() and color == Color.WHITE) or (
                            self._look_xy(*pxy).isupper() and color == Color.BLACK
                        ):
                            candidates.add(self.square_xy_to_str(*pxy))
                        break

        elif piece_type == Piece.KING:
            displacements = set(product((-1, 0, 1), repeat=2))
            displacements.remove((0, 0))
            for dx, dy in displacements:
                pxy = x + dx, y + dy
                if not self._xy_on_board(*pxy):
                    continue
                if self._empty_xy(*pxy):
                    candidates.add(self.square_xy_to_str(*pxy))
                # capturing moves
                elif (self._look_xy(*pxy).islower() and color == Color.WHITE) or (
                    self._look_xy(*pxy).isupper() and color == Color.BLACK
                ):
                    candidates.add(self.square_xy_to_str(*pxy))

        return frozenset(candidates)


# TODO: move most of these doctests elsewhere
def parse_move(move_str: str) -> dict:
    """
    Given a move in algebraic notation, return a dict describing it.

    >>> parse_move('Qe5') == {
    ...     'piece': 'Q', 'target': 'e5',
    ...     'orig_rank': None, 'orig_file': None, 'capture': False,
    ...     'castle': None, 'check': False, 'checkmate': False,
    ...     'promote': None
    ... }
    True

    >>> parse_move('0-0-0')['castle']
    'queenside'

    >>> parse_move('O-O')['castle']
    'kingside'

    >>> m = parse_move('exd5')
    >>> m['piece'], m['orig_file'], m['capture'], m['target']
    ('P', 'e', True, 'd5')

    >>> parse_move('Ze5') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: ...

    >>> parse_move('dxe8=Q+') == {
    ...     'piece': 'P', 'orig_file': 'd', 'capture': True, 'target': 'e8',
    ...     'promote': 'Q', 'check': True,
    ...     'orig_rank': None, 'castle': None, 'checkmate': False}
    True

    >>> m = parse_move('Be3xd4+')
    >>> (m['piece'], m['orig_file'], m['orig_rank'], m['capture'],
    ...  m['target'], m['check'])
    ('B', 'e', '3', True, 'd4', True)

    >>> parse_move('e3#')['checkmate']
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

    >>> parse_move('R4xe5') == {
    ...     'piece': 'R', 'target': 'e5', 'orig_rank': '4', 'capture': True,
    ...     'orig_file': None, 'check': False, 'checkmate': False,
    ...     'promote': None, 'castle': None }
    True

    >>> parse_move('R4e5') == {
    ...     'piece': 'R', 'target': 'e5', 'orig_rank': '4', 'capture': False,
    ...     'orig_file': None, 'check': False, 'checkmate': False,
    ...     'promote': None, 'castle': None}
    True

    >>> parse_move('Rae5')['orig_file']
    'a'

    >>> m = parse_move('Bd4e5')
    >>> m['orig_file'], m['orig_rank']
    ('d', '4')

    >>> parse_move('Bd4xe5') == {'piece': 'B', 'orig_rank': '4', 'orig_file': 'd', 'capture': True, 'target': 'e5',
    ...     'castle': None, 'check': False, 'checkmate': False, 'promote': None}
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

    >>> parse_move('e9') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: ...

    >>> parse_move('dxe8=Q') == {'piece': 'P', 'orig_file': 'd', 'capture': True, 'target': 'e8', 'promote': 'Q',
    ...     'orig_rank': None, 'castle': None, 'check': False, 'checkmate': False}
    True
    """

    d = dict(
        piece=None,
        orig_rank=None,
        orig_file=None,
        capture=False,
        target=None,
        castle=None,
        check=False,
        checkmate=False,
        promote=None,
    )

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
        d['castle'] = castle_side
        return d

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

    # find last 12345678 from string; that should be the target rank
    target_rank_index = None
    for i, c in reversed(tuple(enumerate(move_str))):
        if c in '12345678':
            target_rank_index = i
            break
    if target_rank_index is None:
        raise ValueError('Unable to parse this one')
    d['target'] = move_str[target_rank_index - 1 : target_rank_index + 1]

    before_target, after_target = (
        move_str[: target_rank_index - 1],
        move_str[target_rank_index + 1 :],
    )

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
