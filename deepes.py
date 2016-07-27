
class Game:
    def __init__(self, fen=None):
        if fen is not None:
            self.position = self.position_from_fen(fen)
        else:
            self.position = self.starting_position()

    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)

    @staticmethod
    def starting_position():
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
    def position_from_fen(fen):
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
        return '\n'.join(''.join(piece for piece in rank) for rank in self.position)
