from .chess_play import Engine
from .chess_rules import WHITE_WINS, BLACK_WINS, DRAW

DEFAULT_VALUES = {'mate': 10000, 'queen': 9.5, 'rook': 5, 'bishop':3.5, 
        'knight': 3, 'pawn': 1, 'draw': 0}

class Evaluator(object):

    def eval0(self, position):
        result = position.result()
        if result is None:
            e = self.complex_eval(position)
        elif result is WHITE_WINS:
            e = DEFAULT_VALUES['mate']
        elif result is BLACK_WINS:
            e = -DEFAULT_VALUES['mate']
        else:
            e = DEFAULT_VALUES['draw']
        return e

    def complex_eval(self, position):
        raise Exception('Must be implemented by subclasses')

    def eval(self, pre_pos, pre_value, move):
        return self.eval0(move.to_position)

def get_material(position, is_black, values=DEFAULT_VALUES):
    material = 0
    for (p, _) in position.get_position(is_black=is_black).values():
        if p != 'king':
            material += DEFAULT_VALUES[p]
    return material

class SimpleEvaluator(Evaluator):

    def complex_eval(self, position):
        return get_material(position, False) - get_material(position, True)

    def eval(self, pre_pos, pre_value, move):
        sign = -1 if move.is_black else 1
        if move.is_mate():
            return sign * DEFAULT_VALUES['mate']
        if move.is_stalemate():
            return DEFAULT_VALUES['draw']
        val = pre_value
        if move.promoted:
            val += sign * (DEFAULT_VALUES[move.promoted] - DEFAULT_VALUES['pawn'])
        if move.is_capture:
            val += sign * DEFAULT_VALUES[move.captured]
        return val


class EvalEngine(Engine):
    
    def __init__(self, evaluator, max_depth=3):
        self.evaluator = evaluator
        self.max_depth = max_depth

    def move(self):
        pos = self.game._current_position()
        analysis_result = self.analyse(pos)
        print analysis_result
        if len(analysis_result) > 1:
            return analysis_result[-1]
        return None

    def _analyse(self, pre_pos, pre_value, depth):
        if depth == self.max_depth:
            return [pre_value]

            #yy#print '1'
            #yy#e = self.evaluator.eval0(pos)
            #yyreturn [self.evaluator.eval0(pos)]
        moves_rank = []
        #print pre_pos.get_position()
        for m in pre_pos.all_moves():
            value = self.evaluator.eval(pre_pos, pre_value, m)
            an = self._analyse(m.to_position, value, depth + 1)
            an.append(m.notation())
            moves_rank.append(an)

            #yy#print m
            #yyan = self.analyse(pos.move(m.notation()), depth + 1)
            #yy#print an
            #yyan.append(m.notation())
            #yymoves_rank.append(an)

        #yy#moves_rank = [self.analyse(pos.move(m.notation()), depth + 1).append(m) for m in pos.all_moves()]
        if not moves_rank:
            return [pre_value]
            #yy#print '2'
            #yyreturn [self.evaluator.eval0(pos)]
        #print '3'
        #print moves_rank
        #print "max %s; min %s " % (max(moves_rank), min(moves_rank))
        return max(moves_rank) if pre_pos.white_moves else min(moves_rank) 
        
    def analyse(self, pos):
        pre_value = self.evaluator.eval0(pos)
        return self._analyse(pos, pre_value, 0)

if __name__ == '__main__':
    #pos0 = {'b8': ('king', True), 'a6': ('king', False), 'a5': ('rook', False)}
    from .chess_rules import parse_square
    #pos0 = {parse_square('b8'): ('king', True), parse_square('a6'): ('king', False), parse_square('a5'): ('rook', False)}
    #pos0 = {parse_square('b8'): ('king', True), parse_square('a6'): ('king', False), parse_square('h8'): ('rook', False)}
    pos0 = {parse_square('b8'): ('king', True), parse_square('a6'): ('king', False), parse_square('h5'): ('rook', False)}
    poslist = {'e8': ('king', True), 'e6': ('pawn', False), 'f7': ('pawn', True), 'e7': ('pawn', True), 'd7': ('pawn', True), 'f8': ('bishop', True), 'g8': ('knight', True), 'c4': ('bishop', False), 'e1': ('king', False)}
    pos0 = {parse_square(sq): value for sq, value in poslist.iteritems()}
    from .chess_play import Game
    from .chess_rules import Position
    pos = Position(position=pos0)
    #pos = Position(position=pos0, white_moves=False)
    print pos.get_position()
    game = Game(pos)
    game.move('exf7')
    #game.move('Rh8')
    evaluator = SimpleEvaluator()
    engine = EvalEngine(evaluator, 3)
    engine.set_game(game)
    print engine.move()

