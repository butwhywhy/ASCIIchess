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
    busy_msg = "Engine thinking ... In a hurry? Type 'now'"
    def print_engine_move(move):
        if move != None:
            print '%s%s' %(white_place_holder if gaming.game.turn() == 'black' 
                    else black_place_holder, move)

    from .engine_helper import SimpleEvaluator, EvalEngine
    from .variant_tree import TreeEngine
    #simple_engine = EvalEngine(SimpleEvaluator())
    simple_engine = TreeEngine(SimpleEvaluator())
    gaming = GamingEngine(engine=simple_engine)

    ## To test from a particular position
    # poslist = {'e8': (KING, True), 'e6': (PAWN, False), 'f7': (PAWN, True), 'e7': (PAWN, True), 'd7': (PAWN, True), 'f8': (BISHOP, True), 'g8': (KNIGHT, True), 'c4': (BISHOP, False), 'e1': (KING, False)}
    # from .chess_rules import parse_square, Position
    # pos0 = {parse_square(sq): value for sq, value in poslist.iteritems()}
    # gaming = GamingEngine(engine=simple_engine, init_pos=Position(pos0))
    gaming = GamingEngine(engine=simple_engine)

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
            thinking_interact(gaming, print_engine_move)
        else:
            try:
                reply = gaming.user_move(user_action)
            except IllegalMoveException:
                print "Illegal move '%s'." % user_action
                print "Try again or type 'help' to see your options."
                continue
            print busy_msg
            thinking_interact(gaming, print_engine_move)
    print gaming.game.result()

from multiprocessing import Process, Pipe
import os, sys
import time
def thinking_interact(gaming, print_engine_move):
    def compute(pipe, gaming):
        gaming.start(pipe)

    def listen_user(fileno, pipe):
        sys.stdin = os.fdopen(fileno)
        while True:
            user_input = raw_input()
            if user_input == 'now':
                pipe.send('now')
                break
            print 'Command not recognized: %s' % user_input
    (pipe_comp1, pipe_comp2) = Pipe()
    (pipe_cli1, pipe_cli2) = Pipe()
    p_engine = Process(target=compute, args=(pipe_comp1, gaming))
    p_cli = Process(target=listen_user, args=(sys.stdin.fileno(), pipe_cli1))
    p_engine.start()
    p_cli.start()
    while True:
        if pipe_comp2.poll():
            best_variant = pipe_comp2.recv()
            print best_variant
            move = best_variant[0][0]

            gaming.user_move(move)

            print_engine_move(move)
            p_cli.terminate()
            break
        if pipe_cli2.poll():
            pipe_comp2.send(pipe_cli2.recv())
        time.sleep(0.5)

if __name__ == '__main__':
    play()
