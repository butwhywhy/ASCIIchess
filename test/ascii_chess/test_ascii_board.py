import ascii_chess
from ascii_chess.ascii_chess import *
from ascii_chess.chess_rules import parse_square

def test_is_functional():
    # TODO: include assertions
    side = 10
    board = ChessBoard(side, 0, 0.7)
    print board
    
    for p in ascii_pieces:
        pp = ascii_pieces[p]
        print pp
        print p, pp.get_height(), pp.get_width()
    black_pieces = ChessPiecesSet(side, 1)
    for p in black_pieces.pieces.values():
        print p
        print p.get_height(), p.get_width()
    white_pieces = ChessPiecesSet(side, 0.2)
    for p in white_pieces.pieces.values():
        print p
        print p.get_height(), p.get_width()

    board.add_piece(white_pieces['pawn'], *parse_square('d4'))
    board.add_piece(white_pieces['pawn'], *parse_square('e4'))
    board.add_piece(black_pieces['pawn'], *parse_square('d5'))
    board.add_piece(black_pieces['pawn'], *parse_square('e5'))
    print board

    board.set_position(white_pieces, black_pieces)
    print board



