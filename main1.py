import copy as cp
import time
from queue import PriorityQueue, Queue

# from random import seed
# from random import randint

test = 0
# seed(1)


class State:
    def __init__(self, box_pos, player_pos, ancestor, gval = -1, fval = -1):
        self.box_pos = box_pos
        self.player_pos = player_pos
        self.ancestor = ancestor
        self.gval = gval
        self.fval = fval

    #use __eq__ method to compare instance of classes
    def __eq__(self, state):
        return self.player_pos == state.player_pos and self.box_pos == state.box_pos

    #used to become hasable object -> object can be contained in set data structure
    #frozenset is an immutable set -> element can not be added or removed
    def __hash__(self):
        return hash((self.player_pos, frozenset(self.box_pos)))

    #use for priority queue
    def __lt__(self, state):
        if (self.fval == state.fval):
            return self.gval < state.gval

        return self.fval < state.fval

    def is_final_state(self, goal_pos):
        return self.box_pos == goal_pos

    def deep_copy_box_pos(self):
        return self.box_pos.copy()


class DeadlockSolver:
    @staticmethod
    def check_simple_deadlock(matrix, num_row, num_col, goal_pos):
        matrix_flag = [[False] * num_col for i in range(num_row)]
        for goal in goal_pos:
            q = Queue()
            q.put(goal)
            matrix_flag[goal[0]][goal[1]] = True
            while not q.empty():
                (x, y) = q.get()
                # if matrix[x + 1][y] != '#' and matrix[x - 1][y] != '#':
                #     if (not matrix_flag[x + 1][y] and matrix[x + 2][y] != '#'):
                #         q.put((x + 1, y))
                #         matrix_flag[x + 1][y] = True
                #     if (not matrix_flag[x - 1][y] and matrix[x - 2][y] != '#'):
                #         q.put((x - 1, y))
                #         matrix_flag[x - 1][y] = True
                # if matrix[x][y + 1] != '#' and matrix[x][y - 1] != '#':
                #     if (not matrix_flag[x][y + 1] and matrix[x][y + 2] != '#'):
                #         q.put((x, y + 1))
                #         matrix_flag[x][y + 1] = True
                #     if (not matrix_flag[x][y - 1] and matrix[x][y - 2] != '#'):
                #         q.put((x, y - 1))
                #         matrix_flag[x][y - 1] = True

                #pull up
                if matrix[x - 1][y] != '#' and matrix[x - 2][y] != '#':
                    if (not matrix_flag[x - 1][y]):
                        q.put((x - 1, y))
                        matrix_flag[x - 1][y] = True

                #pull down
                if matrix[x + 1][y] != '#' and matrix[x + 2][y] != '#':
                    if (not matrix_flag[x + 1][y]):
                        q.put((x + 1, y))
                        matrix_flag[x + 1][y] = True

                #pull left
                if matrix[x][y - 1] != '#' and matrix[x][y - 2] != '#':
                    if (not matrix_flag[x][y - 1]):
                        q.put((x, y - 1))
                        matrix_flag[x][y - 1] = True

                #pull right
                if matrix[x][y + 1] != '#' and matrix[x][y + 2] != '#':
                    if (not matrix_flag[x][y + 1]):
                        q.put((x, y + 1))
                        matrix_flag[x][y + 1] = True
        return matrix_flag


    @staticmethod
    def has_freeze_deadlock(pos, matrix, box_pos, goal_pos, no_simple_deadlock, checked_list):
        # print(pos)
        (x, y) = pos
        checked_list.add((x, y))
        x_axis_freeze = False
        if (matrix[x + 1][y] == '#' or matrix[x - 1][y] == '#'):
            x_axis_freeze = True
        elif not no_simple_deadlock[x + 1][y] and not no_simple_deadlock[x - 1][y]:
            x_axis_freeze = True
        elif (x + 1, y) in box_pos and ((x + 1, y) in checked_list or DeadlockSolver.has_freeze_deadlock((x + 1, y), matrix, box_pos, goal_pos, no_simple_deadlock, checked_list)):
            x_axis_freeze = True
        elif (x - 1, y) in box_pos and ((x - 1, y) in checked_list or DeadlockSolver.has_freeze_deadlock((x - 1, y), matrix, box_pos, goal_pos, no_simple_deadlock, checked_list)):
            x_axis_freeze = True
        else:
            return False

        y_axis_freeze = False
        if (matrix[x][y + 1] == '#' or matrix[x][y - 1] == '#'):
            y_axis_freeze = True
        elif not no_simple_deadlock[x][y + 1] and not no_simple_deadlock[x][y - 1]:
            y_axis_freeze = True
        elif (x, y + 1) in box_pos and ((x, y + 1) in checked_list or DeadlockSolver.has_freeze_deadlock((x, y + 1), matrix, box_pos, goal_pos, no_simple_deadlock, checked_list)):
            y_axis_freeze = True
        elif (x, y - 1) in box_pos and ((x, y - 1) in checked_list or DeadlockSolver.has_freeze_deadlock((x, y - 1), matrix, box_pos, goal_pos, no_simple_deadlock, checked_list)):
            y_axis_freeze = True
        else:
            return False

        
        
        # if (t):
        #     print(pos)
        #     print(box_pos)
        # return t

        last_check = False
        for box in checked_list:
            if (box not in goal_pos):
                last_check = True

        return x_axis_freeze and y_axis_freeze and last_check

class Search:
    def __init__(self, num_row, num_col, matrix, box_pos, goal_pos, player_pos, is_astar = False):
        self.num_row = num_row
        self.num_col = num_col
        self.matrix = matrix
        if (is_astar):
            self.initial_state = State(box_pos, player_pos, None, 0, 0)    
        else:
            self.initial_state = State(box_pos, player_pos, None)
        self.goal_pos = goal_pos

        self.no_simple_deadlock = DeadlockSolver.check_simple_deadlock(self.matrix, self.num_row, self.num_col, self.goal_pos)


    def can_go_up(self, current_state):
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        if (x <= 1):
            return False
        t1 = self.matrix[x - 1][y]
        t2 = self.matrix[x - 2][y]
        box_pos = current_state.box_pos.copy()
        if ((x - 1, y) in box_pos):
            new_box = box_pos.copy()
            new_box.remove((x - 1, y))
            new_box.add((x - 2, y))
        
        #continue execute if (x - 1, y) not a wall. 
        #if (x - 1, y) have a box, then (x - 2, y) must be free

        # return t1 != '#' and ((x - 1, y) not in box_pos or (t2 != '#' and (x - 2, y) not in box_pos and self.no_simple_deadlock[x - 2][y]))

        return t1 != '#' and ((x - 1, y) not in box_pos or (t2 != '#' and (x - 2, y) not in box_pos and self.no_simple_deadlock[x - 2][y] and (not DeadlockSolver.has_freeze_deadlock((x - 2, y), self.matrix, new_box, self.goal_pos, self.no_simple_deadlock, set()))))    #f_heuristic is a heuristic function used by A star algorigthm
    def go_up(self, current_state, f_heuristic = None):
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        new_box_pos = current_state.deep_copy_box_pos()
        if ((x - 1, y) in current_state.box_pos):
            new_box_pos.remove((x - 1, y))
            new_box_pos.add((x - 2, y))
        if (f_heuristic):
            new_gval = current_state.gval + 1
            new_fval = new_gval + f_heuristic(new_box_pos, self.goal_pos)
            return State(new_box_pos, (x - 1, y), current_state, new_gval, new_fval) 
        return State(new_box_pos, (x - 1, y), current_state)

    def can_go_down(self, current_state):
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        if (x >= self.num_row - 2):
            return False
        t1 = self.matrix[x + 1][y]
        t2 = self.matrix[x + 2][y]
        # box_pos = current_state.box_pos

        box_pos = current_state.box_pos.copy()
        if ((x + 1, y) in box_pos):
            new_box = box_pos.copy()
            new_box.remove((x + 1, y))
            new_box.add((x + 2, y))
        
        #continue execute if (x + 1, y) not a wall. 
        #if (x + 1, y) have a box, then (x + 2, y) must be free
        # return t1 != '#' and ((x + 1, y) not in box_pos or (t2 != '#' and (x + 2, y) not in box_pos and self.no_simple_deadlock[x + 2][y]))
        # return t1 != '#' and ((x + 1, y) not in box_pos or (t2 != '#' and (x + 2, y) not in box_pos and self.no_simple_deadlock[x + 2][y]))
        return t1 != '#' and ((x + 1, y) not in box_pos or (t2 != '#' and (x + 2, y) not in box_pos and self.no_simple_deadlock[x + 2][y] and (not DeadlockSolver.has_freeze_deadlock((x + 2, y), self.matrix, new_box, self.goal_pos, self.no_simple_deadlock, set()))))

    def go_down(self, current_state, f_heuristic = None):
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        new_box_pos = current_state.deep_copy_box_pos()
        if ((x + 1, y) in current_state.box_pos):
            new_box_pos.remove((x + 1, y))
            new_box_pos.add((x + 2, y))
        if (f_heuristic):
            new_gval = current_state.gval + 1
            new_fval = new_gval + f_heuristic(new_box_pos, self.goal_pos)
            return State(new_box_pos, (x + 1, y), current_state, new_gval, new_fval) 
        return State(new_box_pos, (x + 1, y), current_state)

    def can_go_left(self, current_state):
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        if (y <= 1):
            return False
        t1 = self.matrix[x][y - 1]
        t2 = self.matrix[x][y - 2]
        box_pos = current_state.box_pos.copy()
        if ((x, y - 1) in box_pos):
            new_box = box_pos.copy()
            new_box.remove((x, y - 1))
            new_box.add((x, y - 2))
        
        #continue execute if (x, y - 1) not a wall. 
        #if (x, y - 1) have a box, then (x, y - 2) must be free
        # return t1 != '#' and ((x, y - 1) not in box_pos or (t2 != '#' and (x, y - 2) not in box_pos and self.no_simple_deadlock[x][y - 2]))

        # return t1 != '#' and ((x, y - 1) not in box_pos or (t2 != '#' and (x, y - 2) not in box_pos and self.no_simple_deadlock[x][y - 2]))
        return t1 != '#' and ((x, y - 1) not in box_pos or (t2 != '#' and (x, y - 2) not in box_pos and self.no_simple_deadlock[x][y - 2] and (not DeadlockSolver.has_freeze_deadlock((x, y - 2), self.matrix, new_box, self.goal_pos, self.no_simple_deadlock, set()))))

    def go_left(self, current_state, f_heuristic = None):
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        new_box_pos = current_state.deep_copy_box_pos()
        if ((x, y - 1) in current_state.box_pos):
            new_box_pos.remove((x, y - 1))
            new_box_pos.add((x, y - 2))
        if (f_heuristic):
            new_gval = current_state.gval + 1
            new_fval = new_gval + f_heuristic(new_box_pos, self.goal_pos)
            return State(new_box_pos, (x, y - 1), current_state, new_gval, new_fval) 
        return State(new_box_pos, (x, y - 1), current_state)

    def can_go_right(self, current_state):
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        if (y >= self.num_col - 2): 
            return False
        t1 = self.matrix[x][y + 1]
        t2 = self.matrix[x][y + 2]
        box_pos = current_state.box_pos
        box_pos = current_state.box_pos.copy()
        if ((x, y + 1) in box_pos):
            new_box = box_pos.copy()
            new_box.remove((x, y + 1))
            new_box.add((x, y + 2))
        
        #continue execute if (x, y + 1) not a wall. 
        #if (x, y + 1) have a box, then (x, y + 2) must be free
        # return t1 != '#' and ((x, y + 1) not in box_pos or (t2 != '#' and (x, y + 2) not in box_pos and self.no_simple_deadlock[x][y + 2]))

        # return t1 != '#' and ((x, y + 1) not in box_pos or (t2 != '#' and (x, y + 2) not in box_pos and self.no_simple_deadlock[x][y + 2]))
        return t1 != '#' and ((x, y + 1) not in box_pos or (t2 != '#' and (x, y + 2) not in box_pos and self.no_simple_deadlock[x][y + 2] and (not DeadlockSolver.has_freeze_deadlock((x, y + 2), self.matrix, new_box, self.goal_pos, self.no_simple_deadlock, set()))))
    def go_right(self, current_state, f_heuristic = None):
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        new_box_pos = current_state.deep_copy_box_pos()
        if ((x, y + 1) in current_state.box_pos):
            new_box_pos.remove((x, y + 1))
            new_box_pos.add((x, y + 2))
        if (f_heuristic):
            new_gval = current_state.gval + 1
            new_fval = new_gval + f_heuristic(new_box_pos, self.goal_pos)
            return State(new_box_pos, (x, y + 1), current_state, new_gval, new_fval) 
        return State(new_box_pos, (x, y + 1), current_state)



    def expand(self, state, closed_set, queue, f_heuristic = None, lookup_table = None):
        #successors_list = list()

        if (self.can_go_up(state)):
            new_state = self.go_up(state, f_heuristic)
            if (new_state not in closed_set):
                closed_set.add(new_state)
                queue.put(new_state)
                lookup_table[hash(new_state)] = new_state
                # print("U")
            else:
                id = hash(new_state)
                if (new_state.fval < lookup_table[id].fval):
                    lookup_table[id].fval = new_state.fval
                    lookup_table[id].gval = new_state.gval
                    lookup_table[id].ancestor = new_state.ancestor

        if (self.can_go_right(state)):
            new_state = self.go_right(state, f_heuristic)
            if (new_state not in closed_set):
                closed_set.add(new_state)
                queue.put(new_state)
                lookup_table[hash(new_state)] = new_state
                # print("U")
            else:
                id = hash(new_state)
                if (new_state.fval < lookup_table[id].fval):
                    lookup_table[id].fval = new_state.fval
                    lookup_table[id].gval = new_state.gval
                    lookup_table[id].ancestor = new_state.ancestor



        if (self.can_go_left(state)):
            new_state = self.go_left(state, f_heuristic)
            if (new_state not in closed_set):
                closed_set.add(new_state)
                queue.put(new_state)
                lookup_table[hash(new_state)] = new_state
                # print("U")
            else:
                id = hash(new_state)
                if (new_state.fval < lookup_table[id].fval):
                    lookup_table[id].fval = new_state.fval
                    lookup_table[id].gval = new_state.gval
                    lookup_table[id].ancestor = new_state.ancestor

        if (self.can_go_down(state)):
            new_state = self.go_down(state, f_heuristic)
            if (new_state not in closed_set):
                closed_set.add(new_state)
                queue.put(new_state)
                lookup_table[hash(new_state)] = new_state
                # print("U")
            else:
                id = hash(new_state)
                if (new_state.fval < lookup_table[id].fval):
                    lookup_table[id].fval = new_state.fval
                    lookup_table[id].gval = new_state.gval
                    lookup_table[id].ancestor = new_state.ancestor


    def construct_path(self, state):
        path = list()
        while (state.ancestor):
            x1 = state.ancestor.player_pos[0]
            y1 = state.ancestor.player_pos[1]
            x2 = state.player_pos[0]
            y2 = state.player_pos[1]
            if (x2 > x1):
                path.insert(0, 'D')
            elif (x2 < x1):
                path.insert(0, 'U')
            elif (y2 > y1):
                path.insert(0, 'R')
            else:
                path.insert(0, 'L')
            state = state.ancestor
        return path
            

class BFS(Search):
    def __init__(self, num_row, num_col, matrix, box_pos, goal_pos, player_pos):
        super().__init__(num_row, num_col, matrix, box_pos, goal_pos, player_pos)

    def search(self):
        start_time = time.time()
        frontier = Queue()
        frontier.put(self.initial_state)
        closed_set = set()
        closed_set.add(self.initial_state)

        a = 0

        while (not frontier.empty()):
            a += 1
            current_state = frontier.get()
            if (current_state.is_final_state(self.goal_pos)):
                
                print(a)
                print("--- %s seconds ---" % (time.time() - start_time))
                return self.construct_path(current_state)
            self.expand(current_state, closed_set, frontier)
            #frontier.extend(self.expand(current_state, closed_set))
        print("--- %s seconds ---" % (time.time() - start_time))

        print(self.no_simple_deadlock)

        return ["Impossible"]


class AStar(Search):
    def __init__(self, num_row, num_col, matrix, box_pos, goal_pos, player_pos):
        super().__init__(num_row, num_col, matrix, box_pos, goal_pos, player_pos, True)
        

    def f_heuristic(self, box_pos, goal_pos):
        # sum = 0
        # for box in box_pos:
        #     sum = sum + min([abs(box[0] - goal[0]) + abs(box[1] - goal[1]) for goal in goal_pos])
        # return sum
        
        # return test + 1 + randint(0, 10000)

        dist_sum = 0
        for box in box_pos:       # Find nearest storage point to box that is not in restrictions list
            min_distace = 2**31
            for storage in goal_pos:
                new_dist = (abs(box[0] - storage[0]) + abs(box[1] - storage[1])) # Calculate manhattan distance between box and storage point
                if new_dist < min_distace:
                    min_distace = new_dist
            dist_sum += min_distace
        return dist_sum

    def search(self):
        start_time = time.time()
        frontier = PriorityQueue()
        frontier.put(self.initial_state)
        closed_set = set()
        closed_set.add(self.initial_state)
        lookup_table = dict()
        lookup_table[hash(self.initial_state)] = self.initial_state
        a = 0

        while (not frontier.empty()):

            a += 1
            
            current_state = frontier.get()

            if (current_state.is_final_state(self.goal_pos)):
                print(a)
                print("--- %s seconds ---" % (time.time() - start_time))
                return self.construct_path(current_state)
            self.expand(current_state, closed_set, frontier, self.f_heuristic, lookup_table)
            #frontier.extend(self.expand(current_state, closed_set))
        print("--- %s seconds ---" % (time.time() - start_time))
        return ["Impossible"]

if __name__ == "__main__":
    with open('input7.txt', 'r') as file:
        matrix = [list(line.rstrip()) for line in file]
    
    box_pos, goal_pos, player_pos = set(), set(), ()
    for i in range(len(matrix)):
        for j in range(len(matrix[i]) - 1): #omit endline
            if matrix[i][j] == '.':
                goal_pos.add((i, j))
            elif matrix[i][j] == '*':
                box_pos.add((i, j))
                goal_pos.add((i, j))
            elif matrix[i][j] == '$':
                box_pos.add((i, j))
            elif matrix[i][j] == '@':
                player_pos = (i, j)
            elif matrix[i][j] == '+':
                player_pos = (i, j)
                goal_pos.add((i, j))
    num_row, num_col = len(matrix), max([len(row) for row in matrix]) #number of row and column of matrix 

    #add extra " " character to some lines of matrix
    for row in matrix:
        for i in range(num_col):
            if (i > len(row) - 1):
                row.append(' ')
    ob = AStar(num_row, num_col, matrix, box_pos, goal_pos, player_pos)
    print(ob.search())

    # print(box_pos)
    # no_simple_deadlock = DeadlockSolver.check_simple_deadlock(matrix, num_row, num_col, goal_pos)
    # print(DeadlockSolver.has_freeze_deadlock((3, 5), matrix, box_pos, goal_pos, no_simple_deadlock, set()))
    # ob1 = State({(3, 4), (5, 6), (7, 9), (9, 7), (2, 3), (10, 11)}, (1, 2), None)
    # ob2 = State({(3, 4), (10, 11), (5, 6), (2, 3), (9, 7), (7, 9)}, (1, 2), None)
    # print(hash(ob1) == hash(ob2))
    # c = {-1: 'a'}
    # print(c[-1])
    # c[-2] = 'd'
    # print(hash(ob1) == hash(ob2))