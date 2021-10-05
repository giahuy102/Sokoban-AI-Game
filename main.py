"""Sokoban routines
    A) Class State
    Define the structure of a state in state space. This class has some functions helping detemine a state 
    in search space.
    B) Class DeadlockSolver
    Has some utility function to determine whether a state creates a deadlock situation. "Deadlock" means
    the level isn't solvable anymore, no matter what the user does.
    C) Class Search
    Is an abstract class for types of searching. It also contains some utility function for making decisions
    on changing a state
    D) Class BFS:
    Contains some functions implementing BFS algorithm
    E) Class AStar:
    Contains some functions implementing AStar algorithm
"""

import time
from abc import ABC, abstractmethod
from queue import PriorityQueue, Queue

class State:
    def __init__(self, box_pos, player_pos, ancestor, gval = -1, fval = -1):
        """
        Create a new state of sokoban game
        @param box_pos: A set of tuples which displays the positions of boxes in a state 
        @param player_pos: A tuple which displays the position of player in a state
        @param ancestor: An object with State type which displays the state of ancestor (node) of current state (node)
        @param gval: an integer number that is the cost of getting to current state. It's used when we implement A* algorithm
        @param fval: a number (integer or real) that is the cost of getting from state to last state through current state.
        It's used when we implement A* algorithm
        """
        self.box_pos = box_pos
        self.player_pos = player_pos
        self.ancestor = ancestor
        self.gval = gval
        self.fval = fval

    def __eq__(self, state):
        """
        Used to compare the instances of the class with == operator
        @param: another state (object) that we want to compare with current state (object)
        @return: a boolean value shows whether states are equal 
        """
        return self.player_pos == state.player_pos and self.box_pos == state.box_pos

    def __hash__(self):
        """
        The hash method must be implemented for actions to be inserted into sets 
        and dictionaries (make a hashable object). It's also used for implementing index for lookup table of references to nodes.
        @return: The hash value of the action.
        """
        return hash((self.player_pos, frozenset(self.box_pos))) #use frozenset (immutable set) for creating hashable value

    def __lt__(self, state):    
        """
        For A* algorithm first we muse a priority queue data structure. This queue stores search nodes 
        waiting to be expanded. Thus we need to define a node1 < node2 function by defining 
        the __lt__ function. Dependent on the type of search this comparison function compares the h-value, 
        the g-value or the f-value of the nodes. Note for the f-value we wish to break ties by letting 
        node1 < node2 if they both have identical f-values but if node1 has a GREATER g value. 
        This means that we expand nodes along deeper paths first causing the search to proceed directly to the goal
        """
        if (self.fval == state.fval):
            return self.gval > state.gval
        return self.fval < state.fval

    def is_final_state(self, goal_pos):
        """
        Check if current state a goal state. The goal state has all boxes in all goal positions
        @param goal_pos: positions of the goals
        @return: a boolean value shows whether current state is goal state
        """
        return self.box_pos == goal_pos

    def deep_copy_box_pos(self):
        """
        Deep copy of positon of boxes
        @return: a copy value of the positions of boxes
        """
        return self.box_pos.copy()

class DeadlockSolver:
    @staticmethod
    def has_simple_deadlock(matrix, num_row, num_col, goal_pos):
        """
        Static method to pre-mark if a position in matrix has a simple deadlock. Simple deadlocks squares 
        of a level never change during the gameplay.
        @param matrix: a map of the gameplay
        @param num_row: the number of row of matrix
        @param num_col: the number of column of matrix
        @param goal_pos: a set of tuple displays positions of the goals
        @return: a pre-marked matrix with boolean values showing that positions has simple deadlock or not
        """
        matrix_flag = [[True] * num_col for i in range(num_row)] #pre-mark all position of matrix as deadlock
        #for loop with BFS style (use queue data structure) to pull the boxes from all goal positions 
        #to all posible positions of matrix.
        for goal in goal_pos:
            q = Queue() #FIFO queue for storing the positions
            q.put(goal)
            matrix_flag[goal[0]][goal[1]] = False #This position is not a deadlock
            while not q.empty():
                (x, y) = q.get()
                #We can pull a box up if position (x - 1, y) and (x - 2, y) are not the walls
                if matrix[x - 1][y] != '#' and matrix[x - 2][y] != '#':
                    if (matrix_flag[x - 1][y]):
                        q.put((x - 1, y))
                        matrix_flag[x - 1][y] = False #This position is not a deadlock
                #We can pull a box down if position (x + 1, y) and (x + 2, y) are not the walls
                if matrix[x + 1][y] != '#' and matrix[x + 2][y] != '#':
                    if (matrix_flag[x + 1][y]):
                        q.put((x + 1, y))
                        matrix_flag[x + 1][y] = False #This position is not a deadlock
                #We can pull a box left if position (x, y - 1) and (x, y - 2) are not the walls
                if matrix[x][y - 1] != '#' and matrix[x][y - 2] != '#':
                    if (matrix_flag[x][y - 1]):
                        q.put((x, y - 1))
                        matrix_flag[x][y - 1] = False #This position is not a deadlock
                #We can pull a box right if position (x, y + 1) and (x, y + 2) are not the walls
                if matrix[x][y + 1] != '#' and matrix[x][y + 2] != '#':
                    if (matrix_flag[x][y + 1]):
                        q.put((x, y + 1))
                        matrix_flag[x][y + 1] = False #This position is not a deadlock
        return matrix_flag

    @staticmethod
    def has_freeze_deadlock(pos, matrix, box_pos, goal_pos, has_simple_deadlock, checked_list):
        """
        Static method a move of a box to a new position has a freeze deadlock
        @param pos: a tuple of new position of the box after being moved
        @param box_pos: A set of tuples which displays the positions of boxes after moving the box
        @param goal_pos: a set of tuple displays positions of the goals
        @param has_simple_deadlock: the pre-marked of simple deadlocks of matrix
        @param checked_list: a set of tuple storing all freezed deadlock nodes has been checked so far
        @return: a boolean value show that if a move of the box to new position has deadlock or not
        """
        (x, y) = pos #assign new position
        checked_list.add((x, y)) #mark new position as being checked
        # The box is blocked along the vertical axis when one of the following checks are true:
        #     If there is a wall on the left or on the right side of the box then the box is blocked along this axis
        #     If there is a simple deadlock square on both sides (left and right) of the box the box is blocked along this axis
        #     If there is a box one the left or right side then this box is blocked if the other box is blocked. 
        x_axis_freeze = False
        if matrix[x + 1][y] == '#' or matrix[x - 1][y] == '#':
            x_axis_freeze = True
        elif has_simple_deadlock[x + 1][y] and has_simple_deadlock[x - 1][y]:
            x_axis_freeze = True
        elif (x + 1, y) in box_pos and ((x + 1, y) in checked_list or DeadlockSolver.has_freeze_deadlock((x + 1, y), matrix, box_pos, goal_pos, has_simple_deadlock, checked_list)):
            x_axis_freeze = True
        elif (x - 1, y) in box_pos and ((x - 1, y) in checked_list or DeadlockSolver.has_freeze_deadlock((x - 1, y), matrix, box_pos, goal_pos, has_simple_deadlock, checked_list)):
            x_axis_freeze = True
        else:
            return False
        # The box is blocked along the horizontal axis when one of the following checks are true:
        #     If there is a wall on the above side or under side of the box then the box is blocked along this axis
        #     If there is a simple deadlock square on both sides (above and under) of the box the box is blocked along this axis
        #     If there is a box one the above or under side then this box is blocked if the other box is blocked. 
        y_axis_freeze = False
        if matrix[x][y + 1] == '#' or matrix[x][y - 1] == '#':
            y_axis_freeze = True
        elif has_simple_deadlock[x][y + 1] and has_simple_deadlock[x][y - 1]:
            y_axis_freeze = True
        elif (x, y + 1) in box_pos and ((x, y + 1) in checked_list or DeadlockSolver.has_freeze_deadlock((x, y + 1), matrix, box_pos, goal_pos, has_simple_deadlock, checked_list)):
            y_axis_freeze = True
        elif (x, y - 1) in box_pos and ((x, y - 1) in checked_list or DeadlockSolver.has_freeze_deadlock((x, y - 1), matrix, box_pos, goal_pos, has_simple_deadlock, checked_list)):
            y_axis_freeze = True
        else:
            return False
        #If the new box position doesn't make a goal state, we accept this situation as freeze deadlock
        all_box_not_in_goal = False
        for box in checked_list:
            if box not in goal_pos:
                all_box_not_in_goal = True
        return x_axis_freeze and y_axis_freeze and all_box_not_in_goal

class Search(ABC):
    def __init__(self, num_row, num_col, matrix, box_pos, goal_pos, player_pos):
        """
        Creat a new Search object
        @param num_row: the number of rows of matrix
        @param num_col: the number of columns of matrix
        @param box_pos: A set of tuples which displays the positions of boxes
        @param goal_pos: a set of tuple displays positions of the goals
        @param player_pos: A tuple which displays the position of player in a state
        """
        self.num_row = num_row
        self.num_col = num_col
        self.matrix = matrix
        self.initial_state = State(box_pos, player_pos, None)
        self.goal_pos = goal_pos
        #add new attribute has_simple_deadlock to track simple deadlock postition
        self.has_simple_deadlock = DeadlockSolver.has_simple_deadlock(self.matrix, self.num_row, self.num_col, self.goal_pos)

    def can_go_up(self, current_state):
        """
        Check if player can go up to make a new state
        @param current_state: the current state object of searching
        @return: a boolean value show that whether a new state is valid
        """
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        #The player can go up if all of the following checks are true:
            #The player x-coordinate position greater than 1
            #The above of player position is not a wall
            #If the above player is a box then:
                #The above of that box must not be a wall and a box
                #The above of that box must not has any types of deadlocks
        if x <= 1:
            return False
        t1 = self.matrix[x - 1][y]
        t2 = self.matrix[x - 2][y]
        box_pos = current_state.box_pos
        if t1 == '#':
            return False
        elif (x - 1, y) in box_pos:
            if t2 == '#' or (x - 2, y) in box_pos or self.has_simple_deadlock[x - 2][y]:
                return False
            else:
                new_box = box_pos.copy()
                new_box.remove((x - 1, y))
                new_box.add((x - 2, y))
                if DeadlockSolver.has_freeze_deadlock((x - 2, y), self.matrix, new_box, self.goal_pos, self.has_simple_deadlock, set()):
                    return False
        return True

    def go_up(self, current_state, heuristic = None):
        """
        Move up the player and change the state
        @param current_state: the current state object of searching
        @param heuristic: the heuristic function if we implement A* algorithm
        """
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        #create a set of tuples of box positions for a new state
        new_box_pos = current_state.deep_copy_box_pos()
        #delete all box position and add new box position
        if (x - 1, y) in current_state.box_pos:
            new_box_pos.remove((x - 1, y))
            new_box_pos.add((x - 2, y))
        #create g value and f value of new state by using heuristic function
        if heuristic:
            new_gval = current_state.gval + 1 #g value of new state = g value of current state + 1
            new_fval = new_gval + heuristic(new_box_pos, self.goal_pos) #f value = g value + value of heuristic function of new state
            return State(new_box_pos, (x - 1, y), current_state, new_gval, new_fval) 
        return State(new_box_pos, (x - 1, y), current_state)

    def can_go_down(self, current_state):
        """
        Check if player can go down to make a new state
        @param current_state: the current state object of searching
        @return: a boolean value show that whether a new state is valid
        """
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        #The player can go down if all of the following checks are true:
            #The player x-coordinate position less than num_row - 2
            #The above of under position is not a wall
            #If the under player is a box then:
                #The under of that box must not be a wall and a box
                #The under of that box must not has any types of deadlocks
        if (x >= self.num_row - 2):
            return False
        t1 = self.matrix[x + 1][y]
        t2 = self.matrix[x + 2][y]
        box_pos = current_state.box_pos
        if t1 == '#':
            return False
        elif (x + 1, y) in box_pos:
            if t2 == '#' or (x + 2, y) in box_pos or self.has_simple_deadlock[x + 2][y]:
                return False
            else:
                new_box = box_pos.copy()
                new_box.remove((x + 1, y))
                new_box.add((x + 2, y))
                if DeadlockSolver.has_freeze_deadlock((x + 2, y), self.matrix, new_box, self.goal_pos, self.has_simple_deadlock, set()):
                    return False
        return True

    def go_down(self, current_state, heuristic = None):
        """
        Move down the player and change the state
        @param current_state: the current state object of searching
        @param heuristic: the heuristic function if we implement A* algorithm
        """
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        #create a set of tuples of box positions for a new state
        new_box_pos = current_state.deep_copy_box_pos()
        #delete all box position and add new box position
        if ((x + 1, y) in current_state.box_pos):
            new_box_pos.remove((x + 1, y))
            new_box_pos.add((x + 2, y))
        #create g value and f value of new state by using heuristic function
        if heuristic:
            new_gval = current_state.gval + 1 #g value of new state = g value of current state + 1
            new_fval = new_gval + heuristic(new_box_pos, self.goal_pos) #f value = g value + value of heuristic function of new state
            return State(new_box_pos, (x + 1, y), current_state, new_gval, new_fval) 
        return State(new_box_pos, (x + 1, y), current_state)

    def can_go_left(self, current_state):
        """
        Check if player can go left to make a new state
        @param current_state: the current state object of searching
        @return: a boolean value show that whether a new state is valid
        """
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        #The player can go down if all of the following checks are true:
            #The player y-coordinate position greater than 1
            #The left side of left position is not a wall
            #If the left player is a box then:
                #The left of that box must not be a wall and a box
                #The left of that box must not has any types of deadlocks
        if (y <= 1):
            return False
        t1 = self.matrix[x][y - 1]
        t2 = self.matrix[x][y - 2]
        box_pos = current_state.box_pos
        if t1 == '#':
            return False
        elif (x, y - 1) in box_pos:
            if t2 == '#' or (x, y - 2) in box_pos or self.has_simple_deadlock[x][y - 2]:
                return False
            else:
                new_box = box_pos.copy()
                new_box.remove((x, y - 1))
                new_box.add((x, y - 2))
                if DeadlockSolver.has_freeze_deadlock((x, y - 2), self.matrix, new_box, self.goal_pos, self.has_simple_deadlock, set()):
                    return False
        return True

    def go_left(self, current_state, heuristic = None):
        """
        Move left the player and change the state
        @param current_state: the current state object of searching
        @param heuristic: the heuristic function if we implement A* algorithm
        """
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        #create a set of tuples of box positions for a new state
        new_box_pos = current_state.deep_copy_box_pos()
        #delete all box position and add new box position
        if ((x, y - 1) in current_state.box_pos):
            new_box_pos.remove((x, y - 1))
            new_box_pos.add((x, y - 2))
        #create g value and f value of new state by using heuristic function
        if heuristic:
            new_gval = current_state.gval + 1 #g value of new state = g value of current state + 1
            new_fval = new_gval + heuristic(new_box_pos, self.goal_pos) #f value = g value + value of heuristic function of new state
            return State(new_box_pos, (x, y - 1), current_state, new_gval, new_fval) 
        return State(new_box_pos, (x, y - 1), current_state)

    def can_go_right(self, current_state):
        """
        Check if player can go right to make a new state
        @param current_state: the current state object of searching
        @return: a boolean value show that whether a new state is valid
        """
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        #The player can go down if all of the following checks are true:
            #The player y-coordinate position less than number of column - 2
            #The right side of left position is not a wall
            #If the right player is a box then:
                #The right of that box must not be a wall and a box
                #The right of that box must not has any types of deadlocks
        if (y >= self.num_col - 2): 
            return False
        t1 = self.matrix[x][y + 1]
        t2 = self.matrix[x][y + 2]
        box_pos = current_state.box_pos
        if t1 == '#':
            return False
        elif (x, y + 1) in box_pos:
            if t2 == '#' or (x, y + 2) in box_pos or self.has_simple_deadlock[x][y + 2]:
                return False
            else:
                new_box = box_pos.copy()
                new_box.remove((x, y + 1))
                new_box.add((x, y + 2))
                if DeadlockSolver.has_freeze_deadlock((x, y + 2), self.matrix, new_box, self.goal_pos, self.has_simple_deadlock, set()):
                    return False
        return True

    def go_right(self, current_state, heuristic = None):
        """
        Move left the player and change the state
        @param current_state: the current state object of searching
        @param heuristic: the heuristic function if we implement A* algorithm
        """
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        #create a set of tuples of box positions for a new state
        new_box_pos = current_state.deep_copy_box_pos()
        #delete all box position and add new box position
        if ((x, y + 1) in current_state.box_pos):
            new_box_pos.remove((x, y + 1))
            new_box_pos.add((x, y + 2))
        #create g value and f value of new state by using heuristic function
        if heuristic:
            new_gval = current_state.gval + 1 #g value of new state = g value of current state + 1
            new_fval = new_gval + heuristic(new_box_pos, self.goal_pos) #f value = g value + value of heuristic function of new state
            return State(new_box_pos, (x, y + 1), current_state, new_gval, new_fval) 
        return State(new_box_pos, (x, y + 1), current_state)

    def construct_path(self, state):
        """
        Construct the path to goal state
        @param state: the state to start construting the path
        @return: The list of elements display the steps U, D, L, R conresponding to Up, Down, Left, Right
        """
        path = list() #initilize list of path
        #Loop to go back to ancestor nodes until reaching initial node
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

    @abstractmethod
    def search():
        """
        Abstract method for Search class
        """
        pass
    
class BFS(Search):
    def __init__(self, num_row, num_col, matrix, box_pos, goal_pos, player_pos):
        """
        Creat a new BFS Search object
        @param num_row: the number of rows of matrix
        @param num_col: the number of columns of matrix
        @param box_pos: A set of tuples which displays the positions of boxes
        @param goal_pos: a set of tuple displays positions of the goals
        @param player_pos: A tuple which displays the position of player in a state
        """
        super().__init__(num_row, num_col, matrix, box_pos, goal_pos, player_pos)

    def handle(self, new_state, closed_set, frontier):
        """
        Handle closed_set and frontier queue after making a move
        @param new_state: a state after making a move
        @param closed_set: includes all nodes which are in the frontier queue or not in frontier queue but were explored
        @param frontier: a FIFO queue of states (nodes)
        """
        #If this is the first time we have explored this state (not in closed_set):
            #Add this state to closed_set
            #Add this state to frontier queue
        if (new_state not in closed_set):
            closed_set.add(new_state)
            frontier.put(new_state)

    def expand(self, state, closed_set, frontier):
        """
        Function to expand all neighbors of a state
        @param state: a state to be expanded
        @param closed_set: includes all nodes which are in the frontier queue or not in frontier queue but were explored
        @param frontier: a FIFO queue of states (nodes)
        """
        if (self.can_go_up(state)):
            new_state = self.go_up(state)
            self.handle(new_state, closed_set, frontier)
        if (self.can_go_right(state)):
            new_state = self.go_right(state)
            self.handle(new_state, closed_set, frontier)
        if (self.can_go_left(state)):
            new_state = self.go_left(state)
            self.handle(new_state, closed_set, frontier)
        if (self.can_go_down(state)):
            new_state = self.go_down(state)
            self.handle(new_state, closed_set, frontier)

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
        print("--- %s seconds ---" % (time.time() - start_time))
        return ["Impossible"]

class AStar(Search):
    def __init__(self, num_row, num_col, matrix, box_pos, goal_pos, player_pos):
        """
        Creat a new AStar Search object
        @param num_row: the number of rows of matrix
        @param num_col: the number of columns of matrix
        @param box_pos: A set of tuples which displays the positions of boxes
        @param goal_pos: a set of tuple displays positions of the goals
        @param player_pos: A tuple which displays the position of player in a state
        """
        super().__init__(num_row, num_col, matrix, box_pos, goal_pos, player_pos)
        #initialize g value and f value for initial state
        self.initial_state.gval = 0
        self.initial_state.fval = self.heuristic(box_pos, goal_pos)

    def handle(self, new_state, closed_set, frontier, state_lookup_table):
        """
        Handle closed_set and frontier queue after making a move
        @param new_state: a state after making a move
        @param closed_set: includes all nodes which are in the frontier queue or not in frontier queue but were explored
        @param frontier: a Priority queue of states (nodes)
        @param state_lookup_table: contains entries which have reference to all states that have been explored so far.
        Each entry also has a boolean value to check if the node is in frontier or not
        """
        #If this is the first time we have explored this state (not in closed_set):
            #Add this state to closed_set
            #Add this state to frontier queue 
            #Update lookup table
        if (new_state not in closed_set):
            closed_set.add(new_state)
            frontier.put(new_state)
            state_lookup_table[hash(new_state)] = [new_state, True]
        else:
            #If this state was explored before and have g value less than new g value:
                #Update values of that state to new state
                #if that state not in frontier then add it to frontier
            id = hash(new_state)
            if (new_state.gval < state_lookup_table[id][0].gval):
                state_lookup_table[id][0].fval = new_state.fval
                state_lookup_table[id][0].gval = new_state.gval
                state_lookup_table[id][0].ancestor = new_state.ancestor
                if (state_lookup_table[id][1] == False):
                    state_lookup_table[id][1] = True
                    frontier.put(new_state)

    def expand(self, state, closed_set, frontier, state_lookup_table):
        """
        Function to expand all neighbors of a state
        @param state: a state to be expanded
        @param closed_set: includes all nodes which are in the frontier queue or not in frontier queue but were explored
        @param frontier: a Priority queue of states (nodes)
        @param state_lookup_table: contains entries which have reference to all states that have been explored so far.
        Each entry also has a boolean value to check if the node is in frontier or not
        """
        if (self.can_go_up(state)):
            new_state = self.go_up(state, self.heuristic)
            self.handle(new_state, closed_set, frontier, state_lookup_table)
        if (self.can_go_right(state)):
            new_state = self.go_right(state, self.heuristic)
            self.handle(new_state, closed_set, frontier, state_lookup_table)
        if (self.can_go_left(state)):
            new_state = self.go_left(state, self.heuristic)
            self.handle(new_state, closed_set, frontier, state_lookup_table)
        if (self.can_go_down(state)):
            new_state = self.go_down(state, self.heuristic)
            self.handle(new_state, closed_set, frontier, state_lookup_table)

    def manhattan(self, x1, y1, x2, y2):
        """
        Calculate manhattan distance
        @param x1: x-coordinate of object 1
        @param y1: y-coordinate of object 1
        @param x2: x-coordinate of object 2 
        @param y2: y-coordinate of object 2
        @return manhattan distance of 2 objects
        """
        return abs(x1 - x2) + abs(y1 - y2)

    def heuristic(self, box_pos, goal_pos):
        """
        Heuristic function for A Star Algorithm
        @param box_pos: A set of tuples which displays the positions of boxes
        @param goal_pos: a set of tuple displays positions of the goals
        @return: a heuristic value (h value)
        """
        sum = 0
        #for each box position, calculate its minimum distance to all the goals. 
        #After that, calculate the sum of all that distances
        for box in box_pos:
            sum = sum + min([self.manhattan(box[0], box[1], goal[0], goal[1]) for goal in goal_pos])
        return sum

    def search(self):
        start_time = time.time()
        frontier = PriorityQueue()
        frontier.put(self.initial_state)
        closed_set = set()
        closed_set.add(self.initial_state)
        state_lookup_table = dict()
        state_lookup_table[hash(self.initial_state)] = [self.initial_state, True]
        a = 0

        while (not frontier.empty()):

            a += 1

            current_state = frontier.get()
            state_lookup_table[hash(self.initial_state)][1] = False
            if (current_state.is_final_state(self.goal_pos)):
                print(a)
                print("--- %s seconds ---" % (time.time() - start_time))
                return self.construct_path(current_state)
            self.expand(current_state, closed_set, frontier, state_lookup_table)
            #frontier.extend(self.expand(current_state, closed_set))
        print("--- %s seconds ---" % (time.time() - start_time))
        return ["Impossible"]

if __name__ == "__main__":
    for i in range (1, 41):
        print(i)
        with open('Mini Cosmos/Level_' + str(i) + '.txt', 'r') as file:
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

        ob = BFS(num_row, num_col, matrix, box_pos, goal_pos, player_pos)
        print(ob.search())
        ob = AStar(num_row, num_col, matrix, box_pos, goal_pos, player_pos)
        print(ob.search())
        print("---------------------------------")