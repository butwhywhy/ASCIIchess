from .chess_rules import Position, WHITE_WINS, BLACK_WINS, DRAW
from .ascii_board import ChessBoard, ChessPiecesSet

class Game(object):

    @classmethod
    def fromPGN(cls, PGN):
        import pgn
        pgnfields = pgn.loads(PGN)[0]

        FEN = pgnfields.fen
        position = Position.fromFEN(FEN) if FEN else None

        game = cls(init_pos=position, 
                event=pgnfields.event,
                white_player=pgnfields.white, 
                black_player=pgnfields.black)

        results = [WHITE_WINS, BLACK_WINS, DRAW]
        for m in pgnfields.moves:
            # Omitting comments ...
            if '{' in m:
                continue
            # and result
            if m in results:
                break
            game.move(m)
        return game

    def __init__(self, init_pos=None, event=None,
            white_player=None, black_player=None):
        if init_pos is None:
            init_pos = Position()
        self.history = [(None,  init_pos)]
        self.event = event
        self.white_player = white_player
        self.black_player = black_player

    def toPGN(self):
        import pgn
        PGNgame = pgn.PGNGame(result=self.result(),
                event=self.event,
                white=self.white_player,
                black=self.black_player)
        init_pos = self.history[0][1]
        PGNgame.fen = init_pos.toFEN()
        moves = self.all_notation()
        r = self.result()
        if r:
            moves.append(r)
        PGNgame.moves = moves
        return PGNgame.dumps()

    def _current_position(self):
        return self.history[-1][1]

    def current_position(self):
        return self._current_position().get_position()

    def last_move(self):
        return self.history[-1][0].notation()

    def move(self, move_not):
        self.history.append((move_not, self._current_position().move(move_not)))

    def result(self):
        if self._history().count(self._current_position()) > 2:
            return DRAW
        return self._current_position().result()

    def turn(self):
        return 'white' if self._current_position().white_moves else 'black'

    def _history(self):
        return map(lambda x: x[1], self.history)

    def all_notation(self):
        return [n for (n, _) in self.history if n]

    def back(self):
        if len(self.history) > 1:
            self.history.pop()

class Engine(object):

    def set_game(self, game):
        self.game = game

    def move(self):
        raise Exception('Must be implemented by subclasses')

    def start(self, pipe):
        raise Exception('Must be implemented by subclasses')
    
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
    
    def __init__(self, game=None, init_pos=None, engine=None):
        if not game:
            game = Game(init_pos)
        self.game = game
        if engine is None:
            engine = RandomEngine()
        self.engine = engine
        self.engine.set_game(self.game)
        self.set_graphics()

    def play(self):
        move = self.engine.move()
        if move is not None:
            self.game.move(move)
        return move

    def start(self, pipe):
        self.engine.start(pipe)

    def user_move(self, move):
        self.game.move(move)

    def set_graphics(self, side=10, board_white=0, board_black=0.7, 
            pieces_white=0.2, pieces_black=1):
        self.board = ChessBoard(side, board_white, board_black)
        self.white_set = ChessPiecesSet(side, pieces_white)
        self.black_set = ChessPiecesSet(side, pieces_black)

    def draw(self):
        self.board.set_position(self.white_set, self.black_set, 
                self.game.current_position())
        return repr(self.board)

    def back(self):
        self.game.back()
