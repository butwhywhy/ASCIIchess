from .chess_rules import Position
from .ascii_chess import ChessBoard, ChessPiecesSet

class Game(object):

    def __init__(self, init_pos=None):
        if init_pos is None:
            init_pos = Position()
        self.history = [(None,  init_pos)]

    def _current_position(self):
        return self.history[-1][1]

    def current_position(self):
        return self._current_position().get_position()

    def last_move(self):
        return self.history[-1][0].notation()

    def move(self, move_not):
        self.history.append((move_not, self._current_position().move(move_not)))

    def result(self):
        return self._current_position().result()

    def turn(self):
        return 'white' if self._current_position().white_moves else 'black'

class Engine(object):

    def set_game(self, game):
        self.game = game

    def move(self):
        raise  Exception('Must be implemented by subclasses')
    
class RandomEngine(Engine):

    def move(self):
        import random
        all_moves = []
        for m in self.game._current_position().all_moves():
            all_moves.append(m)
        if not all_moves:
            return None
        return random.choice(all_moves).notation()

class GamingEngine(object):
    
    def __init__(self, init_pos=None, engine=None, engine_is_white=False):
        self.game = Game(init_pos)
        if engine is None:
            engine = RandomEngine()
        self.engine = engine
        self.engine.set_game(self.game)
        self.engine_is_white = engine_is_white
        self.set_graphics()

    def play(self):
        move = self.engine.move()
        if move is not None:
            self.game.move(move)
        return move

    def user_move(self, move):
        self.game.move(move)

    def set_graphics(self, side=10, board_white=0, board_black=0.7, 
            pieces_white=0.2, pieces_black=1):
        self.board = ChessBoard(side, board_white, board_black)
        self.white_set = ChessPiecesSet(side, pieces_white)
        self.black_set = ChessPiecesSet(side, pieces_black)

    def draw(self):
        self.board.set_position(self.white_set, self.black_set, self.game.current_position())
        return repr(self.board)

