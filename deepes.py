
class Position:
    def __init__(self, fen=None):
        if fen is None:
            fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        self.board_array = self.board_array_from_fen(fen)
        (self.active_color, self.castling_availability, self.en_passant_target,
         self.halfmove_clock, self.fullmove_number) = fen.split(' ')[1:]

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.fen()))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.fen() == self.fen()

    @staticmethod
    def board_array_from_fen(fen):
        """
        According to '1. Piece placement' in
        https://en.wikipedia.org/w/index.php?title=Forsyth%E2%80%93Edwards_Notation&oldid=707127024#Definition
        """
        fen_pieces = fen.split(' ')[0]
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

    def basic_board(self):
        return '\n'.join(''.join(piece for piece in rank) for rank in self.board_array)

    def fen(self):
        fen_pieces = ''
        for rank in self.board_array:
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

        return '{} {} {} {} {} {}'.format(fen_pieces, self.active_color, self.castling_availability,
                                          self.en_passant_target, self.halfmove_clock, self.fullmove_number)
