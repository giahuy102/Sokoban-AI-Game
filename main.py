class State:
    def __init__(self, box_pos, player_pos):
        self.box_pos = box_pos
        self.player_pos = player_pos

    #use __eq__ method to compare instance of classes
    def __eq__(self, state):
        return self.player_pos == state.player_pos and self.box_pos == state.box_pos

    def is_final_state(self, goal_pos):
        return self.box_pos == goal_pos

    def deep_copy_box_pos(self):
        return self.box_pos.copy()


class Search:
    def __init__(self, num_row, num_col, matrix, box_pos, goal_pos, player_pos):
        self.num_row = num_row
        self.num_col = num_col
        self.matrix = matrix
        self.initial_state = State(box_pos, player_pos)
        self.goal_pos = goal_pos

    #change matrix when going from (x1, y1) to (x2, y2)
    #is_player check if move player or box to new position => for suitable symbol
    def move(self, x1, y1, x2, y2, is_player):
        if (is_player):
            if (self.matrix[x2][y2] == ' '):
                self.matrix[x2][y2] = '@'
            else:
                self.matrix[x2][y2] = '+'
            if (self.matrix[x1][y1] == '@'):
                self.matrix[x1][y1] = ' '
            else: 
                self.matrix[x1][y1] = '.'
        else:
            if (self.matrix[x2][y2] == ' '):
                self.matrix[x2][y2] = '$'
            else:
                self.matrix[x2][y2] = '*'
            if (self.matrix[x1][y1] == '$'):
                self.matrix[x1][y1] = ' '
            else: 
                self.matrix[x1][y1] = '.'


    def can_go_up(self, current_state):
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        if (x <= 1):
            return False
        t1 = self.matrix[x - 1][y]
        t2 = self.matrix[x - 2][y]
        t3 = t1 == ' ' or t1 == '.'
        t4 = t2 == ' ' or t2 == '.'
        return  t3 or ((t1 == '*' or t1 == '$') and t4)

    def go_up(self, current_state):
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        new_box_pos = current_state.deep_copy_box_pos()
        if (self.matrix[x - 1][y] == '$' or self.matrix[x - 1][y] == '*'):
            self.move(x - 1, y, x - 2, y, False) #move box
            new_box_pos.remove((x - 1, y))
            new_box_pos.add((x - 2, y))
        self.move(x, y, x - 1, y, True) #move player
        return State(new_box_pos, [x - 1, y])

    def can_go_down(self, current_state):
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        if (x >= self.num_row - 2):
            return False
        t1 = self.matrix[x + 1][y]
        t2 = self.matrix[x + 2][y]
        t3 = t1 == ' ' or t1 == '.'
        t4 = t2 == ' ' or t2 == '.'
        return  t3 or ((t1 == '*' or t1 == '$') and t4)

    def go_down(self, current_state):
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        new_box_pos = current_state.deep_copy_box_pos()
        if (self.matrix[x + 1][y] == '$' or self.matrix[x + 1][y] == '*'):
            self.move(x + 1, y, x + 2, y, False) #move box
            new_box_pos.remove((x + 1, y))
            new_box_pos.add((x + 2, y))
        self.move(x, y, x + 1, y, True) #move player
        return State(new_box_pos, [x + 1, y])

    def can_go_left(self, current_state):
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        if (y <= 1):
            return False
        t1 = self.matrix[x][y - 1]
        t2 = self.matrix[x][y - 2]
        t3 = t1 == ' ' or t1 == '.'
        t4 = t2 == ' ' or t2 == '.'
        return  t3 or ((t1 == '*' or t1 == '$') and t4)

    def go_left(self, current_state):
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        new_box_pos = current_state.deep_copy_box_pos()
        if (self.matrix[x][y - 1] == '$' or self.matrix[x][y - 1] == '*'):
            self.move(x, y - 1, x, y - 2, False) #move box
            new_box_pos.remove((x, y - 1))
            new_box_pos.add((x, y - 2))
        self.move(x, y, x, y - 1, True) #move player
        return State(new_box_pos, [x, y - 1])

    def can_go_right(self, current_state):
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        if (y >= self.num_col - 2):
            return False
        t1 = self.matrix[x][y + 1]
        t2 = self.matrix[x][y + 2]
        t3 = t1 == ' ' or t1 == '.'
        t4 = t2 == ' ' or t2 == '.'
        return  t3 or ((t1 == '*' or t1 == '$') and t4)

    def go_right(self, current_state):
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        new_box_pos = current_state.deep_copy_box_pos()
        if (self.matrix[x][y + 1] == '$' or self.matrix[x][y + 1] == '*'):
            self.move(x, y + 1, x, y + 2, False) #move box
            new_box_pos.remove((x, y + 1))
            new_box_pos.add((x, y + 2))
        self.move(x, y, x, y + 1, True) #move player
        return State(new_box_pos, [x, y - 1])

    def expand(state):
        successors_list = list()



class DFS(Search):
    def __init__(self, num_row, num_col, matrix, box_pos, goal_pos, player_pos):
        super().__init__(num_row, num_col, matrix, box_pos, goal_pos, player_pos)

    def search(self):
        closed_list = list()
        stack = list()
        stack.append(self.initial_state)
        while (stack):
            current_state = stack.pop()
            if (current_state.is_final_state(self.goal_pos)):
                return True
            if (current_state not in closed_list):
                closed_list.append(current_state)

        return False





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

