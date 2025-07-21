import numpy as np
import random
from game_logic import move_left, move_right, move_up, move_down, spawn_random_tile

def is_game_over(board):
    if np.any(board == 0):
        return False
    for move in [move_left, move_right, move_up, move_down]:
        moved, _ = move(board)
        if not np.array_equal(board, moved):
            return False
    return True

def print_board(board):
    print("\n2048 Board:")
    print(board)

# === Game Start ===
board = np.zeros((4, 4), dtype=int)
board = spawn_random_tile(board)
board = spawn_random_tile(board)

while True:
    print_board(board)

    if is_game_over(board):
        print("Game Over!")
        break

    move = input("Move (W/A/S/D): ").lower()
    old_board = board.copy()

    if move == 'a':
        board, score = move_left(board)
    elif move == 'd':
        board, score = move_right(board)
    elif move == 'w':
        board, score = move_up(board)
    elif move == 's':
        board, score = move_down(board)
    else:
        print("Invalid move! Use W (up), A (left), S (down), D (right).")
        continue

    if not np.array_equal(board, old_board):
        board = spawn_random_tile(board)
