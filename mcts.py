import random
import math

class Game_Tree:
    def __init__(self, pos, parent, owner):
        self.pos = pos
        self.parent = parent
        self.owner = owner
        self.num_children = len(self.pos.legal_moves())
        self.children = []
        self.num_wins = 0
        self.num_losses = 0
        self.num_visits = 0

    def add_children(self, node_table):
        if len(self.children) < self.num_children:
            self.children = [Game_Tree(self.pos.result(move), self, self.owner) for move in self.pos.legal_moves()]
            for c in self.children:
                node_table.setdefault(c.pos, c)

    def choose_unvisited(self, node_table):
        current = self
        while not current.pos.game_over() and current.num_visits > 0:
            current.add_children(node_table)
            i = current.ucb()
            current = current.children[i]
        return current

    def playout(self, node_table):
        current = self.pos
        while not current.game_over():
            moves = current.legal_moves()
            move = random.choice(moves)
            current = current.result(move)
        return self, current.winner()

    def update_upwards(self, result, node_table):
        current = self
        while current != None:
            current.num_wins += result
            current.num_losses += 1 - result
            current.num_visits += 1

            if node_table[current.pos].num_visits < current.num_visits:
                node_table[current.pos] = current
            current = current.parent

    def ucb(self):
        ret = 0
        curr_max = -1
        options = []
        for i in range(len(self.children)):
            child = self.children[i]
            if child.num_visits == 0:
                options.append(i)
                continue

            if self.pos.next_player() == self.owner:
                explt_term = child.num_wins / child.num_visits
            else:
                explt_term = child.num_losses / child.num_visits

            explr_term = math.sqrt(2 * math.log(self.num_visits) / child.num_visits)
            result = explt_term + explr_term
            if result > curr_max:
                curr_max = result
                ret = i
        if len(options) == 0:
            return ret
        return random.choice(options)

class MCTS_Func:
    def __init__(self, num_iters):
        self.master_tree = None
        self.node_table = {}
        def fn(pos):
            if self.master_tree == None or self.node_table.get(pos) == None:
                self.master_tree = Game_Tree(pos, None, pos.next_player())
                self.node_table.clear()
                self.node_table[pos] = self.master_tree
                if self.master_tree.pos.game_over():
                    return None

            tree = self.node_table[pos]

            for i in range(num_iters):
                node = tree.choose_unvisited(self.node_table)
                result_node, result = node.playout(self.node_table)
                if tree.owner == 0 and result == 1:
                    result = 1
                elif tree.owner == 1 and result == -1:
                    result = 1
                elif result != 0:
                    result = 0
                else:
                    result = 0.5

                result_node.update_upwards(result, self.node_table)

            best_ew = -1
            moves = tree.pos.legal_moves()
            best_move = moves[0]
            for move in moves:
                r_move = tree.pos.result(move)
                resulting_node = self.node_table[r_move]
                if resulting_node.num_visits == 0:
                    continue
                ew = resulting_node.num_wins / resulting_node.num_visits
                if ew > best_ew:
                    best_ew = ew
                    best_move = move

            return best_move
        self.fn = fn

def mcts_strategy(num_iters):
    return MCTS_Func(num_iters).fn

"""
    def playout(self, node_table):
        current = self
        while not current.pos.game_over():
            res = current.pos.result(random.choice(current.pos.legal_moves()))
            current.children.append(Game_Tree(res, current, current.owner))
            current = current.children[0]
            node_table.setdefault(current.pos, current)
        current.add_children(node_table)
        return current, current.pos.winner()
"""

"""
    def playout(self, node_table):
        current = self
        while not current.pos.game_over():
            current.add_children(node_table)
            current = random.choice(current.children)
        current.add_children(node_table)
        return current
"""

"""
    def choose_unvisited(self):
        current = self
        while current.has_unvisited_children and current.num_visits > 0:
            unvisited_children = [c for c in current.children if c.has_unvisited_children]
            current = random.choice(unvisited_children)
        return current
"""

"""
def mcts_strategy(num_iters):
    master_tree = None
    node_table = {}
    def fn(pos):
        master_tree = mcts_strategy.master_tree
        node_table = mcts_strategy.node_table
        if master_tree == None or node_table[pos] == None:
            master_tree = Game_Tree(pos, None)
            node_table.clear()
            node_table[pos] = master_tree
            if master_tree.pos.game_over():
                return None
            master_tree.add_children(node_table)

        tree = node_table[pos]

        for i in range(num_iters):
            node = tree.choose_unvisited()
            if node.num_visits > 0:
                break;
            node.add_children(node_table)
            result_node = node.playout(node_table)
            result = result_node.pos.winner()
            if tree.pos.next_player() == 0 and result == 1:
                result = 1
            elif tree.pos.next_player() == 1 and result == -1:
                result = 1
            else:
                result = 0
            result_node.update_upwards(result)

        best_ew = -1
        moves = tree.pos.legal_moves()
        best_move = moves[0]
        for i in range(len(moves)):
            ew = tree.children[i].num_wins / tree.children[i].num_visits
            if ew > best_ew:
                best_ew = ew
                best_move = moves[i]

        return best_move

    return fn
"""
