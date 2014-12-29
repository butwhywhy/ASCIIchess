import ascii_chess
from ascii_chess.chess_rules import *


def aux_check(position, solution):
    for (p, sq), sol in solution.iteritems():
        ms = set([m.notation() for m in position.moves(p, not position.white_moves, *parse_square(sq))])
        assert ms == set(sol), "%s, %s" % (p, sq)

def test_pawn_white():
    p = [
            (KING, False, 'a1'), 
            (PAWN, False, 'a2'), 
            (PAWN, False, 'h4'), 
            (PAWN, False, 'c7'), 
            (PAWN, False, 'd5'), 
            (PAWN, False, 'f2'), 
            (KING, True, 'a8'), 
            (PAWN, True, 'g5'),
            (PAWN, True, 'e5'), # black moved e7-e5
            (PAWN, True, 'a7'),
            (PAWN, True, 'c6'),
            (PAWN, True, 'd6'),
            (PAWN, True, 'f3'),
            (BISHOP, True, 'd8'),
            ]
    pos = Position(
            position=position_from_dict({parse_square(sq): (piece, color) for (piece, color, sq) in p}),
            col_pawn_moved_2=4
            )
    sol = {
            (PAWN, 'a2'): ('a3', 'a4'),
            (PAWN, 'h4'): ('h5', 'hxg5'),
            (PAWN, 'c7'): ('c8=Q++', 'c8=R+', 'c8=B', 'c8=N', 
                'cxd8=Q+', 'cxd8=R+', 'cxd8=B', 'cxd8=N'),
            (PAWN, 'd5'): ('dxe6', 'dxc6'),
            (PAWN, 'f2'): (),
            }
    aux_check(pos, sol)

def test_pawn_black():
    p = [
            (KING, False, 'a1'), 
            (PAWN, False, 'a2'), 
            (PAWN, False, 'h4'), # white just moved h4
            (PAWN, False, 'c7'), 
            (PAWN, False, 'f5'), 
            (BISHOP, False, 'h1'), 
            (KING, True, 'a8'), 
            (PAWN, True, 'g4'),
            (PAWN, True, 'e7'), 
            (PAWN, True, 'f6'),
            (PAWN, True, 'f3'),
            (PAWN, True, 'c2'),
            ]
    pos = Position(
            position=position_from_dict({parse_square(sq): (piece, color) for (piece, color, sq) in p}),
            white_moves=False,
            col_pawn_moved_2=7
            )
    sol = {
            (PAWN, 'g4'): ('g3', 'gxh3'),
            (PAWN, 'e7'): ('e6', 'e5'),
            (PAWN, 'f6'): (),
            (PAWN, 'f3'): (), # cannot move because black king would be in check
            (PAWN, 'c2'): ('c1=Q++', 'c1=R+', 'c1=B', 'c1=N'), 
            }
    aux_check(pos, sol)

def test_knight():
    p = [
            (KING, False, 'a1'),
            (KNIGHT, False, 'd5'),
            (PAWN, False, 'd6'),
            (PAWN, False, 'c6'),
            (KING, True, 'a8'),
            (KNIGHT, True, 'c7'),
            ]
    pos_white = Position(
            position=position_from_dict({parse_square(sq): (piece, color) for (piece, color, sq) in p}),
            white_moves=True
            )
    sol_white = {
            (KNIGHT, 'd5'): ('Nd5c3', 'Nd5b4', 'Nd5b6+', 'Nd5xc7+', 
                'Nd5e7', 'Nd5f6', 'Nd5f4', 'Nd5e3')
            }
    aux_check(pos_white, sol_white)

    pos_black = Position(
            position=position_from_dict({parse_square(sq): (piece, color) for (piece, color, sq) in p}),
            white_moves=False
            )
    sol_black = {
            (KNIGHT, 'c7'): ('Nc7b5', 'Nc7a6', 'Nc7e8', 'Nc7e6', 'Nc7xd5')
            }
    aux_check(pos_black, sol_black)

def test_king_1():
    p = [
            (KING, False, 'c2'),
            (KING, True, 'e1'),
            (PAWN, True, 'a3')
            ]
    pos_white = Position(
            position=position_from_dict({parse_square(sq): (piece, color) for (piece, color, sq) in p}),
            white_moves=True
            )
    sol_white = {
            (KING, 'c2'): ('Kc2b1', 'Kc2b3', 'Kc2c1', 'Kc2c3', 'Kc2d3')
            }
    aux_check(pos_white, sol_white)

    pos_black = Position(
            position=position_from_dict({parse_square(sq): (piece, color) for (piece, color, sq) in p}),
            white_moves=False
            )
    sol_black = {
            (KING, 'e1'): ('Ke1e2', 'Ke1f1', 'Ke1f2')
            }
    aux_check(pos_black, sol_black)

def test_king_2():
    p_base = [
            (KING, False, 'e1'),
            (ROOK, False, 'h1'),
            (ROOK, False, 'a1'),
            (KING, True, 'e8'),
            (ROOK, True, 'h8'),
            (ROOK, True, 'a8'),
            ]
    p = p_base
    pos_white = Position(
            position=position_from_dict({parse_square(sq): (piece, color) for (piece, color, sq) in p}),
            white_moves=True
            )
    sol_white = {
            (KING, 'e1'): ('O-O', 'O-O-O', 'Ke1f1', 'Ke1d1', 'Ke1f2', 'Ke1e2', 'Ke1d2')
            }
    aux_check(pos_white, sol_white)

    pos_black = Position(
            position=position_from_dict({parse_square(sq): (piece, color) for (piece, color, sq) in p}),
            white_moves=False
            )
    sol_black = {
            (KING, 'e8'): ('O-O', 'O-O-O', 'Ke8f8', 'Ke8d8', 'Ke8f7', 'Ke8e7', 'Ke8d7')
            }
    aux_check(pos_black, sol_black)

    p = p_base + [(BISHOP, False, 'f1'), (BISHOP, False, 'b1')]
    pos_white = Position(
            position=position_from_dict({parse_square(sq): (piece, color) for (piece, color, sq) in p}),
            white_moves=True
            )
    sol_white = {
            (KING, 'e1'): ('Ke1d1', 'Ke1f2', 'Ke1e2', 'Ke1d2')
            }
    aux_check(pos_white, sol_white)

    p = p_base + [(ROOK, False, 'e2')]
    pos_black = Position(
            position=position_from_dict({parse_square(sq): (piece, color) for (piece, color, sq) in p}),
            white_moves=False
            )
    sol_black = {
            (KING, 'e8'): ('Ke8f8', 'Ke8d8', 'Ke8f7', 'Ke8d7')
            }
    aux_check(pos_black, sol_black)

    p = p_base + [(ROOK, False, 'f2'), (ROOK, False, 'd2')]
    pos_black = Position(
            position=position_from_dict({parse_square(sq): (piece, color) for (piece, color, sq) in p}),
            white_moves=False
            )
    sol_black = {
            (KING, 'e8'): ('Ke8e7',)
            }
    aux_check(pos_black, sol_black)

    p = p_base + [(ROOK, True, 'f7'), (ROOK, True, 'b7')]
    pos_black = Position(
            position=position_from_dict({parse_square(sq): (piece, color) for (piece, color, sq) in p}),
            white_moves=True
            )
    sol_black = {
            (KING, 'e1'): ('O-O-O', 'Ke1e2', 'Ke1d1', 'Ke1d2')
            }
    aux_check(pos_black, sol_black)

def test_king_3():
    p = [
            (KING, False, 'e1'),
            (BISHOP, False, 'c3'),
            (KING, True, 'e8'),
            (ROOK, True, 'h8')
            ]
    pos = Position(
            position=position_from_dict({parse_square(sq): (piece, color) for (piece, color, sq) in p}),
            white_moves=True
            )
    assert pos.black_can_castle_short
    pos = pos.move('Bxh8')
    assert not pos.black_can_castle_short

def test_position_1():
    pos = Position()
    game = [
            'd4', 'c5', 
            'dxc5', 'Nf6', 
            'e4', 'e6', 
            'e5', 'b5', 
            'cxb6', 'Bc5', 
            'exf6', 'Nc6', 
            'fxg7', 'Qf6',
            'gxh8=Q+',
            ]
    for m in game:
        pos = pos.move(m)
    all_moves = set([m.notation() for m in pos.all_moves()])
    assert pos.is_check()
    assert set(['Ke8e7', 'Bc5f8', 'Qf6xh8']) == all_moves

    pos = pos.move('Ke7')
    pos = pos.move('Nc3')
    pos = pos.move('Qxf2++')
    assert not list(pos.all_moves())
    assert pos.is_mate()

def test_result_1():
    p = [
            (KING, False, 'a1'), 
            (KING, True, 'a3'), 
            (ROOK, True, 'f1'),
            ]
    pos = Position(
            position=position_from_dict({parse_square(sq): (piece, color) for (piece, color, sq) in p}),
            white_moves=True
            )
    assert pos.result() == BLACK_WINS

def test_result_2():
    p = [
            (KING, False, 'c1'), 
            (ROOK, False, 'a5'),
            (KING, True, 'a1'), 
            ]
    pos = Position(
            position=position_from_dict({parse_square(sq): (piece, color) for (piece, color, sq) in p}),
            white_moves=False
            )
    assert pos.result() == WHITE_WINS

def test_result_3():
    p = [
            (KING, False, 'c1'), 
            (ROOK, False, 'h2'),
            (KING, True, 'a1'), 
            ]
    pos = Position(
            position=position_from_dict({parse_square(sq): (piece, color) for (piece, color, sq) in p}),
            white_moves=False
            )
    assert pos.result() == DRAW

def test_result_4():
    p = [
            (KING, False, 'c1'), 
            (BISHOP, False, 'h2'),
            (KING, True, 'a1'), 
            ]
    pos = Position(
            position=position_from_dict({parse_square(sq): (piece, color) for (piece, color, sq) in p}),
            white_moves=False
            )
    assert pos.result() == DRAW

def test_result_5():
    p = [
            (KING, False, 'c1'), 
            (BISHOP, False, 'h2'),
            (KNIGHT, False, 'h7'),
            (KING, True, 'a1'), 
            ]
    pos = Position(
            position=position_from_dict({parse_square(sq): (piece, color) for (piece, color, sq) in p}),
            white_moves=False
            )
    assert pos.result() is None

def test_result_6():
    p = [
            (KING, False, 'c1'), 
            (PAWN, False, 'h2'),
            (KING, True, 'b5'), 
            ]
    pos = Position(
            position=position_from_dict({parse_square(sq): (piece, color) for (piece, color, sq) in p}),
            white_moves=False
            )
    assert pos.result() is None

def test_result_7():
    p = [
            (KING, True, 'e8'), 
            (KING, False, 'e1'), 
            (BISHOP, False, 'e5'), 
            (BISHOP, True, 'e6'), 
            ]
    pos = Position(
            position=position_from_dict({parse_square(sq): (piece, color) for (piece, color, sq) in p}),
            white_moves=False
            )
    for i in xrange(99):
        assert pos.result() is None
        notation = None
        for m in pos.all_moves():
            if not m.is_capture and not m.to_position.result():
                notation = m.notation()
                break
        assert notation, i
        pos = pos.move(notation)
    for m in pos.all_moves():
        if not m.is_capture:
            notation = m.notation()
            break
    assert notation
    pos = pos.move(notation)
    assert pos.result() == DRAW, pos.moves_for_50


