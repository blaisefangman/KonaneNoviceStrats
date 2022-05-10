from konane_state import KonaneState
from deap_konane import applyHeuristic

import mcts
from konane_mcts_wrapper import MCTSKonaneState

import random

starting_states = [((0,0,2,1,2,1,2,1,2,1), 
                    (1,2,1,2,1,2,1,2,1,2),
                    (2,1,2,1,2,1,2,1,2,1),
                    (1,2,1,2,1,2,1,2,1,2),
                    (2,1,2,1,2,1,2,1,2,1),
                    (1,2,1,2,1,2,1,2,1,2),
                    (2,1,2,1,2,1,2,1,2,1),
                    (1,2,1,2,1,2,1,2,1,2),
                    (2,1,2,1,2,1,2,1,2,1),
                    (1,2,1,2,1,2,1,2,1,2)),

                   ((2,1,2,1,2,1,2,1,2,1), 
                    (1,2,1,2,1,2,1,2,1,2),
                    (2,1,2,1,2,1,2,1,2,1),
                    (1,2,1,2,1,2,1,2,1,2),
                    (2,1,2,1,2,1,2,1,2,1),
                    (1,2,1,2,1,2,1,2,1,2),
                    (2,1,2,1,2,1,2,1,2,1),
                    (1,2,1,2,1,2,1,2,1,2),
                    (2,1,2,1,2,1,2,1,2,0),
                    (1,2,1,2,1,2,1,2,1,0)),
                   
                   ((2,1,2,1,2,1,2,1,2,1), 
                    (1,2,1,2,1,2,1,2,1,2),
                    (2,1,2,1,2,1,2,1,2,1),
                    (1,2,1,2,1,0,1,2,1,2),
                    (2,1,2,1,2,0,2,1,2,1),
                    (1,2,1,2,1,2,1,2,1,2),
                    (2,1,2,1,2,1,2,1,2,1),
                    (1,2,1,2,1,2,1,2,1,2),
                    (2,1,2,1,2,1,2,1,2,1),
                    (1,2,1,2,1,2,1,2,1,2)),
                   
                   ((2,1,2,1,2,1,2,1,2,1), 
                    (1,2,1,2,1,2,1,2,1,2),
                    (2,1,2,1,2,1,2,1,2,1),
                    (1,2,1,2,1,2,1,2,1,2),
                    (2,1,2,1,2,1,2,1,2,1),
                    (1,2,1,2,0,0,1,2,1,2),
                    (2,1,2,1,2,1,2,1,2,1),
                    (1,2,1,2,1,2,1,2,1,2),
                    (2,1,2,1,2,1,2,1,2,1),
                    (1,2,1,2,1,2,1,2,1,2))]

def heuristic_agent(state):
    """
    beg = [-1, 8, 4, -1, 2, -2, 4, 0, 0, 8, 2, 0, -2, 2, -2, -1, 8, -8, -8, 1]
    mid = [-4, -1, 8, -1, 1, 1, 4, -4, 0, -1, 8, -8, 1, 8, 2, -2, -2, 1, -1, 4]
    end = [-4, -4, 2, 2, 0, 1, -4, -8, -2, 1, -2, 2, -1, -4, 2, -8, -8, -2, 1, -1]
    """
    beg = [4, 8, 8, 4, 2, 4, 8, 4, 0, 8, 2, 0, 0, 4, 0, 1, 8, 0, 0, 8]
    mid = [2, 1, 8, 4, 4, 0, 4, 1, 2, 1, 8, 0, 0, 2, 8, 4, 8, 0, 0, 4]
    end = [8, 0, 8, 8, 8, 1, 2, 1, 0, 2, 4, 1, 2, 1, 4, 1, 0, 4, 1, 0]

    if state.num_pieces > 60:
        ind = beg
    elif state.num_pieces > 20:
        ind = mid
    else:
        ind = end

    best_moves = []
    best_score = float('-inf')

    for move in state.valid_moves:
        score = applyHeuristic(ind, state, move)
        if score > best_score:
            best_score = score
            best_moves = [move]
        elif score == best_score:
            best_moves.append(move)

    return random.choice(best_moves)

num_trials = 0
trials_to_do = 100

p1_wins = 0
p2_wins = 0

opp = "rand"
rand_agent = 1

#opp = "mcts"
mcts_agent = 1
mcts_iters = 100

if opp == "rand":
    while num_trials < trials_to_do:
        state = KonaneState(random.choice(starting_states), 1, 98)
        
        while len(state.valid_moves) > 0:
            if state.mover == rand_agent:
                state = state.do_jump(random.choice(state.valid_moves))
            else:
                state = state.do_jump(heuristic_agent(state))

        if state.mover == rand_agent:
            if rand_agent == 1:
                p2_wins += 1
            else:
                p1_wins += 1

        num_trials += 1
        print(num_trials)
        rand_agent = (rand_agent % 2) + 1

elif opp == "mcts":
    while num_trials < trials_to_do:
        state = KonaneState(random.choice(starting_states), 1, 98)
        mcts_strat = mcts.mcts_strategy(mcts_iters)
        
        while len(state.valid_moves) > 0:
            if state.mover == mcts_agent:
                state = state.do_jump(mcts_strat(MCTSKonaneState(state)))
            else:
                state = state.do_jump(heuristic_agent(state))

        if state.mover == mcts_agent:
            if mcts_agent == 1:
                p2_wins += 1
            else:
                p1_wins += 1

        num_trials += 1
        print(num_trials)
        mcts_agent = (mcts_agent % 2) + 1

import time
timestr = time.strftime('%Y-%m-%d-%H-%M')
filename = 'results/{0}_{1}_{2}.txt'.format(opp, "simulation", timestr)
f = open(filename, 'w')

f.write("Games Played: {}\n".format(trials_to_do))
if opp == "mcts":
    f.write("Opponent: MCTS({})\n".format(mcts_iters))
else:
    f.write("Opponent: Random\n")
f.write("Heuristic Agent Player 1 Win Rate: {}\n".format(p1_wins / (trials_to_do / 2)))
f.write("Heuristic Agent Player 2 Win Rate: {}\n".format(p2_wins / (trials_to_do / 2)))
f.write("Heuristic Agent Win Rate: {}\n".format((p1_wins + p2_wins) / trials_to_do))
