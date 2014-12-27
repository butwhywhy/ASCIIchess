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

from .chess_rules import GEN_ROOK, GEN_BISHOP, GEN_KNIGHT

class DynamicsEvaluator(Evaluator):

    def complex_eval(self, position):
        pos_array = position.position
        value = 0.5 if position.white_moves else -0.5
        value_unit = 0.001

        white_king = position.white_pieces[KING][0]
        black_king = position.black_pieces[KING][0]

        (y, x) = white_king
        for gen in GEN_ROOK + GEN_BISHOP:
            y_t = y + gen[0]
            x_t = x + gen[1]
            if 0 <= y_t < 8 and 0 <= x_t < 8:
                content = pos_array[y_t][x_t]
                if content:
                    (piece, is_black) = content
                    if is_black:
                        value += 4 * DEFAULT_VALUES[piece] * value_unit
                else:
                    value += value_unit
                y_t += gen[0]
                x_t += gen[1]

        (y, x) = black_king
        for gen in GEN_ROOK + GEN_BISHOP:
            y_t = y + gen[0]
            x_t = x + gen[1]
            if 0 <= y_t < 8 and 0 <= x_t < 8:
                content = pos_array[y_t][x_t]
                if content:
                    (piece, is_black) = content
                    if not is_black:
                        value -= 4 * DEFAULT_VALUES[piece] * value_unit
                else:
                    value -= value_unit
                y_t += gen[0]
                x_t += gen[1]

        white_queens = position.white_pieces[QUEEN]
        black_queens = position.black_pieces[QUEEN]
        if white_queens:
            value += DEFAULT_VALUES[QUEEN] * len(white_queens)
            for (y, x) in white_queens:
                for gen in GEN_ROOK + GEN_BISHOP:
                    y_t = y + gen[0]
                    x_t = x + gen[1]
                    depth = 0
                    while depth < 4 and 0 <= y_t < 8 and 0 <= x_t < 8:
                        content = pos_array[y_t][x_t]
                        if content:
                            (piece, is_black) = content
                            if is_black:
                                if piece == KING:
                                    value += (80 - 10 * depth) * value_unit
                                else:
                                    value += (4 - depth) * DEFAULT_VALUES[piece] * value_unit
                            elif piece == PAWN:
                                break
                            depth += 1
                        else:
                            value += (4 - depth/2) * value_unit
                        y_t += gen[0]
                        x_t += gen[1]
        if black_queens:
            value -= DEFAULT_VALUES[QUEEN] * len(black_queens)
            for (y, x) in black_queens:
                for gen in GEN_ROOK + GEN_BISHOP:
                    y_t = y + gen[0]
                    x_t = x + gen[1]
                    depth = 0
                    while depth < 4 and 0 <= y_t < 8 and 0 <= x_t < 8:
                        content = pos_array[y_t][x_t]
                        if content:
                            (piece, is_black) = content
                            if not is_black:
                                if piece == KING:
                                    value -= (80 - 10 * depth) * value_unit
                                else:
                                    value -= (4 - depth) * DEFAULT_VALUES[piece] * value_unit
                            elif piece == PAWN:
                                break
                            depth += 1
                        else:
                            value -= (4 - depth/2) * value_unit
                        y_t += gen[0]
                        x_t += gen[1]

        white_rooks = position.white_pieces[ROOK]
        black_rooks = position.black_pieces[ROOK]
        if white_rooks:
            value += DEFAULT_VALUES[ROOK] * len(white_rooks)
            for (y, x) in white_rooks:
                for gen in GEN_ROOK:
                    y_t = y + gen[0]
                    x_t = x + gen[1]
                    depth = 0
                    while depth < 8 and 0 <= y_t < 8 and 0 <= x_t < 8:
                        content = pos_array[y_t][x_t]
                        if content:
                            (piece, is_black) = content
                            if is_black:
                                if piece == KING:
                                    value += (80 - 10 * depth) * value_unit
                                else:
                                    value += (8 - depth) * DEFAULT_VALUES[piece] * value_unit
                            elif piece == PAWN:
                                break
                            depth += 1
                        else:
                            value += (4 - depth/2) * value_unit
                        y_t += gen[0]
                        x_t += gen[1]
                
        if black_rooks:
            value -= DEFAULT_VALUES[ROOK] * len(black_rooks)
            for (y, x) in black_rooks:
                for gen in GEN_ROOK:
                    y_t = y + gen[0]
                    x_t = x + gen[1]
                    depth = 0
                    while depth < 8 and 0 <= y_t < 8 and 0 <= x_t < 8:
                        content = pos_array[y_t][x_t]
                        if content:
                            (piece, is_black) = content
                            if not is_black:
                                if piece == KING:
                                    value -= (80 - 10 * depth) * value_unit
                                else:
                                    value -= (8 - depth) * DEFAULT_VALUES[piece] * value_unit
                            elif piece == PAWN:
                                break
                            depth += 1
                        else:
                            value -= (4 - depth/2) * value_unit
                        y_t += gen[0]
                        x_t += gen[1]

        white_bishops = position.white_pieces[BISHOP]
        black_bishops = position.black_pieces[BISHOP]
        if white_bishops:
            value += DEFAULT_VALUES[BISHOP] * len(white_bishops)
            for (y, x) in white_bishops:
                for gen in GEN_BISHOP:
                    y_t = y + gen[0]
                    x_t = x + gen[1]
                    depth = 0
                    while depth < 3 and 0 <= y_t < 8 and 0 <= x_t < 8:
                        content = pos_array[y_t][x_t]
                        if content:
                            (piece, is_black) = content
                            if is_black:
                                if piece == KING:
                                    value += (60 - 20 * depth) * value_unit
                                else:
                                    value += (6 - 2 * depth) * DEFAULT_VALUES[piece] * value_unit
                            elif piece == PAWN:
                                break
                            depth += 1
                        else:
                            value += (4 - depth) * value_unit
                        y_t += gen[0]
                        x_t += gen[1]
        if black_bishops:
            value -= DEFAULT_VALUES[BISHOP] * len(black_bishops)
            for (y, x) in black_bishops:
                for gen in GEN_BISHOP:
                    y_t = y + gen[0]
                    x_t = x + gen[1]
                    depth = 0
                    while depth < 3 and 0 <= y_t < 8 and 0 <= x_t < 8:
                        content = pos_array[y_t][x_t]
                        if content:
                            (piece, is_black) = content
                            if not is_black:
                                if piece == KING:
                                    value -= (60 - 20 * depth) * value_unit
                                else:
                                    value -= (6 - 2 * depth) * DEFAULT_VALUES[piece] * value_unit
                            elif piece == PAWN:
                                break
                            depth += 1
                        else:
                            value -= (4 - depth) * value_unit
                        y_t += gen[0]
                        x_t += gen[1]

        white_knights = position.white_pieces[KNIGHT]
        black_knights = position.black_pieces[KNIGHT]
        if white_knights:
            value += DEFAULT_VALUES[KNIGHT] * len(white_knights)
            for (y, x) in white_knights:
                for gen in GEN_KNIGHT:
                    y_t = y + gen[0]
                    x_t = x + gen[1]
                    if 0 <= y_t < 8 and 0 <= x_t < 8:
                        content = pos_array[y_t][x_t]
                        if content:
                            (piece, is_black) = content
                            if is_black:
                                if piece == KING:
                                    value += 100 * value_unit
                                else:
                                    value += 10 * DEFAULT_VALUES[piece] * value_unit
                        else:
                            value += 4 * value_unit
        if black_knights:
            value -= DEFAULT_VALUES[KNIGHT] * len(black_knights)
            for (y, x) in black_knights:
                for gen in GEN_KNIGHT:
                    y_t = y + gen[0]
                    x_t = x + gen[1]
                    if 0 <= y_t < 8 and 0 <= x_t < 8:
                        content = pos_array[y_t][x_t]
                        if content:
                            (piece, is_black) = content
                            if not is_black:
                                if piece == KING:
                                    value -= 100 * value_unit
                                else:
                                    value -= 10 * DEFAULT_VALUES[piece] * value_unit
                        else:
                            value -= 4 * value_unit

        white_pawns = position.white_pieces[PAWN]
        black_pawns = position.black_pieces[PAWN]
        if white_pawns:
            value += DEFAULT_VALUES[PAWN] * len(white_pawns)
            for (y, x) in white_pawns:
                is_passed = True
                if black_pawns:
                    for (o_y, o_x) in black_pawns:
                        if abs(o_x - x) <= 1 and o_y > y:
                            is_passed = False
                            break
                if is_passed:
                    value += 0.2
                    if y >= 3:
                        if y == 3:
                            value += 0.05
                        elif y == 4:
                            value += 0.15
                        elif y == 5:
                            value += 0.65
                        elif y == 6:
                            value += 1.9
                else:
                    if y == 4:
                        value += 0.05
                    elif y == 5:
                        value += 0.15
                for gen in ((1, 1), (1, -1)):
                    y_t = y + gen[0]
                    x_t = x + gen[1]
                    if 0 <= y_t < 8 and 0 <= x_t < 8:
                        content = pos_array[y_t][x_t]
                        if content:
                            (piece, is_black) = content
                            if is_black:
                                if piece == KING:
                                    value += 60 * value_unit
                                else:
                                    value += 12 * DEFAULT_VALUES[piece] * value_unit
        if black_pawns:
            value -= DEFAULT_VALUES[PAWN] * len(black_pawns)
            for (y, x) in black_pawns:
                is_passed = True
                if white_pawns:
                    for (o_y, o_x) in white_pawns:
                        if abs(o_x - x) <= 1 and o_y < y:
                            is_passed = False
                            break
                if is_passed:
                    value -= 0.2
                    if y <= 4:
                        if y == 4:
                            value -= 0.05
                        elif y == 3:
                            value -= 0.15
                        elif y == 2:
                            value -= 0.65
                        elif y == 1:
                            value -= 1.9
                else:
                    if y == 3:
                        value -= 0.05
                    elif y == 2:
                        value -= 0.15
                for gen in ((-1, 1), (-1, -1)):
                    y_t = y + gen[0]
                    x_t = x + gen[1]
                    if 0 <= y_t < 8 and 0 <= x_t < 8:
                        content = pos_array[y_t][x_t]
                        if content:
                            (piece, is_black) = content
                            if not is_black:
                                if piece == KING:
                                    value -= 60 * value_unit
                                else:
                                    value -= 12 * DEFAULT_VALUES[piece] * value_unit
        return value

    def eval(self, pre_pos, pre_value, move):
        sign = -1 if move.is_black else 1
        if move.is_mate():
            return sign * DEFAULT_VALUES['mate']
        if move.is_stalemate():
            return DEFAULT_VALUES['draw']
        return self.complex_eval(move.to_position)
