import numpy
import random
import parse_db_to_dict
import konane_state

from deap import base, creator, tools, algorithms

import multiprocessing

#POSSIBLE_VALUES = [-8, -4, -2, -1, 0, 1, 2, 4, 8]
POSSIBLE_VALUES = [0, 1, 2, 4, 8]

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attr_value", random.choice, POSSIBLE_VALUES)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_value, 20)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def applyHeuristic(individual, state, move):
    score = 0
    if state.is_corner(move):
        score += individual[0]
    else:
        score += individual[1]

    if state.is_corner_after(move):
        score += individual[2]
    else:
        score += individual[3]

    if state.is_edge_and_not_corner(move):
        score += individual[4]
    else:
        score += individual[5]

    if state.is_edge_and_not_corner_after(move):
        score += individual[6]
    else:
        score += individual[7]

    if state.move_is_towards_edge(move):
        score += individual[8]
    else:
        score += individual[9]

    if state.is_jumpable_before(move):
        score += individual[10]
    else:
        score += individual[11]

    if state.is_jumpable_after(move):
        score += individual[12]
    else:
        score += individual[13]

    if state.move_jump_differential(move):
        score += individual[14]
    else:
        score += individual[15]

    if state.removed_can_jump(move):
        score += individual[16]
    else:
        score += individual[17]

    if state.more_crowded_after(move):
        score += individual[18]
    else:
        score += individual[19]

    return score

def evalKonaneHeuristic(piece_range, individual):
    correct = 0
    wrong = 0
    for (state, moves) in parse_db_to_dict.move_dict.items():
        if state.num_pieces < piece_range[0] or state.num_pieces > piece_range[1]:
            continue
        best_score = float('-inf')
        best_moves = []
        for move in state.valid_moves:
            score = applyHeuristic(individual, state, move)

            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)

        for move in best_moves:
            if move in moves:
                correct += 1
            else:
                wrong += 1
    return (correct / (correct + wrong), )

def evalKonaneStageHeuristic(stages):
    correct = 0
    wrong = 0
    for (state, moves) in parse_db_to_dict.move_dict.items():
        for (piece_range, individual) in stages:
            if state.num_pieces < piece_range[0] or state.num_pieces > piece_range[1]:
                continue
            best_score = float('-inf')
            best_moves = []
            for move in state.valid_moves:
                score = applyHeuristic(individual, state, move)
                
                if score > best_score:
                    best_score = score
                    best_moves = [move]
                elif score == best_score:
                    best_moves.append(move)

            for move in best_moves:
                if move in moves:
                    correct += 1
                else:
                    wrong += 1
    return correct / (correct + wrong)

toolbox.register("mate", tools.cxTwoPoint)

def mutNewValue(individual, indpb):
    for i in range(len(individual)):
        if random.random() < indpb:
            individual[i] = random.choice(POSSIBLE_VALUES)
    return individual,

toolbox.register("mutate", mutNewValue, indpb=0.10)
toolbox.register("select", tools.selTournament, tournsize=7)

def evolveHeuristics(ngen=40, n=1000, pop=None):
    if pop is None:
        pop = toolbox.population(n)
    hof = tools.HallOfFame(10)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("med", numpy.median)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    cxpb = 0.5
    mutpb = 0.2
    pop, logbook = algorithms.eaSimple(pop, toolbox, cxpb, mutpb, ngen, stats, halloffame=hof)

    return pop, hof, stats, logbook

if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=4)
    toolbox.register("map", pool.map)

    mode = "3stage"

    if mode == "all":
        piece_ranges = [[0, 100]]
    elif mode == "end":
        piece_ranges = [[0, 20]]
    elif mode == "mid":
        piece_ranges = [[21, 60]]
    elif mode == "beg":
        piece_ranges = [[61, 100]]
    elif mode == "3stage":
        piece_ranges = [[0, 20], [21, 60], [61, 100]]
    ngen = 40
    n = 5000
    
    import time
    timestr = time.strftime('%Y-%m-%d-%H-%M')
    filename = 'results/{0}_{1}_{2}_{3}.txt'.format(mode, n, ngen, timestr)
    f = open(filename, 'w')

    strats = []

    pop = None
    for piece_range in piece_ranges:
        f.write('Range: {}, Pop: {}, Ngen: {}\n'.format(str(piece_range), n, ngen))
        toolbox.register("evaluate", evalKonaneHeuristic, piece_range)
        
        pop, hof, stats, logbook = evolveHeuristics(ngen, n, pop)

        f.write(str(logbook))

        f.write('\n\nHall of Fame\n')
        f.write('------------\n')
        for ind in hof:
            f.write(str(ind))
            f.write('\n')
        f.write('\n')
        strats += [(piece_range, hof[0])]
        toolbox.unregister("evaluate")
        for ind in pop:
            del ind.fitness.values

    if mode == "3stage":
        f.write("Three stage strategy fitness: {}\n".format(str(evalKonaneStageHeuristic(strats))))
    f.close()
