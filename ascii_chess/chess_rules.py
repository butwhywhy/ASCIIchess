
ROWS = ('1', '2', '3', '4', '5', '6', '7', '8')
COLS = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
PIECES = {'K': 'king', 'Q': 'queen', 'R': 'rook', 'B': 'bishop',
        'N': 'knight', '': 'pawn'}
PIECES_NOTATION = {'king': 'K', 'queen': 'Q', 'rook': 'R', 'bishop': 'B',
        'knight': 'N', 'pawn': ''}

def parse_square(square_notation):
    c = square_notation[0]
    r = square_notation[1]
    return (ROWS.index(r), COLS.index(c))

def format_square(y, x):
    return COLS[x] + ROWS[y]

INITIAL = {}
INITIAL[parse_square('a1')] = ('rook', False)
INITIAL[parse_square('b1')] = ('knight', False)
INITIAL[parse_square('c1')] = ('bishop', False)
INITIAL[parse_square('d1')] = ('queen', False)
INITIAL[parse_square('e1')] = ('king', False)
INITIAL[parse_square('f1')] = ('bishop', False)
INITIAL[parse_square('g1')] = ('knight', False)
INITIAL[parse_square('h1')] = ('rook', False)

INITIAL[parse_square('a8')] = ('rook', True)
INITIAL[parse_square('b8')] = ('knight', True)
INITIAL[parse_square('c8')] = ('bishop', True)
INITIAL[parse_square('d8')] = ('queen', True)
INITIAL[parse_square('e8')] = ('king', True)
INITIAL[parse_square('f8')] = ('bishop', True)
INITIAL[parse_square('g8')] = ('knight', True)
INITIAL[parse_square('h8')] = ('rook', True)

for c in COLS:
    INITIAL[parse_square(c+'2')] = ('pawn', False)
    INITIAL[parse_square(c+'7')] = ('pawn', True)

GEN_ROOK = ((0, 1), (0, -1), (1, 0), (-1, 0))
GEN_BISHOP = ((1, 1), (1, -1), (-1, 1), (-1, -1))
GEN_KNIGHT = ((1, 2), (2, 1), (1, -2), (2, -1), 
        (-1, 2), (-2, 1), (-1, -2), (-2, -1))

def moves_generator(piece, is_black, is_capture, y):
    if piece == 'rook':
        return {'gen': GEN_ROOK, 'limit': 8}
    if piece == 'bishop':
        return {'gen': GEN_BISHOP, 'limit': 8}
    if piece == 'knight':
        return {'gen': GEN_KNIGHT, 'limit': 1}
    if piece == 'queen':
        return {'gen': GEN_BISHOP + GEN_ROOK, 'limit': 8}
    if piece == 'king':
        return {'gen': GEN_BISHOP + GEN_ROOK, 'limit': 1}
    if piece == 'pawn':
        if not is_black:
            if not is_capture:
                return {'gen': ((1, 0),), 
                        'limit':  2 if y == 1 else 1}
            else:
                return {'gen': ((1, 1), (1, -1)), 'limit': 1}
        else:
            if not is_capture:
                return {'gen': ((-1, 0),), 
                        'limit':  2 if y == 6 else 1}
            else:
                return {'gen': ((-1, 1), (-1, -1)), 'limit': 1}
    raise Exception('Unknown piece ' + repr(piece))


class Position(object):

    def __init__(self, position=None, white_moves=True, 
            white_can_castle_long=None, white_can_castle_short=None, 
            black_can_castle_long=None, black_can_castle_short=None, 
            col_pawn_moved_2=None):
        if position is None:
            position = INITIAL

        self.position = position

        self.has_ms = None
        self.mate = None
        self.stalemate = None


        self.white_moves = white_moves
        wk = self.get_position('king', False)
        bk = self.get_position('king', True)
        wr = self.get_position('rook', False)
        br = self.get_position('rook', True)

        if white_can_castle_long is None:
            try:
                self.white_can_castle_long = (self.position[(0,4)] == ('king', False)
                        and self.position[(0,0)] == ('rook', False))
            except KeyError:
                self.white_can_castle_long = False
        else:
            self.white_can_castle_long = white_can_castle_long

        if white_can_castle_short is None:
            try:
                self.white_can_castle_short = (self.position[(0,4)] == ('king', False)
                        and self.position[(0,7)] == ('rook', False))
            except KeyError:
                self.white_can_castle_short = False
        else:
            self.white_can_castle_short = white_can_castle_short

        if black_can_castle_long is None:
            try:
                self.black_can_castle_long = (self.position[(7,4)] == ('king', True)
                        and self.position[(7,0)] == ('rook', True))
            except KeyError:
                self.black_can_castle_long = False
        else:
            self.black_can_castle_long = black_can_castle_long

        if black_can_castle_short is None:
            try:
                self.black_can_castle_short = (self.position[(7,4)] == ('king', True)
                        and self.position[(7,7)] == ('rook', True))
            except KeyError:
                self.black_can_castle_short = False
        else:
            self.black_can_castle_short = black_can_castle_short

        if col_pawn_moved_2 in COLS:
            col_pawn_moved_2 = COLS.index(col_pawn_moved_2) # column 'a', 'b', ....
        self.col_pawn_moved_2 = col_pawn_moved_2

    def get_square_content(self, sq):
        try:
            return self.position[sq]
        except KeyError:
            return None

    def get_square_content_2(self, sq):
        try:
            return self.position[sq]
        except KeyError:
            return None

    def get_position(self, piece_type=None, is_black=None):
        if piece_type is None and is_black is None:
            return dict(self.position)
        result = {}
        for sq, value in self.position.iteritems():
            piece, color = value
            if (is_black is None or is_black == color) and (
                    piece_type is None or piece_type == piece):
                result[sq] = value
        return result

    def moves(self, piece, is_black, y, x):
        if piece == 'king':
            if (is_black and self.black_can_castle_short) or (
                    not is_black and self.white_can_castle_short):
                yy = 7 if is_black else 0
                if all(self.get_square_content((yy, xx)) is None for xx in (5, 6)): 
                    if not any(self.can_capture(not is_black, (yy, xx))
                            for xx in (4, 5, 6)):
                        yield self.Move(piece, self, (y, 4), 
                                (y, 6))
            if (is_black and self.black_can_castle_long) or (
                    not is_black and self.white_can_castle_long):
                yy = 7 if is_black else 0
                if all(self.get_square_content((yy, xx)) is None for xx in (1, 2, 3)): 
                    if not any(self.can_capture(not is_black, (yy, xx))
                            for xx in (2, 3, 4)):
                        yield self.Move(piece, self, (y, 4), 
                                (y, 2))
            
        moves_gen = moves_generator(piece, is_black, False, y)
        for g in moves_gen['gen']:
            m = 0
            (y_t, x_t) = (y, x)
            while m < moves_gen['limit']:
                m += 1
                (y_t, x_t) = (y_t + g[0], x_t + g[1])
                if 0 <= y_t < 8 and 0 <= x_t < 8:
                    t_content = self.get_square_content((y_t, x_t))
                else:
                    break
                if not t_content:
                    if piece == 'pawn' and y_t in (0, 7):
                        for prom in ('bishop', 'knight', 'rook', 'queen'):
                            try:
                                yield self.Move(piece, self, (y,x), 
                                        (y_t, x_t), promoted=prom)
                            except IllegalMoveException:
                                break
                    else:
                        try:
                            yield self.Move(piece, self, (y,x), 
                                    (y_t, x_t))
                        except IllegalMoveException:
                            pass
                else:
                    (t_piece, t_is_black) = t_content
                    if t_is_black != is_black and piece != 'pawn':
                        try:
                            yield self.Move(piece, self, (y,x), 
                                    (y_t, x_t), is_capture=True)
                        except IllegalMoveException:
                            pass
                    break
        if piece == 'pawn':
            pawn_captures_gen = moves_generator(piece, is_black, True, y)
            for g in pawn_captures_gen['gen']:
                (y_t, x_t) = (y + g[0], x + g[1])
                if 0 <= y_t < 8 and 0 <= x_t < 8:
                    t_content = self.get_square_content((y_t, x_t))
                else:
                    continue
                if not t_content:
                    if self.col_pawn_moved_2 == x_t:
                        if (is_black and y_t == 2) or (
                                not is_black and y_t == 5):
                            try:
                                yield self.Move(piece, self, (y,x), 
                                        (y_t, x_t), 
                                        is_capture=True, ap=True)
                            except IllegalMoveException:
                                pass
                else:
                    (t_piece, t_is_black) = t_content
                    if t_is_black != is_black:
                        if y_t in (0, 7):
                            for prom in ('bishop', 'knight', 'rook', 'queen'):
                                try:
                                    yield self.Move(piece, self, 
                                            (y,x), 
                                            (y_t, x_t), 
                                            is_capture=True, promoted=prom)
                                except IllegalMoveException:
                                    break
                        else:
                            try:
                                yield self.Move(piece, self, (y,x), 
                                        (y_t, x_t), is_capture=True)
                            except IllegalMoveException:
                                pass



    class Move(object):

        def __init__(self, main_piece, position, sq_from, 
                sq_to, is_capture=False, promoted=None, ap=False):
            self.main_piece = main_piece
            self.position = position
            self.is_black = not (position.white_moves)
            self.sq_from = sq_from
            self.sq_to = sq_to
            self.is_capture = is_capture
            self.promoted = promoted
            self.ap = ap

            self.proccess()

        def proccess(self):
            self.changes = {self.sq_from: None, 
                    self.sq_to: ((self.promoted if self.promoted else self.main_piece, self.is_black))}
            (t_y, t_x) = self.sq_to
            if self.main_piece == 'pawn' and self.ap:
                if t_y == 2:
                    t_y = 3
                elif t_y == 5:
                    t_y = 4
                self.changes[(t_y, t_x)] = None
            elif self.main_piece == 'king':
                (y, x) = self.sq_from
                if x == 4:
                    if t_x == 6:
                        self.changes[(y, 7)] = None
                        self.changes[(y, 5)] = ('rook', self.is_black)
                    elif t_x == 2:
                        self.changes[(y, 0)] = None
                        self.changes[(y, 3)] = ('rook', self.is_black)

            to_pos = self.position.get_position()
            for sq, val in self.changes.iteritems():
                if not val:
                    del to_pos[sq]
                else:
                    to_pos[sq] = val

            white_can_castle_short = self.position.white_can_castle_short
            white_can_castle_long = self.position.white_can_castle_long
            black_can_castle_short = self.position.black_can_castle_short
            black_can_castle_long = self.position.black_can_castle_long
            col_pawn_moved_2 = None
            if self.main_piece == 'king' or self.main_piece == 'rook':
                (y, x) = self.sq_from
                if x == 0:
                    if y == 0:
                        white_can_castle_long = False
                    elif y == 7:
                        black_can_castle_long = False
                elif x == 7:
                    if y == 0:
                        white_can_castle_short = False
                    elif y == 7:
                        black_can_castle_short = False
                elif x == 4:
                    if y == 0:
                        white_can_castle_long = False
                        white_can_castle_short = False
                    elif y == 7:
                        black_can_castle_long = False
                        black_can_castle_short = False
            elif self.main_piece == 'pawn':
                (y, x) = self.sq_from
                if abs(t_y - y) == 2:
                    col_pawn_moved_2 = COLS[x]

            self.captured = None
            if self.is_capture:
                if self.ap:
                    self.captured = 'pawn'
                else:
                    (self.captured, _) = self.position.get_square_content((t_y, t_x))

            self.to_position = Position(
                    position=to_pos, 
                    white_moves=self.is_black,
                    white_can_castle_long=white_can_castle_long, 
                    white_can_castle_short=white_can_castle_short,
                    black_can_castle_long=black_can_castle_long,
                    black_can_castle_short=black_can_castle_short,
                    col_pawn_moved_2=col_pawn_moved_2)
            if self.to_position.checks(not self.is_black):
                raise IllegalMoveException('In check')

        def notation(self):
            #TODO
            return self.notations()[-1]

        def notations(self):
            notation = ('x' if self.is_capture else '') + format_square(*self.sq_to)
            (t_y, t_x) = self.sq_to
            (y, x) = self.sq_from
            notations = []
            if self.main_piece == 'pawn':
                if t_x != x:
                    notation = COLS[x] + notation
                if self.promoted:
                    notation = notation + '=' + PIECES_NOTATION[self.promoted]
                notations.append(notation)
            else:
                if self.main_piece == 'king' and abs(x - t_x) == 2:
                    if t_x == 6:
                        notations.append('0-0')
                        notations.append('O-O')
                    elif t_x == 2:
                        notations.append('0-0-0')
                        notations.append('O-O-O')
                else:
                    p_not = PIECES_NOTATION[self.main_piece]
                    notations.append(p_not + notation)
                    notations.append(p_not + COLS[x] + notation)
                    notations.append(p_not + ROWS[y] + notation)
                    notations.append(p_not + COLS[x] + ROWS[y] + notation)
            if self.to_position.is_check():
                symbol = '++' if self.to_position.is_mate() else '+'
                for n in list(notations):
                    notations.append(n + symbol)

            return notations


        def __repr__(self):
            return self.notation()

        def changes(self):
            return self.changes

        def to_position(self):
            return self.to_position

        def is_mate(self):
            return self.to_position.is_mate()

        def is_stalemate(self):
            return self.to_position.is_stalemate()

    def can_capture(self, is_black, square):
        for sq, (piece, _) in self.get_position(is_black=is_black).iteritems():
            (y, x) = sq
            moves_gen = moves_generator(piece, is_black, True, y)
            for g in moves_gen['gen']:
                m = 0
                (y_t, x_t) = (y, x)
                while m < moves_gen['limit']:
                    m += 1
                    (y_t, x_t) = (y_t + g[0], x_t + g[1])
                    if 0 <= y_t < 8 and 0 <= x_t < 8:
                        t_content = self.get_square_content((y_t, x_t))
                    else:
                        break
                    if (y_t, x_t) == square:
                        return True
                    if t_content:
                        break
        return False
    
    def has_moves(self):
        if self.has_ms is None:
            aux = False
            for m in self.all_moves():
                aux = True
                break
            self.has_ms = aux
        return self.has_ms

    def is_check(self):
        return self.checks(self.white_moves)

    def is_mate(self):
        if self.mate is None:
            self.mate = not self.has_moves() and self.is_check()
        return self.mate

    def is_stalemate(self):
        if self.stalemate is None:
            self.stalemate = not self.has_moves() and not self.is_check() 
        return self.stalemate

    def checks(self, is_black):
        king_pos = self.get_position('king', not is_black).keys()[0]
        return self.can_capture(is_black, king_pos)

    def result(self):
        if self.has_moves():
            return None
        if self.is_stalemate():
            return DRAW
        if self.is_mate():
            if self.white_moves:
                return BLACK_WINS
            return WHITE_WINS

    def all_moves(self):
        for sq, (piece, is_black) in self.get_position(is_black=not self.white_moves).iteritems():
            p_moves = self.moves(piece, is_black, *sq)
            for move in p_moves:
                yield move

    def move(self, move_notation):
        for mv in self.all_moves():
            if move_notation in mv.notations():
                return mv.to_position
        raise IllegalMoveException('Illegal move %s' % move_notation)

WHITE_WINS = '1-0'
BLACK_WINS = '0-1'
DRAW = '0.5-0.5'

class IllegalMoveException(Exception):
    pass

