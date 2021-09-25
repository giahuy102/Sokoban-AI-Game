class State:
    def __init__(self, box_pos, goal_pos, player_pos):
        self.box_pos = box_pos
        self.goal_pos = goal_pos
        self.player_pos = player_pos

    def is_equal_state(self, state):
        return self.player_pos == state.player_pos and self.box_pos == state.box_pos

    def is_final_state(self):
        return self.box_pos == self.goal_pos


class Search:
    def __init__(self, matrix, box_pos, goal_pos, player_pos):
        self.matrix = matrix
        self.state = State(box_pos, goal_pos, player_pos)

class DFS(Search):
    def __init__(self):
        super().__init__(matrix, box_pos, goal_pos, player_pos)
        stack = list()




if __name__ == "__main__":
    with open('input.txt', 'r') as file:
        matrix = [list(line) for line in file]
    num_row, num_col = len(matrix), len(matrix[0]) - 1 #number of row and column of matrix
    box_pos, goal_pos, player_pos = set(), set(), []
    for i in range(num_row):
        for j in range(num_col):
            if matrix[i][j] == '.':
                goal_pos.add((i, j))
            elif matrix[i][j] == '*':
                box_pos.add((i, j))
                goal_pos.add((i, j))
            elif matrix[i][j] == '$':
                box_pos.add((i, j))
            elif matrix[i][j] == '@':
                player_pos.extend(list((i, j)))
            elif matrix[i][j] == '+':
                player_pos.extend((i, j))
                goal_pos.add((i, j))
    print(box_pos)
    print(goal_pos)

