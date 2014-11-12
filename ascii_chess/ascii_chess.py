from ascii_drawing import Canvas, Square, figure_from_string, GeneralColorConversor, ScaleConversor
class ChessBoard(object):
    def __init__(self, side, white_darkness, black_darkness):
        self.extra = 4
        self.side = side
        self.white_darkness = white_darkness
        self.black_darkness = black_darkness
        self.white_square = Square(self.side, self.side, self.white_darkness, 1)
        self.black_square = Square(self.side, self.side, self.black_darkness, 1)
        ll = self.side * 8 + 2 * self.extra
        self.canvas = Canvas(ll, ll)
        self.clean_board()

    def add_piece(self, figure, row, column):
        self.clean_square(row, column)
        self.canvas.add_figure(figure, *self.get_square(row, column))

    def set_position(self, white_set, black_set, position=None):
        from .chess_rules import parse_square
        if position is None:
            from .chess_rules import INITIAL
            position = INITIAL
        self.clean_board()
        for square, (piece, is_black) in position.iteritems():
            p = black_set[piece] if is_black else white_set[piece]
            self.add_piece(p, *square)


    def clean_square(self, row, column):
        if (column + row) % 2 != 0:
            self.canvas.add_figure(self.white_square, *self.get_square(row, column))
        else:
            self.canvas.add_figure(self.black_square, *self.get_square(row, column))

    def clean_board(self):
        for i in xrange(8):
            for j in xrange(8):
                self.clean_square(i, j)


    def get_square(self, row, col):
        x = col
        y = 8 - row - 1
        return (self.extra + y * self.side, self.extra + x * self.side)

    def __repr__(self):
        return self.canvas.paint()


class ChessPiecesSet(object):
    
    def __init__(self, side, max_darkness):
        def pix_transform(darkness, opacity):
            if darkness == 0:
                return (darkness, 0)
            return (darkness * max_darkness, 1)
        color_conv = GeneralColorConversor(pix_transform)
        scale_conv = ScaleConversor(side, side)
        self.pieces = {}
        for pname in ascii_pieces:
            self.pieces[pname] = scale_conv.convert(
                    color_conv.convert(ascii_pieces[pname]))
    
    def __getitem__(self, piece_name):
        return self.pieces[piece_name]

from os import path
from pkg_resources import resource_string
#_pieces_path = os.path.abspath(
                #os.path.join(os.path.dirname(__file__), 'ascii_chess_pieces'))
#ascii_pieces = {p : figure_from_file(os.path.join(_pieces_path, p))
ascii_pieces = {p : figure_from_string(resource_string('ascii_chess', path.join('ascii_chess_pieces', p)))
        for p in ('pawn', 'bishop', 'knight', 'rook', 'queen', 'king')}

if __name__ == '__main__':
    side = 10
    board = ChessBoard(side, 0, 0.7)
    print board
    
    for p in ascii_pieces:
        pp = ascii_pieces[p]
        print pp
        print p, pp.get_height(), pp.get_width()
    black_pieces = ChessPiecesSet(side, 1)
    for p in black_pieces.pieces.values():
        print p
        print p.get_height(), p.get_width()
    white_pieces = ChessPiecesSet(side, 0.2)
    for p in white_pieces.pieces.values():
        print p
        print p.get_height(), p.get_width()

    from .chess_rules import parse_square
    board.add_piece(white_pieces['pawn'], *parse_square('d4'))
    board.add_piece(white_pieces['pawn'], *parse_square('e4'))
    board.add_piece(black_pieces['pawn'], *parse_square('d5'))
    board.add_piece(black_pieces['pawn'], *parse_square('e5'))
    print board

    board.set_position(white_pieces, black_pieces)
    print board



