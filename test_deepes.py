from deepes import Position


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


def test_starting_board_array():
    assert Position.starting_board_array() == STARTING_BOARD_ARRAY


def test_init_board_array():
    assert Position().board_array == STARTING_BOARD_ARRAY


def test_initializes_with_fen():
    assert Position(fen=STARTING_FEN)


def test_starting_fen_gives_starting_board_array():
    assert Position(fen=STARTING_FEN).board_array == STARTING_BOARD_ARRAY


def test_board_array_from_fen_after_e4():
    assert Position(fen=FEN_AFTER_E4).board_array == BOARD_ARRAY_AFTER_E4


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
