import sys, traceback, time, os.path
from multiprocessing import Process, Pipe
from os import fdopen
from .chess_rules import IllegalMoveException
from .chess_play import Game, GamingEngine

def play():
    help_message = '''Options:
        - <move notation>
        - help
        - diagram
        - play
        - back
        - quit
        - new
        - export
        - import
        - set
        '''
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

    from .engine_helper import DynamicsEvaluator, EvalEngine
    from .variant_tree import TreeEngine
    #simple_engine = EvalEngine(DynamicsEvaluator())
    simple_engine = TreeEngine(DynamicsEvaluator())
    gaming = GamingEngine(engine=simple_engine)

    ## To test from a particular position
    # poslist = {'e8': (KING, True), 'e6': (PAWN, False), 'f7': (PAWN, True), 'e7': (PAWN, True), 'd7': (PAWN, True), 'f8': (BISHOP, True), 'g8': (KNIGHT, True), 'c4': (BISHOP, False), 'e1': (KING, False)}
    # from .chess_rules import parse_square, Position
    # pos0 = {parse_square(sq): value for sq, value in poslist.iteritems()}
    # gaming = GamingEngine(engine=simple_engine, init_pos=Position(pos0))



    saved = True
    first_move = True

    def set_players():
        if gaming.game.turn() == 'white':
            wp = type(gaming.engine)
            bp = 'You'
        else:
            wp = 'You'
            bp = type(gaming.engine)
        gaming.game.white_player = wp
        gaming.game.black_player = bp


    class Options(object):
        def __init__(self, level=3, human_only=False, size='m'):
            self.level = level
            self.human_only = human_only
            self.size = size


    def reset_graphics():
        if options.size == 's':
            side = 10
        elif options.size == 'm':
            side = 20
        else:
            side = 40
        gaming.set_graphics(side=side)

    def set_options():
        options_help = '''You can set the following options:
            - done                      Exit this menu
            - level 0-7                 Engine level, increasing strength
            - engine on/off             Switch on/off engine
            - analysis on/off           Show or hide main analysed variants
            - blind on/off              Blind chess: hide/show board
            - board s/m/l               Board size small, medium or large
        '''
        print options_help
        print "Current values: level %d, engine %s, analysis %s, blind %s, board %s" % (
                options.level,
                'off' if options.human_only else 'on',
                'on' if simple_engine.print_analysis else 'off',
                'on',
                'large' if options.size.lower() == 'l' else (
                    'small' if options.size.lower() == 's'
                    else 'medium')
                )

        while True:
            user_action = raw_input('set: ')
            if user_action == 'done':
                break
            if user_action == 'engine on':
                options.human_only = False
            elif user_action == 'engine off':
                options.human_only = True
            elif user_action == 'analysis on':
                simple_engine.print_analysis = 3
            elif user_action == 'analysis off':
                simple_engine.print_analysis = 0
            elif user_action == 'blind on':
                pass
                #print 'Option not available yet'
            elif user_action == 'blind off':
                print 'Option not available yet'
            else:
                import re
                mlevel = re.match('level ([0-7])$', user_action)
                if mlevel:
                    options.level = int(mlevel.groups()[0])
                    continue
                msize = re.match('board ([sSmMlL])', user_action)
                if msize:
                    options.size = msize.groups()[0].lower()
                    reset_graphics()
                    continue
                print 'Option not recognized:', user_action
                print options_help

    options = Options()
    reset_graphics()

    print gaming.draw()

    while True:
        if gaming.game.result():
            print gaming.game.result()
            user_action = raw_input("Game ended. What do you want to do? ")
            if user_action == 'play':
                print "Can't continue ended game"
                continue
        else:
            user_action = raw_input(
                    white_prompt if gaming.game.turn() == 'white' 
                    else black_prompt)
        if user_action == 'help':
            print help_message
        elif user_action == 'quit':
            can_quit = saved
            if not can_quit:
                bool_reply = raw_input("Do you want to save the current " 
                        + "game before leaving it? ")
                if bool_reply and bool_reply != "no":
                    can_quit = export_game(gaming.game)
                else:
                    can_quit = True
            if can_quit:
                sys.exit()
        elif user_action == 'diagram':
            print gaming.draw()
        elif user_action == 'play':
            if saved:
                saved = False
            if first_move:
                set_players()
                first_move = False
            print busy_msg
            thinking_interact(gaming, print_engine_move, options.level)
        elif user_action == 'back':
            gaming.back()
        elif user_action == 'export':
            saved = export_game(gaming.game)
        elif user_action in ('import', 'new'):
            if not saved:
                bool_reply = raw_input("Do you want to save the current " 
                        + "game before leaving it? ")
                if bool_reply and bool_reply != "no":
                    saved = export_game(gaming.game)
            if user_action == 'import':
                game = import_game()
            else:
                game = None
            gaming = GamingEngine(game=game, engine=simple_engine)
            saved = True
            first_move = True
            print gaming.draw()
        elif user_action == 'set':
            set_options()

        else:
            try:
                gaming.user_move(user_action)
            except IllegalMoveException:
                print "Illegal move '%s'." % user_action
                print "Try again or type 'help' to see your options."
                continue
            if saved:
                saved = False
            if gaming.game.result():
                continue
            if first_move:
                set_players()
                first_move = False
            if not options.human_only:
                print busy_msg
                thinking_interact(gaming, print_engine_move, options.level)

def export_game(game):
    default_name = time.strftime('%Y%m%d%H%M%S') + '.png'
    file_to_export = raw_input("Type the name of the file to save the game ("
            + default_name + "): ")
    if not file_to_export:
        file_to_export = default_name
    if not file_to_export.endswith('.png'):
        file_to_export += '.png'
    if os.path.exists(file_to_export):
        print "FILE %s ALREADY EXISTS" % file_to_export
        print "GAME COULD NOT BE EXPORTED"
        return False
    try:
        with open(file_to_export, mode='w') as f:
            f.write(game.toPGN())
        print "Game saved in " + file_to_export
        return True
    except Exception, e:
        print "An error occurred while exporting game"
        print traceback.format_exc()
        return False

def import_game():
    file_to_import = raw_input(
            "Type the name of the file containing the game to import: ")
    if file_to_import:
        try:
            with open(file_to_import) as f:
                PGN = f.read()
            return Game.fromPGN(PGN)
        except Exception, e:
            print "An error occurred while exporting game"
            print traceback.format_exc()
    return None

def thinking_interact(gaming, print_engine_move, level):
    def compute(pipe, gaming):
        gaming.start(pipe)

    def listen_user(fileno, pipe):
        sys.stdin = fdopen(fileno)
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

    time_spent = 0
    if level == 0:
        move_seconds = 3
    elif level == 1:
        move_seconds = 7
    elif level == 2:
        move_seconds = 12
    elif level == 3:
        move_seconds = 20
    elif level == 4:
        move_seconds = 30
    elif level == 5:
        move_seconds = 60
    elif level == 6:
        move_seconds = 120
    else:
        move_seconds = 0

    while True:
        if pipe_comp2.poll():
            best_variant = pipe_comp2.recv()
            #print best_variant
            move = best_variant[0][0]

            gaming.user_move(move)

            print_engine_move(move)
            p_cli.terminate()
            break
        time.sleep(0.5)
        time_spent += 0.5
        if pipe_cli2.poll():
            pipe_comp2.send(pipe_cli2.recv())
        if move_seconds and time_spent > move_seconds:
            pipe_comp2.send('now')

if __name__ == '__main__':
    play()
