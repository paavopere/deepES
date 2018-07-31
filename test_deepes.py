from textwrap import dedent
from deepes import Position, Piece, Color
import pytest
xfail = pytest.mark.xfail

STARTING_BOARD_ARRAY = (
    ('r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'),
    ('p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'),
    ('.', '.', '.', '.', '.', '.', '.', '.'),
    ('.', '.', '.', '.', '.', '.', '.', '.'),
    ('.', '.', '.', '.', '.', '.', '.', '.'),
    ('.', '.', '.', '.', '.', '.', '.', '.'),
    ('P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'),
    ('R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'),
)
BOARD_ARRAY_AFTER_E4 = (
    ('r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'),
    ('p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'),
    ('.', '.', '.', '.', '.', '.', '.', '.'),
    ('.', '.', '.', '.', '.', '.', '.', '.'),
    ('.', '.', '.', '.', 'P', '.', '.', '.'),
    ('.', '.', '.', '.', '.', '.', '.', '.'),
    ('P', 'P', 'P', 'P', '.', 'P', 'P', 'P'),
    ('R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'),
)
STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
FEN_AFTER_E4 = 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1'
FEN_AFTER_E3 = 'rnbqkbnr/pppppppp/8/8/8/4P3/PPPP1PPP/RNBQKBNR b KQkq - 0 1'
STARTING_BBOARD = dedent('''
    rnbqkbnr
    pppppppp
    ........
    ........
    ........
    ........
    PPPPPPPP
    RNBQKBNR
''').strip()
BBOARD_AFTER_E4 = dedent('''
    rnbqkbnr
    pppppppp
    ........
    ........
    ....P...
    ........
    PPPP.PPP
    RNBQKBNR
''').strip()


def test_position_initializes():
    assert type(Position()) == Position


def test_default_position_repr():
    assert repr(Position()) == 'Position({})'.format(repr(STARTING_FEN))


def test_init_board_array():
    assert Position()._board_array == STARTING_BOARD_ARRAY


def test_initializes_with_fen():
    assert Position(fen=STARTING_FEN)


def test_starting_fen_gives_starting_board_array():
    assert Position(fen=STARTING_FEN)._board_array == STARTING_BOARD_ARRAY


def test_board_array_from_fen_after_e4():
    assert Position(fen=FEN_AFTER_E4)._board_array == BOARD_ARRAY_AFTER_E4


def test_starting_basic_board():
    assert Position().basic_board() == STARTING_BBOARD


def test_basic_board_from_fen_after_e4():
    assert Position(fen=FEN_AFTER_E4).basic_board() == BBOARD_AFTER_E4


def test_starting_fen_gives_starting_fen():
    assert Position(fen=STARTING_FEN).fen() == STARTING_FEN


def test_default_gives_starting_fen():
    assert Position().fen() == STARTING_FEN


def test_fen_from_fen_after_e4():
    assert Position(fen=FEN_AFTER_E4).fen() == FEN_AFTER_E4


def test_position_equality():
    position_1 = Position()
    position_2 = Position()
    assert position_1 == position_2


def test_can_move():
    assert Position().move('e3')


def test_fen_after_move_e3():
    assert Position().move('e3').fen() == FEN_AFTER_E3


def test_equality_after_move_e3():
    assert Position().move('e3') == Position(FEN_AFTER_E3)


def test_both_pawns_can_advance():
    expected = 'rnbqkbnr/1ppppppp/8/p7/P7/8/1PPPPPPP/RNBQKBNR w KQkq - 0 3'
    assert Position().move('a3').move('a6').move('a4').move('a5').fen() == expected


def test_pawns_can_initially_advance_two():
    assert Position().move('e4').fen() == FEN_AFTER_E4

    pos = Position()
    pos = pos.move('a4')
    pos = pos.move('a5')
    expected_fen = 'rnbqkbnr/1ppppppp/8/p7/P7/8/1PPPPPPP/RNBQKBNR w KQkq a6 0 2'
    assert pos.fen() == expected_fen


def test_pawn_cannot_advance_three():
    with pytest.raises(Exception) as excinfo:
        Position().move('a5')
    assert str(excinfo.value) == 'Illegal move'

    with pytest.raises(Exception) as excinfo:
        Position().move('a4').move('c4')
    assert str(excinfo.value) == 'Illegal move'


def test_pawn_cannot_advance_two_after_advancing():
    pos = Position()
    pos = pos.move('e3')
    pos = pos.move('a6')
    with pytest.raises(Exception) as excinfo:
        pos.move('e5')
    assert str(excinfo.value) == 'Illegal move'
    pos = Position()
    pos = pos.move('e3')
    pos = pos.move('a6')
    pos = pos.move('e4')
    with pytest.raises(Exception) as excinfo:
        pos.move('a4')
    assert str(excinfo.value) == 'Illegal move'


def test_pawn_cannot_advance_into_occupied_square():
    pos = Position().move('e4').move('e5')
    with pytest.raises(Exception) as excinfo:
        pos.move('e5')
    assert 'Illegal move' in str(excinfo.value)


def test_pawn_cannot_regress():
    pos = Position().move('e4').move('e5')
    with pytest.raises(Exception) as excinfo:
        pos.move('e3')
    assert 'Illegal move' in str(excinfo.value)


def test_cannot_initialize_with_unexpected_active_color():
    with pytest.raises(KeyError) as excinfo:
        Position('rnbqkbnr/1ppppppp/8/p7/P7/8/1PPPPPPP/RNBQKBNR y KQkq a6 0 2')
    assert 'Unexpected active color' in str(excinfo.value)


@xfail
def test_promote():
    pos = Position('3qk3/P7/8/8/8/8/7p/3QK3 w - - 0 0')
    pos = pos.move('a8=Q')
    assert pos.fen() == 'Q2qk3/8/8/8/8/8/7p/3QK3 b - - 1 1'


@xfail
def test_promote_to_check():
    pos = Position('3qk3/P7/8/8/8/8/7p/3QK3 b - - 0 0')
    pos = pos.move('h1=Q+')
    assert pos.fen() == '3qk3/P7/8/8/8/8/8/3QK2q w - - 1 2'


def test_rook_move():
    pos = Position('rnbqkbnr/ppppp3/8/5ppp/7P/R7/PPPPPPP1/RNBQKBN1 w Qkq f6 0 4')
    pos = pos.move('Rd3')
    assert pos.fen() == 'rnbqkbnr/ppppp3/8/5ppp/7P/3R4/PPPPPPP1/RNBQKBN1 b Qkq - 1 4'


def test_rook_move2():
    pos = Position('8/8/1K1k3r/8/4r3/8/8/R6R w - - 0 32')
    pos = pos.move('Rh4')
    assert pos.fen() == '8/8/1K1k3r/8/4r2R/8/8/R7 b - - 1 32'


def test_rook_move_black():
    pos = Position('rnbqkbn1/ppppppp1/7r/7p/7P/5PP1/PPPPP3/RNBQKBNR b KQq - 0 4')
    pos = pos.move('Rc6')
    assert pos.fen() == 'rnbqkbn1/ppppppp1/2r5/7p/7P/5PP1/PPPPP3/RNBQKBNR w KQq - 1 5'


@xfail
def test_rook_move_no_jump_over_piece():
    pos = Position('8/8/1K1kr3/8/4r2R/8/8/R7 w - - 2 33')
    with pytest.raises(Exception) as excinfo:
        pos.move('Rb4')
    assert 'Illegal move' in str(excinfo.value)


@xfail
def test_pieces_that_can_move_here_not_implemented_lol():
    pos = Position()
    with pytest.raises(NotImplementedError):
        pos.pieces_that_can_move_here(Piece.PAWN, 'e3', Color.WHITE) == ('e2',)
