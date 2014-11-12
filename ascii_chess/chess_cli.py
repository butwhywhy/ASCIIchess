from .chess_rules import IllegalMoveException
from .chess_play import GamingEngine

def play():
    help_message = '''Options:
        - help
        - diagram
        - play
        - quit
        - <move notation>'''
    move_place_holder = ' ... '
    white_place_holder = ' ! '
    black_place_holder = white_place_holder + move_place_holder
    white_prompt = '>> '
    black_prompt = white_prompt + move_place_holder
    busy_msg = 'Engine thinking ...'
    def print_engine_move(move):
        if move != None:
            print '%s%s' %(white_place_holder if gaming.game.turn() == 'black' 
                    else black_place_holder, move)

    from .engine_helper import SimpleEvaluator, EvalEngine
    simple_engine = EvalEngine(SimpleEvaluator())
    gaming = GamingEngine(engine=simple_engine)

    poslist = {'e8': ('king', True), 'e6': ('pawn', False), 'f7': ('pawn', True), 'e7': ('pawn', True), 'd7': ('pawn', True), 'f8': ('bishop', True), 'g8': ('knight', True), 'c4': ('bishop', False), 'e1': ('king', False)}
    from .chess_rules import parse_square, Position
    pos0 = {parse_square(sq): value for sq, value in poslist.iteritems()}
    gaming = GamingEngine(engine=simple_engine, init_pos=Position(pos0))
    #gaming = GamingEngine()

    print gaming.draw()
    while gaming.game.result() is None:
        user_action = raw_input(white_prompt if gaming.game.turn() == 'white' 
                else black_prompt)
        if user_action == 'help':
            print help_message
        elif user_action == 'quit':
            from sys import exit
            exit()
        elif user_action == 'diagram':
            print gaming.draw()
        elif user_action == 'play':
            print busy_msg
            print_engine_move(gaming.play())
        else:
            try:
                reply = gaming.user_move(user_action)
            except IllegalMoveException:
                print "Illegal move '%s'." % user_action
                print "Try again or type 'help' to see your options."
                continue
            print busy_msg
            print_engine_move(gaming.play())
    print gaming.game.result()

if __name__ == '__main__':
    play()
