import re

from konane_state import KonaneState

debug = False

state_str = r'''info: num=2, mvr=(\d), nxt=\d, prv=(\d)\.\s*
\[.*\s*
Empty = \{(.*)\}\s*
Who = \{(.*)\}\s*
\]'''

MVR_GROUP = 1
PRV_GROUP = 2
EMP_GROUP = 3
WHO_GROUP = 4

MVR_IDX = MVR_GROUP - 1
PRV_IDX = PRV_GROUP - 1
EMP_IDX = EMP_GROUP - 1
WHO_IDX = WHO_GROUP - 1

state_re = re.compile(state_str)

filenames = ['Random_db.txt', 'UCT_db.txt', 'AB_db.txt']
db = ""

for filename in filenames:
    f = open(filename)
    db += f.read()

states = re.findall(state_re, db)

move_str = r'\[.*decision=true.*\n'
move_re = re.compile(move_str)

moves = re.findall(move_re, db)

if debug:
    print('Num states: ', len(states))
    print('Num moves: ', len(moves))

state_move = zip(states, moves)

def str_to_konane_move(move):
    is_pass = re.search('Pass', move)
    if is_pass is not None:
        return None
    move = re.search('from=(\d+),.*to=(\d+)', move)
    frow = int(move.group(1)) // 10
    fcol = int(move.group(1)) % 10
    trow = int(move.group(2)) // 10
    tcol = int(move.group(2)) % 10
    return ((frow, fcol), (trow, tcol))

if debug:
    test = KonaneState(states[0])
    test.print()

move_dict = {}
second_move_dict = {}
konane_state_dict = {}

for state, move in state_move:
    state = KonaneState(state)

    # Cache KonaneStates based on relevant info
    try:
        state = konane_state_dict[(state.board, state.mover, state.can_pass)]
    except KeyError:
        konane_state_dict[(state.board, state.mover, state.can_pass)] = state

    # Ignore the initial removed pieces at the beginning of the game
    if state.num_pieces > 98:
        continue
    move = str_to_konane_move(move)
    if state.can_pass:
        if move is None:
            move = True
        else:
            move = False
        try:
            second_move_dict[state].add(move)
        except KeyError:
            second_move_dict[state] = set([move])
    else:
        try:
            move_dict[state].add(move)
            if debug and len(move_dict[state]) > 1:
                print(move_dict[state])
        except KeyError:
            move_dict[state] = set([move])
        if debug and not move in state.valid_moves:
            print("Move: ", move)
            print("Valid Moves: ", state.valid_moves)
            assert move in state.valid_moves

if debug:
    state = list(move_dict.keys())[0]
    possible_moves = state.valid_moves
    state.print()
    state.do_jump(possible_moves[0]).print()
