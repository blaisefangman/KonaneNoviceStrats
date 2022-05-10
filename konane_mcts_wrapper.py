from konane_state import KonaneState

class MCTSKonaneState:
    def __init__(self, state):
        self.state = state

    def legal_moves(self):
        return self.state.valid_moves

    def result(self, move):
        return MCTSKonaneState(self.state.do_jump(move))

    def next_player(self):
        return self.state.mover

    def game_over(self):
        return len(self.state.valid_moves) == 0

    def winner(self):
        return (self.state.mover % 2) + 1

    def __hash__(self):
        return hash((self.state.board, self.state.mover))

    def __eq__(self, other):
        return type(self) is type(other) and self.state.board == other.state.board and self.state.mover == other.state.mover
