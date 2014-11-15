import ascii_chess
from ascii_chess.chess_rules import *


def aux_check(position, solution):
    for (p, sq), sol in solution.iteritems():
        ms = set([m.notation() for m in position.moves(p, not position.white_moves, *parse_square(sq))])
        assert ms == set(sol), "%s, %s" % (p, sq)

def test_pawn_white():
    p = [
            ('king', False, 'a1'), 
            ('pawn', False, 'a2'), 
            ('pawn', False, 'h4'), 
            ('pawn', False, 'c7'), 
            ('pawn', False, 'd5'), 
            ('pawn', False, 'f2'), 
            ('king', True, 'a8'), 
            ('pawn', True, 'g5'),
            ('pawn', True, 'e5'), # black moved e7-e5
            ('pawn', True, 'a7'),
            ('pawn', True, 'c6'),
            ('pawn', True, 'd6'),
            ('pawn', True, 'f3'),
            ('bishop', True, 'd8'),
            ]
    pos = Position(
            position={parse_square(sq): (piece, color) for (piece, color, sq) in p},
            col_pawn_moved_2=4
            )
    sol = {
            ('pawn', 'a2'): ('a3', 'a4'),
            ('pawn', 'h4'): ('h5', 'hxg5'),
            ('pawn', 'c7'): ('c8=Q++', 'c8=R+', 'c8=B', 'c8=N', 
                'cxd8=Q+', 'cxd8=R+', 'cxd8=B', 'cxd8=N'),
            ('pawn', 'd5'): ('dxe6', 'dxc6'),
            ('pawn', 'f2'): (),
            }
    aux_check(pos, sol)

def test_pawn_black():
    p = [
            ('king', False, 'a1'), 
            ('pawn', False, 'a2'), 
            ('pawn', False, 'h4'), # white just moved h4
            ('pawn', False, 'c7'), 
            ('pawn', False, 'f5'), 
            ('bishop', False, 'h1'), 
            ('king', True, 'a8'), 
            ('pawn', True, 'g4'),
            ('pawn', True, 'e7'), 
            ('pawn', True, 'f6'),
            ('pawn', True, 'f3'),
            ('pawn', True, 'c2'),
            ]
    pos = Position(
            position={parse_square(sq): (piece, color) for (piece, color, sq) in p},
            white_moves=False,
            col_pawn_moved_2=7
            )
    sol = {
            ('pawn', 'g4'): ('g3', 'gxh3'),
            ('pawn', 'e7'): ('e6', 'e5'),
            ('pawn', 'f6'): (),
            ('pawn', 'f3'): (), # cannot move because black king would be in check
            ('pawn', 'c2'): ('c1=Q++', 'c1=R+', 'c1=B', 'c1=N'), 
            }
    aux_check(pos, sol)

def test_knight():
    p = [
            ('king', False, 'a1'),
            ('knight', False, 'd5'),
            ('pawn', False, 'd6'),
            ('pawn', False, 'c6'),
            ('king', True, 'a8'),
            ('knight', True, 'c7'),
            ]
    pos_white = Position(
            position={parse_square(sq): (piece, color) for (piece, color, sq) in p},
            white_moves=True
            )
    sol_white = {
            ('knight', 'd5'): ('Nd5c3', 'Nd5b4', 'Nd5b6+', 'Nd5xc7+', 
                'Nd5e7', 'Nd5f6', 'Nd5f4', 'Nd5e3')
            }
    aux_check(pos_white, sol_white)

    pos_black = Position(
            position={parse_square(sq): (piece, color) for (piece, color, sq) in p},
            white_moves=False
            )
    sol_black = {
            ('knight', 'c7'): ('Nc7b5', 'Nc7a6', 'Nc7e8', 'Nc7e6', 'Nc7xd5')
            }
    aux_check(pos_black, sol_black)

def test_king_1():
    p = [
            ('king', False, 'c2'),
            ('king', True, 'e1'),
            ('pawn', True, 'a3')
            ]
    pos_white = Position(
            position={parse_square(sq): (piece, color) for (piece, color, sq) in p},
            white_moves=True
            )
    sol_white = {
            ('king', 'c2'): ('Kc2b1', 'Kc2b3', 'Kc2c1', 'Kc2c3', 'Kc2d3')
            }
    aux_check(pos_white, sol_white)

    pos_black = Position(
            position={parse_square(sq): (piece, color) for (piece, color, sq) in p},
            white_moves=False
            )
    sol_black = {
            ('king', 'e1'): ('Ke1e2', 'Ke1f1', 'Ke1f2')
            }
    aux_check(pos_black, sol_black)

def test_king_2():
    p_base = [
            ('king', False, 'e1'),
            ('rook', False, 'h1'),
            ('rook', False, 'a1'),
            ('king', True, 'e8'),
            ('rook', True, 'h8'),
            ('rook', True, 'a8'),
            ]
    p = p_base
    pos_white = Position(
            position={parse_square(sq): (piece, color) for (piece, color, sq) in p},
            white_moves=True
            )
    sol_white = {
            ('king', 'e1'): ('O-O', 'O-O-O', 'Ke1f1', 'Ke1d1', 'Ke1f2', 'Ke1e2', 'Ke1d2')
            }
    aux_check(pos_white, sol_white)

    pos_black = Position(
            position={parse_square(sq): (piece, color) for (piece, color, sq) in p},
            white_moves=False
            )
    sol_black = {
            ('king', 'e8'): ('O-O', 'O-O-O', 'Ke8f8', 'Ke8d8', 'Ke8f7', 'Ke8e7', 'Ke8d7')
            }
    aux_check(pos_black, sol_black)

    p = p_base + [('bishop', False, 'f1'), ('bishop', False, 'b1')]
    pos_white = Position(
            position={parse_square(sq): (piece, color) for (piece, color, sq) in p},
            white_moves=True
            )
    sol_white = {
            ('king', 'e1'): ('Ke1d1', 'Ke1f2', 'Ke1e2', 'Ke1d2')
            }
    aux_check(pos_white, sol_white)

    p = p_base + [('rook', False, 'e2')]
    pos_black = Position(
            position={parse_square(sq): (piece, color) for (piece, color, sq) in p},
            white_moves=False
            )
    sol_black = {
            ('king', 'e8'): ('Ke8f8', 'Ke8d8', 'Ke8f7', 'Ke8d7')
            }
    aux_check(pos_black, sol_black)

    p = p_base + [('rook', False, 'f2'), ('rook', False, 'd2')]
    pos_black = Position(
            position={parse_square(sq): (piece, color) for (piece, color, sq) in p},
            white_moves=False
            )
    sol_black = {
            ('king', 'e8'): ('Ke8e7',)
            }
    aux_check(pos_black, sol_black)

    p = p_base + [('rook', True, 'f7'), ('rook', True, 'b7')]
    pos_black = Position(
            position={parse_square(sq): (piece, color) for (piece, color, sq) in p},
            white_moves=True
            )
    sol_black = {
            ('king', 'e1'): ('O-O-O', 'Ke1e2', 'Ke1d1', 'Ke1d2')
            }
    aux_check(pos_black, sol_black)

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



