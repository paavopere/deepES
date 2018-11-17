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


def test_cannot_initialize_with_unexpected_active_color():
    with pytest.raises(KeyError) as excinfo:
        Position('rnbqkbnr/1ppppppp/8/p7/P7/8/1PPPPPPP/RNBQKBNR y KQkq a6 0 2')
    assert 'Unexpected active color' in str(excinfo.value)


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


@xfail
def test_pawn_capture():
    pos = Position('rnbqkbnr/pppp1ppp/8/4p3/3P4/4P3/PPP2PPP/RNBQKBNR b KQkq - 0 2') \
        .move('exd4')
    assert pos.fen() == 'rnbqkbnr/pppp1ppp/8/8/3p4/4P3/PPP2PPP/RNBQKBNR w KQkq - 0 3'


@xfail
def test_pawn_capture_must_specify_origin():
    pos = Position('rnbqkbnr/pppp1ppp/8/4p3/3P4/4P3/PPP2PPP/RNBQKBNR b KQkq - 0 2')
    with pytest.raises(Exception) as excinfo:
        pos.move('xd4')
    assert 'Illegal move' in str(excinfo.value)


@xfail
def test_pawn_capture_en_passant():
    pos = Position('rnbqkbnr/pppppp1p/6p1/6P1/8/8/PPPPPP1P/RNBQKBNR b KQkq - 0 2') \
        .move('f5').move('gxf6')
    assert pos.fen() == 'rnbqkbnr/ppppp2p/5Pp1/8/8/8/PPPPPP1P/RNBQKBNR b KQkq - 0 3'


def test_pawn_cannot_advance_three():
    with pytest.raises(Exception) as excinfo:
        Position().move('a5')
    assert 'Illegal move' in str(excinfo.value)

    with pytest.raises(Exception) as excinfo:
        Position().move('a4').move('c4')
    assert 'Illegal move' in str(excinfo.value)


def test_pawn_cannot_advance_two_after_advancing():
    pos = Position().move('e3').move('a6')
    with pytest.raises(Exception) as excinfo:
        pos.move('e5')
    assert 'Illegal move' in str(excinfo.value)
    pos = Position().move('e3').move('a6').move('e4')
    with pytest.raises(Exception) as excinfo:
        pos.move('a4')
    assert 'Illegal move' in str(excinfo.value)


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


def test_must_promote():
    pos = Position('3qk3/P7/8/8/8/8/7p/3QK3 w - - 0 0')
    with pytest.raises(Exception) as excinfo:
        pos.move('a8')
    assert 'Illegal move' in str(excinfo.value)


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


def test_rook_move_ambiguous_file():
    pos = Position('r1br2k1/2q1bppp/p4n2/2Pp4/8/B4N2/P2Q1PPP/R3R1K1 w - - 1 18')
    pos.move('Rac1')  # this should work
    with pytest.raises(Exception) as excinfo:
        pos.move('Rc1')  # ambiguous origin
    assert 'Illegal move' in str(excinfo.value)


def test_rook_move_invalidate_castling():
    pos = Position('rnbqkbnr/1pppppp1/8/p6p/P6P/8/1PPPPPP1/RNBQKBNR w KQkq a6 0 3')
    pos = pos.move('Rh3')
    assert pos.fen() == 'rnbqkbnr/1pppppp1/8/p6p/P6P/7R/1PPPPPP1/RNBQKBN1 b Qkq - 1 3'
    pos = pos.move('Rh6')
    assert pos.fen() == 'rnbqkbn1/1pppppp1/7r/p6p/P6P/7R/1PPPPPP1/RNBQKBN1 w Qq - 2 4'
    pos = pos.move('Raa3').move('Raa6')  # need to specify file, too
    assert pos.fen() == '1nbqkbn1/1pppppp1/r6r/p6p/P6P/R6R/1PPPPPP1/1NBQKBN1 w - - 4 5'


def test_rook_move_black():
    pos = Position('rnbqkbn1/ppppppp1/7r/7p/7P/5PP1/PPPPP3/RNBQKBNR b KQq - 0 4')
    pos = pos.move('Rc6')
    assert pos.fen() == 'rnbqkbn1/ppppppp1/2r5/7p/7P/5PP1/PPPPP3/RNBQKBNR w KQq - 1 5'


def test_rook_move_no_jump_over_piece():
    pos = Position('8/8/1K1kr3/8/4r2R/8/8/R7 w - - 2 33')
    with pytest.raises(Exception) as excinfo:
        pos.move('Rb4')
    assert 'Illegal move' in str(excinfo.value)


def test_king_move():
    pos = Position('6kr/8/8/8/8/8/8/RK6 b - - 15 41') \
            .move('Kf7')
    assert pos.fen() == '7r/5k2/8/8/8/8/8/RK6 w - - 16 42'


def test_king_move_invalidate_castling():
    pos = Position('rnbqkbnr/pppp1ppp/4p3/8/8/4P3/PPPP1PPP/RNBQKBNR w KQkq - 0 2') \
            .move('Ke2')
    assert pos.fen() == 'rnbqkbnr/pppp1ppp/4p3/8/8/4P3/PPPPKPPP/RNBQ1BNR b kq - 1 2'


def test_knight_move():
    pos = Position().move('Nc3').move('Nc6')
    assert pos.fen() == 'r1bqkbnr/pppppppp/2n5/8/8/2N5/PPPPPPPP/R1BQKBNR w KQkq - 2 2'


def test_knight_move2():
    pos = Position('r1bqkbnr/ppp1pppp/2np4/8/8/2N1P3/PPPP1PPP/R1BQKBNR w KQkq - 0 3') \
        .move('Nge2')
    assert pos.fen() == 'r1bqkbnr/ppp1pppp/2np4/8/8/2N1P3/PPPPNPPP/R1BQKB1R b KQkq - 1 3'


def test_knight_move3():
    with pytest.raises(Exception) as excinfo:
        Position('r1bqkbnr/ppp1pppp/2np4/8/8/2N1P3/PPPP1PPP/R1BQKBNR w KQkq - 0 3') \
            .move('Ne2')
    assert 'ambiguous origin' in str(excinfo.value)


@xfail
def test_knight_capture():
    pos = Position('r2qkbnr/pppbpppp/2n5/3p4/5N2/2N1P3/PPPP1PPP/R1BQKB1R w KQkq - 2 5') \
        .move('Ncxd5')
    assert pos.fen() == 'r2qkbnr/pppbpppp/2n5/3N4/5N2/4P3/PPPP1PPP/R1BQKB1R b KQkq - 0 5'


def test_bishop_move():
    pos = Position('r2qkbnr/pppbpppp/2n5/3N4/5N2/4P3/PPPP1PPP/R1BQKB1R b KQkq - 0 5')\
        .move('Bf5').move('Ba6')
    assert pos.fen() == 'r2qkbnr/ppp1pppp/B1n5/3N1b2/5N2/4P3/PPPP1PPP/R1BQK2R b KQkq - 2 6'


def test_queen_move():
    pos = Position('r2qkbnr/p1p1pppp/p3b3/3N4/3P1N2/2PQP3/PP3PPP/R1B1K2R w KQkq - 1 10')
    assert pos.move('Qc4').fen() == 'r2qkbnr/p1p1pppp/p3b3/3N4/2QP1N2/2P1P3/PP3PPP/R1B1K2R b KQkq - 2 10'
    assert pos.move('Qd1').fen() == 'r2qkbnr/p1p1pppp/p3b3/3N4/3P1N2/2P1P3/PP3PPP/R1BQK2R b KQkq - 2 10'


@xfail
def test_castling():
    pos = Position('r2qkbnr/pbpp1ppp/1pn5/4p3/4P3/5NP1/PPPP1PBP/RNBQK2R w KQkq - 2 5')
    pos = pos.move('O-O')
    assert pos.fen() == 'r2qkbnr/pbpp1ppp/1pn5/4p3/4P3/5NP1/PPPP1PBP/RNBQ1RK1 b kq - 3 5'
    pos = Position('r3kbnr/pbppqppp/1pn5/4p3/4P3/5NPP/PPPP1PB1/RNBQ1RK1 b kq - 0 6')
    pos = pos.move('O-O-O')
    assert pos.fen('2kr1bnr/pbppqppp/1pn5/4p3/4P3/5NPP/PPPP1PB1/RNBQ1RK1 w - - 1 7')


@xfail
def test_castling_not_available():
    pos = Position('r2qk1nr/p1pbbppp/1pnp4/4p3/4P2P/5NPR/PPPP1PB1/RNBQK3 w Qkq - 0 7')
    pos = pos.move('Rh1').move('Be6')
    with pytest.raises(Exception) as excinfo:
        pos.move('O-O')
    assert 'Illegal move' in str(excinfo.value)


def test_pieces_that_can_move_here():
    pos = Position('r1bqkb1r/ppp2ppp/2np1n2/4p3/4P3/1P3N2/PBPP1PPP/RN1QKB1R w KQkq - 0 5')
    assert pos.pieces_that_can_move_here(piece=Piece.KNIGHT, target='e5', color=Color.WHITE) == {'f3'}
    assert pos.pieces_that_can_move_here(piece=Piece.KNIGHT, target='e5', color=Color.BLACK) == set()
    pos = Position('3R2R1/8/4k3/8/2r5/8/2r5/5K2 b - - 3 28')
    assert pos.pieces_that_can_move_here(piece=Piece.ROOK, target='e8', color=Color.WHITE) == {'d8', 'g8'}
    assert pos.pieces_that_can_move_here(piece=Piece.ROOK, target='c5', color=Color.BLACK) == {'c4'}


def test_candidate_targets_empty_square():
    pos = Position()
    assert pos.candidate_targets_from('e5') is None


def test_candidate_targets_initial_pawns():
    pos = Position()
    assert pos.candidate_targets_from('a2') == {'a3', 'a4'}
    assert pos.candidate_targets_from('a7') == {'a6', 'a5'}


def test_candidate_targets_capturing_pawns():
    pos = Position('rn2kbn1/1ppb2p1/p7/1B1pppqp/2rPPPQP/1P6/P1P3PR/RNB1K1N1 w Qq - 6 11')
    assert pos.candidate_targets_from('b3') == {'b4', 'c4'}
    assert pos.candidate_targets_from('h5') == {'g4'}
    assert pos.candidate_targets_from('e4') == {'d5', 'f5'}


def test_candidate_targets_en_passant():
    pos = Position('rnbqkbnr/1pp1pppp/8/p2pP3/8/P7/1PPP1PPP/RNBQKBNR w KQkq d6 0 4')
    assert pos.candidate_targets_from('e5') == {'e6', 'd6'}


def test_candidate_targets_initial_knights():
    pos = Position()
    assert pos.candidate_targets_from('b1') == {'a3', 'c3'}
    assert pos.candidate_targets_from('b8') == {'a6', 'c6'}


def test_candidate_targets_knight_capture():
    pos = Position('r1bqkb1r/ppp2ppp/2np1n2/4p3/4P3/2NP1N2/PPP2PPP/R1BQKB1R w KQkq - 0 5')
    assert pos.candidate_targets_from('f6') == {'g8', 'h5', 'g4', 'e4', 'd5', 'd7'}
    assert pos.candidate_targets_from('f3') == {'g1', 'h4', 'g5', 'e5', 'd4', 'd2'}


def test_candidate_targets_initial_blocked_pieces():
    pos = Position()
    assert pos.candidate_targets_from('a1') == set()
    assert pos.candidate_targets_from('c1') == set()
    assert pos.candidate_targets_from('d1') == set()
    assert pos.candidate_targets_from('e1') == set()
    assert pos.candidate_targets_from('h8') == set()
    assert pos.candidate_targets_from('f8') == set()
    assert pos.candidate_targets_from('e8') == set()
    assert pos.candidate_targets_from('d8') == set()


def test_candidate_targets_bishop():
    pos = Position('rnbqkbnr/pppppp1p/8/6p1/8/3PB3/PPP1PPPP/RN1QKBNR b KQkq - 1 2')
    assert pos.candidate_targets_from('f8') == {'g7', 'h6'}
    assert pos.candidate_targets_from('e3') == {'c1', 'd2', 'f4', 'g5', 'd4', 'c5', 'b6', 'a7'}


def test_candidate_targets_rook():
    pos = Position('rnbqkbn1/1ppppp2/pB4r1/6Pp/8/3P3R/PPP1PPP1/RN1QKBN1 b Qq - 0 6')
    assert pos.candidate_targets_from('h3') == {'h1', 'h2', 'h4', 'h5', 'e3', 'f3', 'g3'}
    assert pos.candidate_targets_from('g6') == {'g7', 'g5', 'b6', 'c6', 'd6', 'e6', 'f6', 'h6'}


def test_candidate_targets_queen():
    pos = Position('rnbq1bn1/1ppp1p2/pB2k1r1/4p1Pp/2P5/2QP3R/PP2PPP1/RN2KBN1 b Q - 4 9')
    assert pos.candidate_targets_from('c3') == {'c1', 'c2', 'a3', 'b3', 'a5', 'b4', 'd4', 'e5', 'd2'}


def test_candidate_targets_king():
    pos = Position('rnbq1bn1/1ppp1p2/pB2k1r1/4p1Pp/2P5/2QP3R/PP2PPP1/RN2KBN1 b Q - 4 9')
    assert pos.candidate_targets_from('e1') == {'d1', 'd2'}


# # this shall be covered by some other function
#
# @xfail
# def test_candidate_targets_king_no_move_to_check():
#     pos = Position('rn1qkbnr/ppp1pppp/3p4/8/4P1b1/3P4/PPP2PPP/RNBQKBNR w KQkq - 1 3')
#     assert pos.candidate_targets_from('e1') == {'e2'}

# TODO: tests to write
# - checking and mating moves
# - no moves that cause check for ourselves
# - when checked, no moves that do not escape check
# - advanced ambiguous cases (need to specify rank and file)
