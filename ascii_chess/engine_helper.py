from .chess_play import Engine
from .chess_rules import WHITE_WINS, BLACK_WINS, DRAW
from .chess_rules import KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN

DEFAULT_VALUES = {'mate': 10000, QUEEN: 9.5, ROOK: 5, BISHOP:3.5, 
        KNIGHT: 3, PAWN: 1, 'draw': 0}

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
        if p != KING:
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
            val += sign * (DEFAULT_VALUES[move.promoted] - DEFAULT_VALUES[PAWN])
        if move.is_capture:
            val += sign * DEFAULT_VALUES[move.captured]
        return val


class EvalEngine(Engine):
    
    def __init__(self, evaluator, max_depth=4):
        self.evaluator = evaluator
        self.max_depth = max_depth

    def move(self):
        pos = self.game._current_position()
        only = None
        for m in pos.all_moves():
            if only:
                only = None
                break
            only = m
        if only:
            return only.notation()
        analysis_result = self.analyse(pos)
        print analysis_result
        if len(analysis_result) > 1:
            return analysis_result[-1]
        return None

    def _analyse(self, pre_pos, pre_value, depth):
        if depth == self.max_depth:
            return [pre_value]

        moves_rank = []
        ms = []
        for m in pre_pos.all_moves():
            if m.is_mate():
                return [-DEFAULT_VALUES['mate'] if m.is_black 
                        else DEFAULT_VALUES['mate'], m.notation()]
            ms.append(m)
        for m in ms:
            value = self.evaluator.eval(pre_pos, pre_value, m)
            an = self._analyse(m.to_position, value, depth + 1)
            an.append(m.notation())
            moves_rank.append(an)

        if not moves_rank:
            return [pre_value]
        return max(moves_rank) if pre_pos.white_moves else min(moves_rank) 
        
    def analyse(self, pos):
        pre_value = self.evaluator.eval0(pos)
        return self._analyse(pos, pre_value, 0)

