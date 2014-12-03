KING = 0
QUEEN = 1
ROOK = 2
BISHOP = 3
KNIGHT = 4
PAWN = 5

ROWS = ('1', '2', '3', '4', '5', '6', '7', '8')
COLS = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
PIECES_NOTATION = {KING: 'K', QUEEN: 'Q', ROOK: 'R', BISHOP: 'B',
        KNIGHT: 'N', PAWN: ''}

def parse_square(square_notation):
    c = square_notation[0]
    r = square_notation[1]
    return (ROWS.index(r), COLS.index(c))

def format_square(y, x):
    return COLS[x] + ROWS[y]

def position_from_dict(pos):
    position = [[None] * 8 for a in xrange(8)] 
    for sq, val in pos.iteritems():
        y, x = sq
        position[y][x] = val
    return position

INITIAL = dict()
INITIAL[parse_square('a1')] = (ROOK, False)
INITIAL[parse_square('b1')] = (KNIGHT, False)
INITIAL[parse_square('c1')] = (BISHOP, False)
INITIAL[parse_square('d1')] = (QUEEN, False)
INITIAL[parse_square('e1')] = (KING, False)
INITIAL[parse_square('f1')] = (BISHOP, False)
INITIAL[parse_square('g1')] = (KNIGHT, False)
INITIAL[parse_square('h1')] = (ROOK, False)

INITIAL[parse_square('a8')] = (ROOK, True)
INITIAL[parse_square('b8')] = (KNIGHT, True)
INITIAL[parse_square('c8')] = (BISHOP, True)
INITIAL[parse_square('d8')] = (QUEEN, True)
INITIAL[parse_square('e8')] = (KING, True)
INITIAL[parse_square('f8')] = (BISHOP, True)
INITIAL[parse_square('g8')] = (KNIGHT, True)
INITIAL[parse_square('h8')] = (ROOK, True)

for c in COLS:
    INITIAL[parse_square(c+'2')] = (PAWN, False)
    INITIAL[parse_square(c+'7')] = (PAWN, True)

GEN_ROOK = ((0, 1), (0, -1), (1, 0), (-1, 0))
GEN_BISHOP = ((1, 1), (1, -1), (-1, 1), (-1, -1))
GEN_KNIGHT = ((1, 2), (2, 1), (1, -2), (2, -1), 
        (-1, 2), (-2, 1), (-1, -2), (-2, -1))

def moves_generator(piece, is_black, is_capture, y):
    if piece == ROOK:
        return {'gen': GEN_ROOK, 'limit': 8}
    if piece == BISHOP:
        return {'gen': GEN_BISHOP, 'limit': 8}
    if piece == KNIGHT:
        return {'gen': GEN_KNIGHT, 'limit': 1}
    if piece == QUEEN:
        return {'gen': GEN_BISHOP + GEN_ROOK, 'limit': 8}
    if piece == KING:
        return {'gen': GEN_BISHOP + GEN_ROOK, 'limit': 1}
    if piece == PAWN:
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

    def __init__(self, position=None, white_pieces=None,
            black_pieces=None, white_moves=True, 
            white_can_castle_long=None, white_can_castle_short=None, 
            black_can_castle_long=None, black_can_castle_short=None, 
            col_pawn_moved_2=None):
        if position is None:
            position = position_from_dict(INITIAL)

        if white_pieces is None or black_pieces is None:
            white_pieces = [None] * 6
            black_pieces = [None] * 6
            for y in xrange(8):
                for x in xrange(8):
                    val = position[y][x]
                    if val:
                        sq = (y, x)
                        (piece, is_black) = val
                        if is_black:
                            try:
                                black_pieces[piece].append(sq)
                            except AttributeError:
                                black_pieces[piece] = [sq]
                        else:
                            try:
                                white_pieces[piece].append(sq)
                            except AttributeError:
                                white_pieces[piece] = [sq]

        self.position = position
        self.white_pieces = white_pieces
        self.black_pieces = black_pieces

        self.has_ms = None
        self.mate = None
        self.stalemate = None


        self.white_moves = white_moves

        if white_can_castle_long is None:
            self.white_can_castle_long = (self.position[0][4] == (KING, False)
                    and self.position[0][0] == (ROOK, False))
        else:
            self.white_can_castle_long = white_can_castle_long

        if white_can_castle_short is None:
            self.white_can_castle_short = (self.position[0][4] == (KING, False)
                    and self.position[0][7] == (ROOK, False))
        else:
            self.white_can_castle_short = white_can_castle_short

        if black_can_castle_long is None:
            self.black_can_castle_long = (self.position[7][4] == (KING, True)
                    and self.position[7][0] == (ROOK, True))
        else:
            self.black_can_castle_long = black_can_castle_long

        if black_can_castle_short is None:
            self.black_can_castle_short = (self.position[7][4] == (KING, True)
                    and self.position[7][7] == (ROOK, True))
        else:
            self.black_can_castle_short = black_can_castle_short

        if col_pawn_moved_2 in COLS:
            col_pawn_moved_2 = COLS.index(col_pawn_moved_2) # column 'a', 'b', ....
        self.col_pawn_moved_2 = col_pawn_moved_2

    def get_square_content(self, sq):
        return self.position[sq[0]][sq[1]]

    def get_position(self, piece_type=None, is_black=None):
        result = dict()
        for y in xrange(8):
            for x in xrange(8):
                val = self.position[y][x]
                if not val:
                    continue
                sq = (y, x)
                piece, color = val
                if (is_black is None or is_black == color) and (
                        piece_type is None or piece_type == piece):
                    result[sq] = val
        return result

    def moves(self, piece, is_black, y, x):
        get_sq = self.get_square_content
        if piece == KING:
            if (is_black and self.black_can_castle_short) or (
                    not is_black and self.white_can_castle_short):
                yy = 7 if is_black else 0
                if all(get_sq((yy, xx)) is None for xx in (5, 6)): 
                    if not any(self.can_capture(not is_black, (yy, xx))
                            for xx in (4, 5, 6)):
                        yield self.Move(piece, self, (y, 4), 
                                (y, 6))
            if (is_black and self.black_can_castle_long) or (
                    not is_black and self.white_can_castle_long):
                yy = 7 if is_black else 0
                if all(get_sq((yy, xx)) is None for xx in (1, 2, 3)): 
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
                if not (0 <= y_t < 8 and 0 <= x_t < 8):
                    break
                t_content = self.position[y_t][x_t]
                if not t_content:
                    if piece == PAWN and y_t in (0, 7):
                        for prom in (BISHOP, KNIGHT, ROOK, QUEEN):
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
                    continue
                (t_piece, t_is_black) = t_content
                if t_is_black != is_black and piece != PAWN:
                    try:
                        yield self.Move(piece, self, (y,x), 
                                (y_t, x_t), is_capture=True)
                    except IllegalMoveException:
                        pass
                break
        if piece == PAWN:
            pawn_captures_gen = moves_generator(piece, is_black, True, y)
            for g in pawn_captures_gen['gen']:
                (y_t, x_t) = (y + g[0], x + g[1])
                if 0 <= y_t < 8 and 0 <= x_t < 8:
                    t_content = get_sq((y_t, x_t))
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
                            for prom in (BISHOP, KNIGHT, ROOK, QUEEN):
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

            self.process()

        def process(self):
            w_p = self.position.white_pieces
            b_p = self.position.black_pieces
            white_pieces = [list(sqs) if sqs else None for sqs in w_p]
            black_pieces = [list(sqs) if sqs else None for sqs in b_p]

            (t_y, t_x) = self.sq_to
            (y, x) = self.sq_from

            to_pos = list(map(list, self.position.position))
            to_pos[y][x] = None
            to_pos[t_y][t_x] = (self.promoted if self.promoted else self.main_piece, 
                    self.is_black)
            if self.is_black:
                moving_pieces = black_pieces
                not_moving_pieces = white_pieces
            else:
                moving_pieces = white_pieces
                not_moving_pieces = black_pieces
            sqs = moving_pieces[self.main_piece]
            sqs.remove(self.sq_from)

            if self.promoted:
                if not sqs:
                    moving_pieces[self.main_piece] = None
                try:
                    moving_pieces[self.promoted].append(self.sq_to)
                except AttributeError:
                    moving_pieces[self.promoted] = [self.sq_to]
            else:
                sqs.append(self.sq_to)

            self.captured = None
            if self.is_capture:
                if self.ap:
                    if t_y == 2:
                        t_y = 3
                    elif t_y == 5:
                        t_y = 4
                    to_pos[t_y][t_x] = None
                    not_moving_pieces[PAWN].remove((t_y, t_x))
                    self.captured = PAWN
                else:
                    self.captured = self.position.get_square_content(self.sq_to)[0]
                    not_moving_pieces[self.captured].remove(self.sq_to)
                if not not_moving_pieces[self.captured]:
                    not_moving_pieces[self.captured] = None
            elif self.main_piece == KING:
                if x == 4:
                    if t_x == 6:
                        to_pos[y][7] = None
                        to_pos[y][5] = (ROOK, self.is_black)
                        moving_pieces[ROOK].remove((y, 7))
                        moving_pieces[ROOK].append((y, 5))
                    elif t_x == 2:
                        to_pos[y][0] = None
                        to_pos[y][3] = (ROOK, self.is_black)
                        moving_pieces[ROOK].remove((y, 0))
                        moving_pieces[ROOK].append((y, 3))

            white_can_castle_short = self.position.white_can_castle_short
            white_can_castle_long = self.position.white_can_castle_long
            black_can_castle_short = self.position.black_can_castle_short
            black_can_castle_long = self.position.black_can_castle_long
            col_pawn_moved_2 = None
            if self.main_piece == KING or self.main_piece == ROOK:
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
            elif self.main_piece == PAWN:
                if abs(t_y - y) == 2:
                    col_pawn_moved_2 = COLS[x]

            if self.is_capture and self.captured == ROOK:
                if t_x == 0:
                    if t_y == 0:
                        white_can_castle_long = False
                    elif t_y == 7:
                        black_can_castle_long = False
                elif t_x == 7:
                    if t_y == 0:
                        white_can_castle_short = False
                    elif t_y == 7:
                        black_can_castle_short = False

            if self.is_capture and self.captured == ROOK:
                (y, x) = self.sq_to
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

            self.to_position = Position(
                    position=to_pos, 
                    white_pieces=white_pieces,
                    black_pieces=black_pieces,
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
            if self.main_piece == PAWN:
                if t_x != x:
                    notation = COLS[x] + notation
                if self.promoted:
                    notation = notation + '=' + PIECES_NOTATION[self.promoted]
                notations.append(notation)
            else:
                if self.main_piece == KING and abs(x - t_x) == 2:
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
            changes = {self.sq_from: None, 
                    self.sq_to: ((self.promoted if self.promoted else self.main_piece, self.is_black))}
            if self.is_capture:
                if self.ap:
                    if t_y == 2:
                        t_y = 3
                    elif t_y == 5:
                        t_y = 4
                    changes[(t_y, t_x)] = None
            elif self.main_piece == KING:
                (y, x) = self.sq_from
                if x == 4:
                    if t_x == 6:
                        changes[(y, 7)] = None
                        changes[(y, 5)] = (ROOK, self.is_black)
                    elif t_x == 2:
                        changes[(y, 0)] = None
                        changes[(y, 3)] = (ROOK, self.is_black)
            return changes

        def to_position(self):
            return self.to_position

        def is_mate(self):
            return self.to_position.is_mate()

        def is_stalemate(self):
            return self.to_position.is_stalemate()

    def can_capture(self, is_black, square):
        get_sq = self.get_square_content
        square_y, square_x = square
        moving_pieces = self.black_pieces if is_black else self.white_pieces
        for piece, sqs in enumerate(moving_pieces):
            if not sqs:
                continue
            for sq in sqs:
                (y, x) = sq
                dy = abs(square_y - y)
                dx = abs(square_x -x)
                if piece == PAWN:
                    if dy != 1 or dx != 1:
                        continue
                elif piece == BISHOP:
                    if dy != dx:
                        continue
                elif piece == KNIGHT:
                    if (dy != 1 or dx != 2) and (dy != 2 or dx != 1):
                        continue
                elif piece == ROOK:
                    if dy and dx:
                        continue
                elif piece == QUEEN:
                    if (dy and dx) and (dy != dx):
                        continue
                elif piece == KING:
                    if dy > 1 or dx > 1:
                        continue
                moves_gen = moves_generator(piece, is_black, True, y)
                for g in moves_gen['gen']:
                    m = 0
                    (y_t, x_t) = (y, x)
                    while m < moves_gen['limit']:
                        m += 1
                        (y_t, x_t) = (y_t + g[0], x_t + g[1])
                        if 0 <= y_t < 8 and 0 <= x_t < 8:
                            t_content = self.position[y_t][x_t]
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
        king_pos = self.white_pieces[KING][0] if is_black else self.black_pieces[KING][0] 
        #print ''
        #print king_pos
        #print self.position
        #print self.white_pieces
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
        is_black = not self.white_moves
        moving_pieces = self.white_pieces if self.white_moves else self.black_pieces
        for piece, sqs in enumerate(moving_pieces):
            if not sqs:
                continue
            for sq in sqs:
                p_moves = self.moves(piece, is_black, *sq)
                for move in p_moves:
                    yield move

    def move(self, move_notation):
        for mv in self.all_moves():
            if move_notation in mv.notations():
                return mv.to_position
        for mv in self.all_moves():
            print mv
        raise IllegalMoveException('Illegal move %s' % move_notation)

WHITE_WINS = '1-0'
BLACK_WINS = '0-1'
DRAW = '0.5-0.5'

class IllegalMoveException(Exception):
    pass

