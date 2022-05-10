from deap_konane import evalKonaneHeuristic

genstrat = [2, -1, -4, 1, 4, -4, 4, 1, -1, 4, 1, 0, -1, 1, 2, -4, 8, -8, -8, 4]

print("End Accuracy: {}".format(evalKonaneHeuristic([0,20], genstrat)))
print("Mid Accuracy: {}".format(evalKonaneHeuristic([21,60], genstrat)))
print("Beg Accuracy: {}".format(evalKonaneHeuristic([61,100], genstrat)))
