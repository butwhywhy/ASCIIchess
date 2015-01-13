import ascii_chess
from ascii_chess.variant_tree import *
from ascii_chess.chess_rules import KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN
from ascii_chess.chess_rules import parse_square, position_from_dict, Position
from ascii_chess.engine_helper import DynamicsEvaluator

EVALUATOR = DynamicsEvaluator()
def test_find_mate():
    pos0 = {parse_square('b8'): (KING, True), parse_square('a6'): (KING, False), parse_square('a5'): (ROOK, False)}
    pos = Position(position=position_from_dict(pos0))
    tree = Tree(pos, EVALUATOR)
    for i in xrange(100):
        try:
            tree.analyse_step(5)
        except Exception, e:
            print ''
            print pos
            try:
                print tree
            except:
                pass
            raise e
        best_variant = tree.best_variant()
        print i, best_variant
        if best_variant[1] > 999:
            assert best_variant[0][0] == 'Ra5c5'
            return
        if i > 30:
            assert False

def test_avoid_mate():
    poslist = [(KING, True, 'b8'), (PAWN, True, 'd2'), (KING, False, 'b6'), (ROOK, False, 'h5')]
    pos0 = {parse_square(sq): (p, color) for p, color, sq in poslist}
    pos = Position(position=position_from_dict(pos0), white_moves=False)
    tree = Tree(pos, EVALUATOR)
    for i in xrange(100):
        try:
            tree.analyse_step(5)
        except Exception, e:
            print ''
            print pos
            try:
                print tree
            except:
                pass
            raise e
        best_variant = tree.best_variant()
        print i, best_variant
        if best_variant[0][0] == 'Kb8c8' and len(best_variant[0]) > 3:
            found = True
            for ch, ch_not in tree.root.children:
                if 'd1=' == ch_not[0:3]:
                    if ch.value < 1000:
                        found = False
                        break
            if found:
                return
        if i > 40:
            assert False

def test_material():
    poslist = {'e8': (KING, True), 'e6': (PAWN, False), 'f7': (PAWN, True), 'e7': (PAWN, True), 'd7': (PAWN, True), 'f8': (BISHOP, True), 'g8': (KNIGHT, True), 'c4': (BISHOP, False), 'e1': (KING, False)}
    pos0 = {parse_square(sq): value for sq, value in poslist.iteritems()}
    pos = Position(position=position_from_dict(pos0), white_moves=True)
    tree = Tree(pos, EVALUATOR)
    for i in xrange(100):
        try:
            tree.analyse_step(5)
        except Exception, e:
            print ''
            print pos
            try:
                print tree
            except:
                pass
            raise e
        best_variant = tree.best_variant()
        print i, best_variant
        if best_variant[0][0] == 'exf7+' and len(best_variant[0]) > 5:
            return
        if i > 10:
            assert False

def test_repetion_draw_evaluation():
    poslist = {'a8': (KING, False),
            'a6': (PAWN, False),
            'c7': (KING, True)}
    pos0 = {parse_square(sq): value for sq, value in poslist.iteritems()}
    pos = Position(position=position_from_dict(pos0), white_moves=False)
    tree = Tree(pos, EVALUATOR)
    for i in xrange(10):
        try:
            tree.analyse_step(5)
        except Exception, e:
            print ''
            print pos
            try:
                print tree
            except:
                pass
            raise e
        best_variant = tree.best_variant()
        print i, best_variant
        if best_variant[0][0] == 'Kc7c8' and best_variant[1] == 0:
            return
        if i > 5:
            assert False

if __name__ == '__main__':
    import statprof
    statprof.start()
    try:
        test_find_mate()
        test_avoid_mate()
        test_material()
    finally:
        statprof.stop()
        statprof.display()
