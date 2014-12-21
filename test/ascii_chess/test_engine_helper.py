import ascii_chess
from ascii_chess.engine_helper import *
from ascii_chess.chess_rules import KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN
from ascii_chess.chess_rules import parse_square, position_from_dict, Position
from ascii_chess.chess_play import Game

def check_best_move(pos, depth, expected):
    game = Game(pos)
    evaluator = DynamicsEvaluator()
    engine = EvalEngine(evaluator, depth)
    engine.set_game(game)
    best = engine.move()
    assert best == expected

def test_find_mate():
    pos0 = {parse_square('b8'): (KING, True), parse_square('a6'): (KING, False), parse_square('a5'): (ROOK, False)}
    pos = Position(position=position_from_dict(pos0))
    check_best_move(pos, 3, 'Ra5c5')

def test_avoid_mate():
    poslist = [(KING, True, 'b8'), (PAWN, True, 'd2'), (KING, False, 'b6'), (ROOK, False, 'h5')]
    pos0 = {parse_square(sq): (p, color) for p, color, sq in poslist}
    pos = Position(position=position_from_dict(pos0), white_moves=False)
    check_best_move(pos, 4, 'Kb8c8')

def test_material():
    poslist = {'e8': (KING, True), 'e6': (PAWN, False), 'f7': (PAWN, True), 'e7': (PAWN, True), 'd7': (PAWN, True), 'f8': (BISHOP, True), 'g8': (KNIGHT, True), 'c4': (BISHOP, False), 'e1': (KING, False)}
    pos0 = {parse_square(sq): value for sq, value in poslist.iteritems()}
    pos = Position(position=position_from_dict(pos0))
    check_best_move(pos, 3, 'exf7+')

#if __name__ == '__main__':
    #test_avoid_mate()
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

