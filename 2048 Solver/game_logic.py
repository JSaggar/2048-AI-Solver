import numpy as np
import random
 
def move_left(board):
    new_board = []
    score = 0

    for row in board: 
        #Step 1: Remove all zeros
        tight = [i for i in row if i != 0]

        #merge adjacent equal numbers 
        merged = []
        skip = False
        for i in range (len(tight)):
            if skip:
                skip = False
                continue

            if i + 1 < len(tight) and tight[i] == tight[i+1]:
                merged.append(tight[i] * 2)
                score += tight[i] * 2
                skip = True
            else:
                merged.append(tight[i])

        #Step 3: Pad the row with zeros
        merged += [0] * (4 - len(merged))
        new_board.append(merged)

    return np.array(new_board), score

def move_right(board):
    # Flip the board horizontally → move left → flip back
    flipped = np.fliplr(board)
    moved, score = move_left(flipped)
    return np.fliplr(moved), score

def move_up(board):
    # Transpose (rotate) → move left → transpose back
    transposed = np.transpose(board)
    moved, score = move_left(transposed)
    return np.transpose(moved), score

def move_down(board):
    # Transpose + flip → move left → reverse both
    transposed = np.transpose(board)
    flipped = np.fliplr(transposed)
    moved, score = move_left(flipped)
    return np.transpose(np.fliplr(moved)), score

def spawn_random_tile(board):
    empty_cells = list(zip(*np.where(board == 0)))

    if not empty_cells:
        return board

    row, col = random.choice(empty_cells)
    board[row][col] = 4 if random.random() < 0.1 else 2
    return board