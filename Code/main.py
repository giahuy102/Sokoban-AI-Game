"""Sokoban routines
    A) Class State:
        Define the structure of a state in state space. This class has some functions helping determine a state
        in search space.
    B) Class DeadlockSolver:
        Has some utility function to determine whether a state creates a deadlock situation. "Deadlock" means
        the level isn't solvable anymore, no matter what the user does.
    C) Class Search:
        Is an abstract class for types of searching. It also contains some utility function for making decisions
        on changing a state
    D) Class BFS:
        Contains some functions implementing BFS algorithm
    E) Class AStar:
        Contains some functions implementing AStar algorithm
    F) Class Master:
        Contains some functions implementing gameplay.
    E) Class StartFrame, LevelFrame, GameFrame, Playing, DoneFrame and AlgorithmFrame:
        Used for creating frame in the user interface.
"""
from abc import ABC, abstractmethod
from queue import PriorityQueue, Queue
from tkinter import *
import tkinter.ttk as ttk
import copy
import time

# Initial constant:
WD = 1125
HT = 790
size = 35
type_algorithm, type_level = 0, 0

map = []
path = []

# List of Levels:
level_list = ["Choose...",
              "Level_01", "Level_02", "Level_03", "Level_04", "Level_05", "Level_06", "Level_07", "Level_08", "Level_09", "Level_10",
              "Level_11", "Level_12", "Level_13", "Level_14", "Level_15", "Level_16", "Level_17", "Level_18", "Level_19", "Level_20",
              "Level_21", "Level_22", "Level_23", "Level_24", "Level_25", "Level_26", "Level_27", "Level_28", "Level_29", "Level_30",
              "Level_31", "Level_32", "Level_33", "Level_34", "Level_35", "Level_36", "Level_37", "Level_38", "Level_39", "Level_40",
              ]


class State:
    def __init__(self, box_pos, player_pos, ancestor, gval=-1, fval=-1):
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
        return hash(
            (self.player_pos, frozenset(self.box_pos)))  # use frozenset (immutable set) for creating hashable value

    def __lt__(self, state):
        """
        For A* algorithm first we muse a priority queue data structure. This queue stores search nodes
        waiting to be expanded. Thus we need to define a node1 < node2 function by defining
        the __lt__ function. Dependent on the type of search this comparison function compares the h-value,
        the g-value or the f-value of the nodes. Note for the f-value we wish to break ties by letting
        node1 < node2 if they both have identical f-values but if node1 has a GREATER g value.
        This means that we expand nodes along deeper paths first causing the search to proceed directly to the goal
        """
        if self.fval == state.fval:
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
        matrix_flag = [[True] * num_col for i in range(num_row)]  # pre-mark all position of matrix as deadlock
        # for loop with BFS style (use queue data structure) to pull the boxes from all goal positions
        # to all posible positions of matrix.
        for goal in goal_pos:
            q = Queue()  # FIFO queue for storing the positions
            q.put(goal)
            matrix_flag[goal[0]][goal[1]] = False  # This position is not a deadlock
            while not q.empty():
                (x, y) = q.get()
                # We can pull a box up if position (x - 1, y) and (x - 2, y) are not the walls
                if matrix[x - 1][y] != '#' and matrix[x - 2][y] != '#':
                    if matrix_flag[x - 1][y]:
                        q.put((x - 1, y))
                        matrix_flag[x - 1][y] = False  # This position is not a deadlock
                # We can pull a box down if position (x + 1, y) and (x + 2, y) are not the walls
                if matrix[x + 1][y] != '#' and matrix[x + 2][y] != '#':
                    if matrix_flag[x + 1][y]:
                        q.put((x + 1, y))
                        matrix_flag[x + 1][y] = False  # This position is not a deadlock
                # We can pull a box left if position (x, y - 1) and (x, y - 2) are not the walls
                if matrix[x][y - 1] != '#' and matrix[x][y - 2] != '#':
                    if matrix_flag[x][y - 1]:
                        q.put((x, y - 1))
                        matrix_flag[x][y - 1] = False  # This position is not a deadlock
                # We can pull a box right if position (x, y + 1) and (x, y + 2) are not the walls
                if matrix[x][y + 1] != '#' and matrix[x][y + 2] != '#':
                    if matrix_flag[x][y + 1]:
                        q.put((x, y + 1))
                        matrix_flag[x][y + 1] = False  # This position is not a deadlock
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
        (x, y) = pos  # assign new position
        checked_list.add((x, y))  # mark new position as being checked
        # The box is blocked along the vertical axis when one of the following checks are true:
        #     If there is a wall on the left or on the right side of the box then the box is blocked along this axis
        #     If there is a simple deadlock square on both sides (left and right) of the box the box is blocked along this axis
        #     If there is a box one the left or right side then this box is blocked if the other box is blocked.
        x_axis_freeze = False
        if matrix[x + 1][y] == '#' or matrix[x - 1][y] == '#':
            x_axis_freeze = True
        elif has_simple_deadlock[x + 1][y] and has_simple_deadlock[x - 1][y]:
            x_axis_freeze = True
        elif (x + 1, y) in box_pos and (
                (x + 1, y) in checked_list or DeadlockSolver.has_freeze_deadlock((x + 1, y), matrix, box_pos, goal_pos,
                                                                                 has_simple_deadlock, checked_list)):
            x_axis_freeze = True
        elif (x - 1, y) in box_pos and (
                (x - 1, y) in checked_list or DeadlockSolver.has_freeze_deadlock((x - 1, y), matrix, box_pos, goal_pos,
                                                                                 has_simple_deadlock, checked_list)):
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
        elif (x, y + 1) in box_pos and (
                (x, y + 1) in checked_list or DeadlockSolver.has_freeze_deadlock((x, y + 1), matrix, box_pos, goal_pos,
                                                                                 has_simple_deadlock, checked_list)):
            y_axis_freeze = True
        elif (x, y - 1) in box_pos and (
                (x, y - 1) in checked_list or DeadlockSolver.has_freeze_deadlock((x, y - 1), matrix, box_pos, goal_pos,
                                                                                 has_simple_deadlock, checked_list)):
            y_axis_freeze = True
        else:
            return False
        # If the new box position doesn't make a goal state, we accept this situation as freeze deadlock
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
        # add new attribute has_simple_deadlock to track simple deadlock postition
        self.has_simple_deadlock = DeadlockSolver.has_simple_deadlock(self.matrix, self.num_row, self.num_col,
                                                                      self.goal_pos)

    def can_go_up(self, current_state):
        """
        Check if player can go up to make a new state
        @param current_state: the current state object of searching
        @return: a boolean value show that whether a new state is valid
        """
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        # The player can go up if all of the following checks are true:
        # The player x-coordinate position greater than 1
        # The above of player position is not a wall
        # If the above player is a box then:
        # The above of that box must not be a wall and a box
        # The above of that box must not has any types of deadlocks
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
                if DeadlockSolver.has_freeze_deadlock((x - 2, y), self.matrix, new_box, self.goal_pos,
                                                      self.has_simple_deadlock, set()):
                    return False
        return True

    def go_up(self, current_state, heuristic=None):
        """
        Move up the player and change the state
        @param current_state: the current state object of searching
        @param heuristic: the heuristic function if we implement A* algorithm
        @return: a state after go up
        """
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        # create a set of tuples of box positions for a new state
        new_box_pos = current_state.deep_copy_box_pos()
        # delete all box position and add new box position
        if (x - 1, y) in current_state.box_pos:
            new_box_pos.remove((x - 1, y))
            new_box_pos.add((x - 2, y))
        # create g value and f value of new state by using heuristic function
        if heuristic:
            new_gval = current_state.gval + 1  # g value of new state = g value of current state + 1
            new_fval = new_gval + heuristic(new_box_pos,
                                            self.goal_pos)  # f value = g value + value of heuristic function of new state
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
        # The player can go down if all of the following checks are true:
        # The player x-coordinate position less than num_row - 2
        # The above of under position is not a wall
        # If the under player is a box then:
        # The under of that box must not be a wall and a box
        # The under of that box must not has any types of deadlocks
        if x >= self.num_row - 2:
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
                if DeadlockSolver.has_freeze_deadlock((x + 2, y), self.matrix, new_box, self.goal_pos,
                                                      self.has_simple_deadlock, set()):
                    return False
        return True

    def go_down(self, current_state, heuristic=None):
        """
        Move down the player and change the state
        @param current_state: the current state object of searching
        @param heuristic: the heuristic function if we implement A* algorithm
        @return: a state after go down
        """
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        # create a set of tuples of box positions for a new state
        new_box_pos = current_state.deep_copy_box_pos()
        # delete all box position and add new box position
        if (x + 1, y) in current_state.box_pos:
            new_box_pos.remove((x + 1, y))
            new_box_pos.add((x + 2, y))
        # create g value and f value of new state by using heuristic function
        if heuristic:
            new_gval = current_state.gval + 1  # g value of new state = g value of current state + 1
            new_fval = new_gval + heuristic(new_box_pos,
                                            self.goal_pos)  # f value = g value + value of heuristic function of new state
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
        # The player can go down if all of the following checks are true:
        # The player y-coordinate position greater than 1
        # The left side of left position is not a wall
        # If the left player is a box then:
        # The left of that box must not be a wall and a box
        # The left of that box must not has any types of deadlocks
        if y <= 1:
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
                if DeadlockSolver.has_freeze_deadlock((x, y - 2), self.matrix, new_box, self.goal_pos,
                                                      self.has_simple_deadlock, set()):
                    return False
        return True

    def go_left(self, current_state, heuristic=None):
        """
        Move left the player and change the state
        @param current_state: the current state object of searching
        @param heuristic: the heuristic function if we implement A* algorithm
        @return: a state after go left
        """
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        # create a set of tuples of box positions for a new state
        new_box_pos = current_state.deep_copy_box_pos()
        # delete all box position and add new box position
        if (x, y - 1) in current_state.box_pos:
            new_box_pos.remove((x, y - 1))
            new_box_pos.add((x, y - 2))
        # create g value and f value of new state by using heuristic function
        if heuristic:
            new_gval = current_state.gval + 1  # g value of new state = g value of current state + 1
            new_fval = new_gval + heuristic(new_box_pos,
                                            self.goal_pos)  # f value = g value + value of heuristic function of new state
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
        # The player can go down if all of the following checks are true:
        # The player y-coordinate position less than number of column - 2
        # The right side of left position is not a wall
        # If the right player is a box then:
        # The right of that box must not be a wall and a box
        # The right of that box must not has any types of deadlocks
        if y >= self.num_col - 2:
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
                if DeadlockSolver.has_freeze_deadlock((x, y + 2), self.matrix, new_box, self.goal_pos,
                                                      self.has_simple_deadlock, set()):
                    return False
        return True

    def go_right(self, current_state, heuristic=None):
        """
        Move left the player and change the state
        @param current_state: the current state object of searching
        @param heuristic: the heuristic function if we implement A* algorithm
        @return: a state after go right
        """
        x = current_state.player_pos[0]
        y = current_state.player_pos[1]
        # create a set of tuples of box positions for a new state
        new_box_pos = current_state.deep_copy_box_pos()
        # delete all box position and add new box position
        if (x, y + 1) in current_state.box_pos:
            new_box_pos.remove((x, y + 1))
            new_box_pos.add((x, y + 2))
        # create g value and f value of new state by using heuristic function
        if heuristic:
            new_gval = current_state.gval + 1  # g value of new state = g value of current state + 1
            new_fval = new_gval + heuristic(new_box_pos,
                                            self.goal_pos)  # f value = g value + value of heuristic function of new state
            return State(new_box_pos, (x, y + 1), current_state, new_gval, new_fval)
        return State(new_box_pos, (x, y + 1), current_state)

    def construct_path(self, state):
        """
        Construct the path to goal state
        @param state: the state to start construting the path
        @return: The list of elements display the steps U, D, L, R conresponding to Up, Down, Left, Right
        """
        path = list()  # initilize list of path
        # Loop to go back to ancestor nodes until reaching initial node
        while state.ancestor:
            x1 = state.ancestor.player_pos[0]
            y1 = state.ancestor.player_pos[1]
            x2 = state.player_pos[0]
            y2 = state.player_pos[1]
            if x2 > x1:
                path.insert(0, 'D')
            elif x2 < x1:
                path.insert(0, 'U')
            elif y2 > y1:
                path.insert(0, 'R')
            else:
                path.insert(0, 'L')
            state = state.ancestor
        return path

    @abstractmethod
    def search(self):
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
        # If this is the first time we have explored this state (not in closed_set):
        # Add this state to closed_set
        # Add this state to frontier queue
        if new_state not in closed_set:
            closed_set.add(new_state)
            frontier.put(new_state)

    def expand(self, state, closed_set, frontier):
        """
        Function to expand all neighbors of a state
        @param state: a state to be expanded
        @param closed_set: includes all nodes which are in the frontier queue or not in frontier queue but were explored
        @param frontier: a FIFO queue of states (nodes)
        """
        if self.can_go_up(state):
            new_state = self.go_up(state)
            self.handle(new_state, closed_set, frontier)
        if self.can_go_right(state):
            new_state = self.go_right(state)
            self.handle(new_state, closed_set, frontier)
        if self.can_go_left(state):
            new_state = self.go_left(state)
            self.handle(new_state, closed_set, frontier)
        if self.can_go_down(state):
            new_state = self.go_down(state)
            self.handle(new_state, closed_set, frontier)

    def search(self):
        """
        Execute BFS algorithm
        @return: the list of steps that the player should follow to reach the goal state
        @return: the number of expanded nodes (number of nodes dequeued from the queue during searching process)
        @return: the number of explored nodes (total number of nodes explored during searching process)
        """
        frontier = Queue() # the FIFO queue
        frontier.put(self.initial_state)
        closed_set = set() # the set contains all nodes explored during searching process
        closed_set.add(self.initial_state)
        expanded_num = 0 # initialize number of expanded node as 0
        # Repeat below steps until the frontier is empty:
            # Dequeue node from frontier
            # Check if it is goal state => True => Return solution
            # Expand all valid neighbors of current state
        while not frontier.empty():
            expanded_num += 1
            current_state = frontier.get() #get the head node of the queue
            if current_state.is_final_state(self.goal_pos):
                path = self.construct_path(current_state)
                return path, expanded_num, len(closed_set)
            self.expand(current_state, closed_set, frontier)
        return ["Impossible"], expanded_num, len(closed_set)


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
        # initialize g value and f value for initial state
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
        # If this is the first time we have explored this state (not in closed_set):
        # Add this state to closed_set
        # Add this state to frontier queue
        # Update lookup table
        if new_state not in closed_set:
            closed_set.add(new_state)
            frontier.put(new_state)
            state_lookup_table[hash(new_state)] = [new_state, True]
        else:
            # If this state was explored before and have g value less than new g value:
            # Update values of that state to new state
            # if that state not in frontier then add it to frontier
            id = hash(new_state)
            if new_state.gval < state_lookup_table[id][0].gval:
                state_lookup_table[id][0].fval = new_state.fval
                state_lookup_table[id][0].gval = new_state.gval
                state_lookup_table[id][0].ancestor = new_state.ancestor
                if state_lookup_table[id][1] == False:
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
        if self.can_go_up(state):
            new_state = self.go_up(state, self.heuristic)
            self.handle(new_state, closed_set, frontier, state_lookup_table)
        if self.can_go_right(state):
            new_state = self.go_right(state, self.heuristic)
            self.handle(new_state, closed_set, frontier, state_lookup_table)
        if self.can_go_left(state):
            new_state = self.go_left(state, self.heuristic)
            self.handle(new_state, closed_set, frontier, state_lookup_table)
        if self.can_go_down(state):
            new_state = self.go_down(state, self.heuristic)
            self.handle(new_state, closed_set, frontier, state_lookup_table)

    def manhattan(self, x1, y1, x2, y2):
        """
        Calculate manhattan distance
        @param x1: x-coordinate of object 1
        @param y1: y-coordinate of object 1
        @param x2: x-coordinate of object 2
        @param y2: y-coordinate of object 2
        @return: manhattan distance of 2 objects
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
        # for each box position, calculate its minimum distance (use manhattan) among the distances to all the goals.
        # After that, calculate the sum of all that minimum distance distances
        for box in box_pos:
            sum = sum + min([self.manhattan(box[0], box[1], goal[0], goal[1]) for goal in goal_pos])
        return sum

    def search(self):
        """
        Execute A* search algorithm
        @return: the list of steps that the player should follow to reach the goal state
        @return: the number of expanded nodes (number of nodes dequeued from the queue during searching process)
        @return: the number of explored nodes (total number of nodes explored during searching process)
        """
        frontier = PriorityQueue() # the priority queue
        frontier.put(self.initial_state)
        closed_set = set() # the set contains all nodes explored during searching process
        closed_set.add(self.initial_state)
        # the lookup table whose entries have references to all explored nodes
        # It also contains a boolean value to check if a node in frontier queue or not
        state_lookup_table = dict()
        state_lookup_table[hash(self.initial_state)] = [self.initial_state, True]
        expanded_num = 0 # initialize number of expanded node as 0
        # Repeat below steps until the frontier is empty:
            # Dequeue node from frontier
            # Check if it is goal state => True => Return solution
            # Expand all valid neighbors of current state
        while not frontier.empty():
            expanded_num += 1
            current_state = frontier.get() # get the node with highest priority (lowest cost)
            state_lookup_table[hash(current_state)][1] = False
            if current_state.is_final_state(self.goal_pos):
                path = self.construct_path(current_state)
                return path, expanded_num, len(closed_set)
            self.expand(current_state, closed_set, frontier, state_lookup_table)
        return ["Impossible"], expanded_num, len(closed_set)


class Master(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.container = ttk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.frames = {}
        self.map, self.search_matrix = [], []
        self.box_pos, self.goal_pos, self.player_pos = set(), set(), ()
        self.num_row, self.num_col = 0, 0
        self.path = ""
        self.expanded_node, self.explored_node, self.execution_time = None, None, None
        for F in (StartFrame, LevelFrame, GameFrame, AlgorithmFrame, DoneFrame):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='NSEW')
        self.switch_frame(StartFrame)

    def choose_level(self, lv):
        """
        Get level input from user in the menu option.
        Draw the game board and call search functions.
        @param lv: level selected by user.
        """
        print(type_level)
        if type_level == 0:
            level = "Micro Cosmos/" + lv + ".txt"
        else:
            level = "Mini Cosmos/" + lv + ".txt"
        temp = []
        with open(level, 'r') as f:
            for line in f:
                row = []
                for i in line:
                    row.append(i)
                temp.append(row)
        self.map = temp
        global map
        map = copy.deepcopy(temp)
        self.load_search_matrix(level)
        self.switch_frame(GameFrame)

    def load_search_matrix(self, level):
        """
        Load input matrix used for search functions.
        @param level: level selected by user.
        """
        with open(level, 'r') as f:
            self.search_matrix = [list(line.rstrip()) for line in f]
        self.goal_pos.clear()
        self.box_pos.clear()
        for i in range(len(self.search_matrix)):
            for j in range(len(self.search_matrix[i]) - 1):  # omit endline
                if self.search_matrix[i][j] == '.':
                    self.goal_pos.add((i, j))
                elif self.search_matrix[i][j] == '*':
                    self.box_pos.add((i, j))
                    self.goal_pos.add((i, j))
                elif self.search_matrix[i][j] == '$':
                    self.box_pos.add((i, j))
                elif self.search_matrix[i][j] == '@':
                    self.player_pos = (i, j)
                elif self.search_matrix[i][j] == '+':
                    self.player_pos = (i, j)
                    self.goal_pos.add((i, j))
        self.num_row, self.num_col = len(self.search_matrix), max([len(row) for row in self.search_matrix])
        # add extra " " character to some lines of matrix
        for row in self.search_matrix:
            for i in range(self.num_col):
                if i > len(row) - 1:
                    row.append(' ')

    def do_search(self):
        """
        Execute BFS or A* search algorithm.
        @return path:  the list of steps that the player should follow to reach the goal state.
        @param expanded_node: the number of expanded nodes (number of nodes dequeued from the queue during searching process).
        @param explored_node: the number of explored nodes (total number of nodes explored during searching process).
        """
        if type_algorithm == 0:
            bfs_search = BFS(self.num_row, self.num_col, self.search_matrix, self.box_pos, self.goal_pos,
                             self.player_pos)
            self.path, self.expanded_node, self.explored_node = bfs_search.search()
        else:
            a_star_search = AStar(self.num_row, self.num_col, self.search_matrix, self.box_pos, self.goal_pos,
                                  self.player_pos)
            self.path, self.expanded_node, self.explored_node = a_star_search.search()

    def switch_frame(self, cont):
        for F in (GameFrame, DoneFrame):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='NSEW')
        frame = self.frames[cont]
        frame.tkraise()


class StartFrame(ttk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        ttk.Frame.__init__(self, parent)
        self.start_frame = PhotoImage(file="images/Start_frame.png")
        self.start_button = PhotoImage(file="images/start_button_0.png")
        self.algorithm_button = PhotoImage(file="images/algorithm_button_0.png")
        self.exit_button = PhotoImage(file="images/exit_button_0.png")
        self.canvas = Canvas(self, width=WD, height=HT)
        self.canvas.pack()
        Label(self, image=self.start_frame).place(x=0, y=0)
        Button(self, image=self.start_button, command=lambda: controller.switch_frame(LevelFrame)).place(x=800, y=500)
        Button(self, image=self.algorithm_button, command=lambda: controller.switch_frame(AlgorithmFrame)).place(x=800, y=600)
        Button(self, image=self.exit_button, command=lambda: controller.destroy()).place(x=800, y=700)


class LevelFrame(ttk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        ttk.Frame.__init__(self, parent)

        self.level_frame = PhotoImage(file="images/Level_frame.png")
        self.home_button = PhotoImage(file="images//home_button_0.png")
        self.algorithm_button = PhotoImage(file="images/algorithm_button_1.png")
        self.variable = IntVar()
        Label(self, image=self.level_frame).place(x=0, y=0)
        Radiobutton(self, text="__ Micro Cosmos __", variable=self.variable, value=0, comman=self.set_level).place(x=450, y=250)
        Radiobutton(self, text="__ Mini Cosmos __", variable=self.variable, value=1, comman=self.set_level).place(x=650, y=250)
        level_buttons = []
        x = 100
        y = 300
        for i in range(1, 41):
            level_buttons.append(Button(self, text=level_list[i], font=('Helvetica',), command=lambda level=level_list[i]: controller.choose_level(level)).place(
                x=x, y=y))
            x = x + 100
            if i % 10 == 0:
                x = 100
                y = y + 100
        Button(self, image=self.home_button, command=lambda: controller.switch_frame(StartFrame)).place(x=100, y=700)
        Button(self, image=self.algorithm_button, command=lambda: controller.switch_frame(AlgorithmFrame)).place(x=230, y=700)

    def set_level(self):
        global type_level
        type_level = self.variable.get()


class AlgorithmFrame(ttk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        ttk.Frame.__init__(self, parent)
        self.game_frame = PhotoImage(file="images/Level_frame.png")
        self.bfs_button = PhotoImage(file="images/bfs_button.png")
        self.a_star_button = PhotoImage(file="images/astar_button.png")
        self.ok_button = PhotoImage(file="images/ok_button.png")
        self.variable = IntVar()
        Label(self, image=self.game_frame).place(x=0, y=0)
        Radiobutton(self, image=self.bfs_button, variable=self.variable, value=0, comman=self.set_alg).place(x=450, y=300)
        Radiobutton(self, image=self.a_star_button, variable=self.variable, value=1, comman=self.set_alg).place(x=450, y=500)
        Button(self, image=self.ok_button, command=lambda: controller.switch_frame(StartFrame)).place(x=520, y=650)

    def set_alg(self):
        global type_algorithm
        type_algorithm = self.variable.get()


class GameFrame(ttk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        ttk.Frame.__init__(self, parent)
        self.canvas = Canvas(self, width=WD, height=HT)
        self.game_frame = PhotoImage(file="images/Play_frame.png")
        self.play_button = PhotoImage(file="images/play_button.png")
        self.home_button = PhotoImage(file="images//home_button_0.png")
        self.algorithm_button = PhotoImage(file="images/algorithm_button_1.png")
        self.level_button = PhotoImage(file="images/level_button_0.png")
        self.play_button = PhotoImage(file="images/play_button.png")
        self.exit_button = PhotoImage(file="images/exit_button_1.png")
        Button(self, image=self.exit_button, command=lambda: controller.destroy()).place(x=1000, y=700)
        Button(self, image=self.play_button, command=lambda: self.play_game()).place(x=450, y=690)
        self.flag = 0
        controller.do_search()
        self.map = controller.map
        self.expanded_node = controller.expanded_node
        self.explored_node = controller.explored_node
        self.path = controller.path
        # Load images for drawing game board
        self.floor = PhotoImage(file="images/floor.png")
        self.wall = PhotoImage(file="images/wall.png")
        self.player = PhotoImage(file="images/player.png")
        self.box = PhotoImage(file="images/box.png")
        self.dock = PhotoImage(file="images/dock.png")
        self.box_on_dock = PhotoImage(file="images/box_on_dock.png")
        self.player_on_dock = PhotoImage(file="images/player_on_dock.png")
        self.draw_board()
        self.canvas.pack()

    def draw_board(self):
        """
        The modules required to draw required game based object on canvas
        """
        x = 350
        y = 210 + size
        flag = 0
        for row in self.map:
            flag = 0
            for char in row:
                if char != " ":
                    flag = 1
                if char == " " and flag == 1:  # floor
                    self.canvas.create_image(x, y, image=self.floor)
                elif char == "#":  # wall
                    self.canvas.create_image(x, y, image=self.wall)
                elif char == '@':  # player
                    self.canvas.create_image(x, y, image=self.player)
                elif char == '$':  # box
                    self.canvas.create_image(x, y, image=self.box)
                elif char == '.':  # dock
                    self.canvas.create_image(x, y, image=self.dock)
                elif char == '*':  # box on dock
                    self.canvas.create_image(x, y, image=self.box_on_dock)
                elif char == '+':  # player on dock
                    self.canvas.create_image(x, y, image=self.player_on_dock)
                x = x + size
            x = 350
            y = y + size

    def get_state(self, x, y):
        """
        @return: the state at position (x, y) in the map.
        """
        return self.map[y][x]

    def set_state(self, x, y, state):
        """
        Set the state at position(x, y) to new state.
        """
        self.map[y][x] = state

    def pos_player(self):
        """
        @return: the position of player in the map.
        """
        x = 0
        y = 0
        for row in self.map:
            for char in row:
                if char == "@" or char == "+":
                    return x, y, char
                else:
                    x = x + 1
            y = y + 1
            x = 0

    """
    Logical Functions below.
    The modules required to carry out game logic.
    """

    def move_box(self, x, y, a, b):
        """
        @param x, y: the current position of box.
        @param a, b: the future position of box to move.
        """
        cur_box = self.get_state(x, y)
        fur_box = self.get_state(x + a, y + b)
        if cur_box == "$" and fur_box == " ":
            self.set_state(x, y, " ")
            self.set_state(x + a, y + b, "$")
        elif cur_box == "$" and fur_box == ".":
            self.set_state(x, y, " ")
            self.set_state(x + a, y + b, "*")
        elif cur_box == "*" and fur_box == " ":
            self.set_state(x, y, ".")
            self.set_state(x + a, y + b, "$")
        elif cur_box == "*" and fur_box == ".":
            self.set_state(x, y, ".")
            self.set_state(x + a, y + b, "*")

    def can_move(self, x, y):
        """
        @return: TRUE if player can move to the position (x, y) in the map and vice versa.
        """
        return self.get_state(self.pos_player()[0] + x, self.pos_player()[1] + y) not in ["#", "*", "$"]

    def next(self, x, y):
        """
        @return: the state of the future position of player (x, y).
        """
        return self.get_state(self.pos_player()[0] + x, self.pos_player()[1] + y)

    def can_push(self, x, y):
        """
        :return: TRUE if the box at position (x, y) can be pushed to next position.
        """
        return self.next(x, y) in ["*", "$"] and self.next(x + x, y + y) in [" ", "."]

    def move(self, x, y):
        """
        The modules required to carry out game logic moving player and pushing boxes
        """
        if self.can_move(x, y):
            cur = self.pos_player()
            next_pos = self.next(x, y)
            if cur[2] == "@" and next_pos == " ":
                self.set_state(cur[0] + x, cur[1] + y, "@")
                self.set_state(cur[0], cur[1], " ")
            elif cur[2] == "@" and next_pos == ".":
                self.set_state(cur[0] + x, cur[1] + y, "+")
                self.set_state(cur[0], cur[1], " ")
            elif cur[2] == "+" and next_pos == " ":
                self.set_state(cur[0] + x, cur[1] + y, "@")
                self.set_state(cur[0], cur[1], ".")
            elif cur[2] == "+" and next_pos == ".":
                self.set_state(cur[0] + x, cur[1] + y, "+")
                self.set_state(cur[0], cur[1], ".")
        elif self.can_push(x, y):
            cur = self.pos_player()
            next_pos = self.next(x, y)
            fur_box = self.next(x + x, y + y)
            if cur[2] == "@" and next_pos == "$" and fur_box == " ":
                self.move_box(cur[0] + x, cur[1] + y, x, y)
                self.set_state(cur[0], cur[1], " ")
                self.set_state(cur[0] + x, cur[1] + y, "@")
            elif cur[2] == "@" and next_pos == "$" and fur_box == ".":
                self.move_box(cur[0] + x, cur[1] + y, x, y)
                self.set_state(cur[0], cur[1], " ")
                self.set_state(cur[0] + x, cur[1] + y, "@")
            elif cur[2] == "@" and next_pos == "*" and fur_box == " ":
                self.move_box(cur[0] + x, cur[1] + y, x, y)
                self.set_state(cur[0], cur[1], " ")
                self.set_state(cur[0] + x, cur[1] + y, "+")
            elif cur[2] == "@" and next_pos == "*" and fur_box == ".":
                self.move_box(cur[0] + x, cur[1] + y, x, y)
                self.set_state(cur[0], cur[1], " ")
                self.set_state(cur[0] + x, cur[1] + y, "+")
            elif cur[2] == "+" and next_pos == "$" and fur_box == " ":
                self.move_box(cur[0] + x, cur[1] + y, x, y)
                self.set_state(cur[0], cur[1], ".")
                self.set_state(cur[0] + x, cur[1] + y, "@")
            elif cur[2] == "+" and next_pos == "$" and fur_box == ".":
                self.move_box(cur[0] + x, cur[1] + y, x, y)
                self.set_state(cur[0], cur[1], ".")
                self.set_state(cur[0] + x, cur[1] + y, "@")
                # ///
            elif cur[2] == "+" and next_pos == "*" and fur_box == " ":
                self.move_box(cur[0] + x, cur[1] + y, x, y)
                self.set_state(cur[0], cur[1], ".")
                self.set_state(cur[0] + x, cur[1] + y, "+")
            elif cur[2] == "+" and next_pos == "*" and fur_box == ".":
                self.move_box(cur[0] + x, cur[1] + y, x, y)
                self.set_state(cur[0], cur[1], ".")
                self.set_state(cur[0] + x, cur[1] + y, "+")

    def play_game(self):
        if self.flag == 0:
            self.flag = 1
            if type_algorithm == 0:
                Label(self, text="BREADTH FIRST SEARCH:", font=('Helvetica',), bg="#ffbd59").place(x=100, y=100)
            else:
                Label(self, text="A* SEARCH:", font=('Helvetica',), bg="#ffbd59").place(x=100, y=100)
            Label(self, text="Expanded Node: " + str(self.expanded_node), font=('Helvetica',), bg="#f3c94a").place(x=100,
                                                                                                                y=125)
            Label(self, text="Explored Node: " + str(self.explored_node), font=('Helvetica',), bg="#f3c94a").place(x=100,
                                                                                                                y=150)
            Label(self, text="STEPS: 0", font=('Helvetica', 30, "bold"), bg="#ffbd59").place(x=700, y=150)
            if self.path == ['Impossible']:
                self.controller.switch_frame(DoneFrame)
            else:
                for i in range(len(self.path)):
                    # print(self.search_path[i])
                    if self.path[i] == "L":
                        self.move(-1, 0)
                    if self.path[i] == "R":
                        self.move(1, 0)
                    if self.path[i] == "U":
                        self.move(0, -1)
                    if self.path[i] == "D":
                        self.move(0, 1)
                    self.canvas.delete("all")
                    self.draw_board()
                    time.sleep(.05)
                    self.canvas.update()
                    Label(self, text="STEPS: " + str(i), font=('Helvetica', 30, "bold"), bg="#ffbd59").place(x=700, y=150)
                global map
                map = self.map
            self.controller.switch_frame(DoneFrame)


class DoneFrame(ttk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        ttk.Frame.__init__(self, parent)
        self.canvas = Canvas(self, width=WD, height=HT)
        self.game_frame = PhotoImage(file="images/Play_frame.png")
        self.exit_button = PhotoImage(file="images/exit_button_1.png")
        self.home_button = PhotoImage(file="images//home_button_0.png")
        self.algorithm_button = PhotoImage(file="images/algorithm_button_1.png")
        self.level_button = PhotoImage(file="images/level_button_0.png")
        Button(self, image=self.exit_button, command=lambda: controller.destroy()).place(x=1000, y=700)
        Button(self, image=self.home_button, command=lambda: controller.switch_frame(StartFrame)).place(x=50, y=700)
        Button(self, image=self.algorithm_button, command=lambda: controller.switch_frame(AlgorithmFrame)).place(
            x=140, y=700)
        Button(self, image=self.level_button, command=lambda: controller.switch_frame(LevelFrame)).place(x=255, y=700)
        self.map = map
        self.expanded_node = controller.expanded_node
        self.explored_node = controller.explored_node
        self.path = controller.path
        # Load images for drawing game board
        self.floor = PhotoImage(file="images/floor.png")
        self.wall = PhotoImage(file="images/wall.png")
        self.player = PhotoImage(file="images/player.png")
        self.box = PhotoImage(file="images/box.png")
        self.dock = PhotoImage(file="images/dock.png")
        self.box_on_dock = PhotoImage(file="images/box_on_dock.png")
        self.player_on_dock = PhotoImage(file="images/player_on_dock.png")
        self.canvas.update()
        self.draw_board()
        self.canvas.pack()
        if type_algorithm == 0:
            Label(self, text="BREADTH FIRST SEARCH:", font=('Helvetica',), bg="#ffbd59").place(x=100, y=100)
        else:
            Label(self, text="A* SEARCH:", font=('Helvetica',), bg="#ffbd59").place(x=100, y=100)
        Label(self, text="Expanded Node: " + str(self.expanded_node), font=('Helvetica',), bg="#f3c94a").place(x=100,
                                                                                                            y=125)
        Label(self, text="Explored Node: " + str(self.explored_node), font=('Helvetica',), bg="#f3c94a").place(x=100,
                                                                                                            y=150)
        Label(self, text="STEPS: " + str(len(self.path)), font=('Helvetica', 30, "bold"), bg="#ffbd59").place(x=700, y=150)
        if self.path == ['Impossible']:
            Label(self, text="IMPOSSIBLE !", font=('Helvetica', 30, "bold"), bg="#ffbd59").place(x=500, y=150)
        Label(self, text="COMPLETE !", font=('Helvetica', 20, "bold"), bg="#ffbd59").place(x=300, y=150)

    def draw_board(self):
        """
        The modules required to draw required game based object on canvas
        """
        x = 350
        y = 210 + size
        flag = 0
        for row in self.map:
            flag = 0
            for char in row:
                if char != " ":
                    flag = 1
                if char == " " and flag == 1:  # floor
                    self.canvas.create_image(x, y, image=self.floor)
                elif char == "#":  # wall
                    self.canvas.create_image(x, y, image=self.wall)
                elif char == '@':  # player
                    self.canvas.create_image(x, y, image=self.player)
                elif char == '$':  # box
                    self.canvas.create_image(x, y, image=self.box)
                elif char == '.':  # dock
                    self.canvas.create_image(x, y, image=self.dock)
                elif char == '*':  # box on dock
                    self.canvas.create_image(x, y, image=self.box_on_dock)
                elif char == '+':  # player on dock
                    self.canvas.create_image(x, y, image=self.player_on_dock)
                x = x + size
            x = 350
            y = y + size


if __name__ == '__main__':
    game = Master()
    game.title("Sokoban Game")
    game.mainloop()
