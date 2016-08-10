from deepes import Position
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
STARTING_BBOARD = ('rnbqkbnr\n'
                   'pppppppp\n'
                   '........\n'
                   '........\n'
                   '........\n'
                   '........\n'
                   'PPPPPPPP\n'
                   'RNBQKBNR')
BBOARD_AFTER_E4 = ('rnbqkbnr\n'
                   'pppppppp\n'
                   '........\n'
                   '........\n'
                   '....P...\n'
                   '........\n'
                   'PPPP.PPP\n'
                   'RNBQKBNR')


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


@xfail
def test_pawn_cannot_advance_into_occupied_square():
    assert False
