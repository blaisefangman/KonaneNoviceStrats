import re

MVR_GROUP = 1
PRV_GROUP = 2
EMP_GROUP = 3
WHO_GROUP = 4

MVR_IDX = MVR_GROUP - 1
PRV_IDX = PRV_GROUP - 1
EMP_IDX = EMP_GROUP - 1
WHO_IDX = WHO_GROUP - 1

class KonaneState:
    def __init__(self, state, mover=None, num_pieces=None):
        if mover is None:
            self.board, self.num_pieces = self._make_konane_board(state)
            self.mover = self._extract_mover(state)
            self.can_pass = self._extract_can_pass(state)
            self.valid_moves = self._valid_moves()
            self.opp_valid_moves = self._valid_moves((self.mover % 2) + 1)
        else:
            self.board = state
            self.num_pieces = num_pieces
            self.mover = mover
            self.can_pass = False
            self.valid_moves = self._valid_moves()
            self.opp_valid_moves = self._valid_moves((self.mover % 2) + 1)

        self.is_corner_cache = {}
        self.is_corner_after_cache = {}
        self.is_edge_cache = {}
        self.is_edge_after_cache = {}
        self.is_towards_edge_cache = {}
        self.is_jumpable_before_cache = {}
        self.is_jumpable_after_cache = {}
        self.jump_diff_cache = {}
        self.removed_can_jump_cache = {}
        self.crowded_after_cache = {}

    def __str__(self):
        rev = reversed(self.board)
        board_str = ""
        for row in rev:
            board_str += str(row) + "\n"
        return board_str

    def print(self):
        print(self)

    def _valid_moves(self, mover=None):
        if mover is None:
            mover = self.mover
        moves = []
        for row in range(10):
            for col in range(10):
                if self.board[row][col] == mover:
                    if row >= 2:
                        if self.board[row-1][col] > 0 and self.board[row-2][col] == 0:
                            moves += [((row, col), (row-2, col))]

                    if row <= 7:
                        if self.board[row+1][col] > 0 and self.board[row+2][col] == 0:
                            moves += [((row, col), (row+2, col))]

                    if col >= 2:
                        if self.board[row][col-1] > 0 and self.board[row][col-2] == 0:
                            moves += [((row, col), (row, col-2))]

                    if col <= 7:
                        if self.board[row][col+1] > 0 and self.board[row][col+2] == 0:
                            moves += [((row, col), (row, col+2))]

        return moves

    def _make_konane_board(self, state):
        board = [[0 for i in range(10)] for j in range(10)]
        owner_str = r'chunk (\d+) = (\d+)'
        owner_re = re.compile(owner_str)
        cells = re.findall(owner_re, state[WHO_IDX])
        num_pieces = 0
        for cell in cells:
            board[int(cell[0]) // 10][int(cell[0]) % 10] = int(cell[1])
            if int(cell[1]) > 0:
                num_pieces += 1

        board = tuple((tuple(row) for row in board))
        return board, num_pieces

    def _extract_mover(self, state):
        return int(state[MVR_IDX])

    def _extract_can_pass(self, state):
        return int(state[MVR_IDX]) == int(state[PRV_IDX])

    def do_jump(self, move):
        remove_row = int((move[0][0] + move[1][0]) / 2)
        remove_col = int((move[0][1] + move[1][1]) / 2)
        start_row, start_col = move[0]
        end_row, end_col = move[1]
        board = [[self.board[row][col] for col in range(10)] for row in range(10)]
        board[start_row][start_col] = 0
        board[end_row][end_col] = self.mover
        board[remove_row][remove_col] = 0
        board = tuple((tuple(row) for row in board))
        if self.mover == 1:
            mover = 2
        else:
            mover = 1
        return KonaneState(board, mover=mover, num_pieces=self.num_pieces-1)

    def is_corner(self, move):
        try:
            return self.is_corner_cache[move]
        except KeyError:
            start = move[0]
            self.is_corner_cache[move] = (start[0] == 0 and (start[1] == 0 or start[1] == 9)) or (start[0] == 9 and (start[1] == 0 or start[1] == 9))
            return self.is_corner_cache[move]

    def is_corner_after(self, move):
        try:
            return self.is_corner_after_cache[move]
        except KeyError:
            end = move[1]
            self.is_corner_after_cache[move] = (end[0] == 0 and (end[1] == 0 or end[1] == 9)) or (end[0] == 9 and (end[1] == 0 or end[1] == 9))
            return self.is_corner_after_cache[move]

    def is_edge_and_not_corner(self, move):
        try:
            return self.is_edge_cache[move]
        except KeyError:
            start = move[0]
            if self.is_corner(move):
                self.is_edge_cache[move] = False
            else: 
                self.is_edge_cache[move] = start[0] == 0 or start[0] == 9 or start[1] == 0 or start[1] == 9
            return self.is_edge_cache[move]

    def is_edge_and_not_corner_after(self, move):
        try:
            return self.is_edge_after_cache[move]
        except KeyError:
            end = move[1]
            if self.is_corner_after(move):
                self.is_edge_after_cache[move] = False
            else: 
                self.is_edge_after_cache[move] = end[0] == 0 or end[0] == 9 or end[1] == 0 or end[1] == 9
            return self.is_edge_after_cache[move]

    def move_is_towards_edge(self, move):
        try:
            return self.is_towards_edge_cache[move]
        except KeyError:
            start = move[0]
            lowest_edge = min(start)
            highest_edge = max(start)
            if lowest_edge <= (9 - highest_edge):
                closest_edge = lowest_edge
            else:
                closest_edge = 9 - highest_edge

            end = move[1]
            lowest_edge = min(end)
            highest_edge = max(end)
            if lowest_edge <= (9 - highest_edge):
                self.is_towards_edge_cache[move] = lowest_edge < closest_edge
            else:
                self.is_towards_edge_cache[move] = (9 - highest_edge) < closest_edge
            return self.is_towards_edge_cache[move]

    def is_jumpable(self, piece):
        row, col = piece
        if row > 0 and row < 9:
            if self.board[row+1][col] > 0 and self.board[row-1][col] == 0:
                return True
            if self.board[row-1][col] > 0 and self.board[row+1][col] == 0:
                return True
        if col > 0 and col < 9:
            if self.board[row][col+1] > 0 and self.board[row][col-1] == 0:
                return True
            if self.board[row][col-1] > 0 and self.board[row][col+1] == 0:
                return True
        return False

    def is_jumpable_before(self, move):
        try:
            return self.is_jumpable_before_cache[move]
        except KeyError:
            self.is_jumpable_before_cache[move] = self.is_jumpable(move[0])
            return self.is_jumpable_before_cache[move]

    def is_jumpable_after(self, move):
        try:
            return self.is_jumpable_after_cache[move]
        except KeyError:
            state = self.do_jump(move)
            self.is_jumpable_after_cache[move] = state.is_jumpable(move[1])
            return self.is_jumpable_after_cache[move]

    def jump_differential(self):
        mvr_jumps = len(self.valid_moves)
        opp_jumps = len(self.opp_valid_moves)
        return mvr_jumps - opp_jumps

    def move_jump_differential(self, move):
        try:
            return self.jump_diff_cache[move]
        except KeyError:
            curr_diff = self.jump_differential()
            next_diff = -self.do_jump(move).jump_differential()
            self.jump_diff_cache[move] = next_diff >= curr_diff
            return self.jump_diff_cache[move]

    def removed_can_jump(self, move):
        try:
            return self.removed_can_jump_cache[move]
        except KeyError:
            row = int((move[0][0] + move[1][0]) / 2)
            col = int((move[0][1] + move[1][1]) / 2)
            if row >= 2:
                if self.board[row-1][col] > 0 and self.board[row-2][col] == 0:
                    self.removed_can_jump_cache[move] = True
                    return True

            if row <= 7:
                if self.board[row+1][col] > 0 and self.board[row+2][col] == 0:
                    self.removed_can_jump_cache[move] = True
                    return True

            if col >= 2:
                if self.board[row][col-1] > 0 and self.board[row][col-2] == 0:
                    self.removed_can_jump_cache[move] = True
                    return True

            if col <= 7:
                if self.board[row][col+1] > 0 and self.board[row][col+2] == 0:
                    self.removed_can_jump_cache[move] = True
                    return True
            self.removed_can_jump_cache[move] = False
            return False

    def more_crowded_after(self, move):
        try:
            return self.crowded_after_cache[move]
        except KeyError:
            row = move[0][0]
            col = move[0][1]
            before = 0
            if row > 0:
                if col > 0:
                    if self.board[row-1][col-1] > 0:
                        before += 1
                if col < 9:
                    if self.board[row-1][col+1] > 0:
                        before += 1
                if self.board[row-1][col] > 0:
                    before += 1
            if row < 9:
                if col > 0:
                    if self.board[row+1][col-1] > 0:
                        before += 1
                if col < 9:
                    if self.board[row+1][col+1] > 0:
                        before += 1
                if self.board[row+1][col] > 0:
                    before += 1
            if col > 0 and self.board[row][col-1] > 0:
                before += 1
            if col < 9 and self.board[row][col+1] > 0:
                before += 1

            row = move[1][0]
            col = move[1][1]
            # -1 to ignore the jumped piece
            after = -1
            if row > 0:
                if col > 0:
                    if self.board[row-1][col-1] > 0:
                        after += 1
                if col < 9:
                    if self.board[row-1][col+1] > 0:
                        after += 1
                if self.board[row-1][col] > 0:
                    after += 1
            if row < 9:
                if col > 0:
                    if self.board[row+1][col-1] > 0:
                        after += 1
                if col < 9:
                    if self.board[row+1][col+1] > 0:
                        after += 1
                if self.board[row+1][col] > 0:
                    after += 1
            if col > 0 and self.board[row][col-1] > 0:
                after += 1
            if col < 9 and self.board[row][col+1] > 0:
                after += 1

            self.crowded_after_cache[move] = after > before
            return self.crowded_after_cache[move]
