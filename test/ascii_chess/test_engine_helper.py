import ascii_chess
from ascii_chess.engine_helper import *
from ascii_chess.chess_rules import parse_square, position_from_dict, Position
from ascii_chess.chess_play import Game

def check_best_move(pos, depth, expected):
    game = Game(pos)
    evaluator = SimpleEvaluator()
    engine = EvalEngine(evaluator, depth)
    engine.set_game(game)
    best = engine.move()
    assert best == expected

def test_find_mate():
    pos0 = {parse_square('b8'): ('king', True), parse_square('a6'): ('king', False), parse_square('a5'): ('rook', False)}
    pos = Position(position=position_from_dict(pos0))
    check_best_move(pos, 3, 'Ra5c5')

def test_avoid_mate():
    poslist = [('king', True, 'b8'), ('pawn', True, 'd2'), ('king', False, 'b6'), ('rook', False, 'h5')]
    pos0 = {parse_square(sq): (p, color) for p, color, sq in poslist}
    pos = Position(position=position_from_dict(pos0), white_moves=False)
    check_best_move(pos, 4, 'Kb8c8')

def test_material():
    poslist = {'e8': ('king', True), 'e6': ('pawn', False), 'f7': ('pawn', True), 'e7': ('pawn', True), 'd7': ('pawn', True), 'f8': ('bishop', True), 'g8': ('knight', True), 'c4': ('bishop', False), 'e1': ('king', False)}
    pos0 = {parse_square(sq): value for sq, value in poslist.iteritems()}
    pos = Position(position=position_from_dict(pos0))
    check_best_move(pos, 3, 'exf7+')

