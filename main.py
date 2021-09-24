
# class Utility:
#     def __init__(self):



if __name__ == "__main__":
    with open('input.txt', 'r') as file:
        matrix = [list(line) for line in file]
    num_row, num_col = len(matrix), len(matrix[0]) - 1 #number of row and column of matrix
    box_pos, goal_pos, player_pos = [], [], []
    for i in range(num_row):
        for j in range(num_col):
            if matrix[i][j] == '.':
                goal_pos.append(list((i, j)))
            elif matrix[i][j] == '*':
                box_pos.append(list((i, j)))
                goal_pos.append(list((i, j)))
            elif matrix[i][j] == '$':
                box_pos.append(list((i, j)))
            elif matrix[i][j] == '@':
                player_pos.extend(list((i, j)))
            elif matrix[i][j] == '+':
                player_pos.extend(list((i, j)))
                goal_pos.append(list((i, j)))

