
class Game:
    def __init__(self, fen=None):
        self.board_array = self.starting_board_array()
        self.active_color = 'w'
        self.castling_availability = 'KQkq'
        self.en_passant_target = '-'
        self.halfmove_clock = '0'
        self.fullmove_number = '1'
        if fen is not None:
            self.board_array = self.board_array_from_fen(fen)
            (self.active_color, self.castling_availability, self.en_passant_target,
             self.halfmove_clock, self.fullmove_number) = fen.split(' ')[1:]

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.fen()))

    @staticmethod
    def starting_board_array():
        pos = (
            tuple(c for c in 'rnbqkbnr'),
            ('p',) * 8,
            ('.',) * 8,
            ('.',) * 8,
            ('.',) * 8,
            ('.',) * 8,
            ('P',) * 8,
            tuple(c for c in 'RNBQKBNR')
        )
        return pos

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
