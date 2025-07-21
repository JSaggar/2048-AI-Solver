import cv2
import numpy as np
import pytesseract



pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load image
image = cv2.imread(r"C:\Users\Asus\source\repos\2048 Solver\2048 Solver\screenshot.jpg")
image = cv2.resize(image, (400, 400))  # optional

# Crop the grid (your working crop)
board_img = image[155:325, 40:365]

# Divide into 4x4 grid
tile_height = board_img.shape[0] // 4
tile_width = board_img.shape[1] // 4

tiles = []
for i in range(4):
    row = []
    for j in range(4):
        tile = board_img[i*tile_height:(i+1)*tile_height, j*tile_width:(j+1)*tile_width]
        row.append(tile)
    tiles.append(row)

# OCR to detect numbers
detected_board = []

for i in range(4):
    row = []
    for j in range(4):
        tile = tiles[i][j]

        # Preprocess tile for better OCR
        gray = cv2.cvtColor(tile, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

        # Use OCR to read number
        number_text = pytesseract.image_to_string(thresh, config='--psm 10 digits')

        try:
            number = int(number_text.strip())
        except:
            number = 0  # No number detected = empty tile

        row.append(number)
        print(f"Tile ({i},{j}) → {number}")
    detected_board.append(row)

# Final 4x4 board
board_array = np.array(detected_board)
print("\n✅ Extracted 2048 Board:")
print(board_array)

from ai_solver import best_move

move = best_move(board_array)
print(f"\n🤖 Best Move: {move.upper()}")
