import os
import time
import numpy as np
import pytesseract
import cv2
from ai_solver import best_move

# Path to ADB executable
ADB_PATH = r"C:\\platform-tools\\adb.exe"

# Tesseract config
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# ADB swipe coordinates
SWIPES = {
    'up':    (500, 1200, 500, 400),
    'down':  (500, 400, 500, 1200),
    'left':  (700, 800, 200, 800),
    'right': (200, 800, 700, 800),
}

def swipe(direction):
    if direction not in SWIPES:
        print(f"❌ Invalid direction: {direction}")
        return

    x1, y1, x2, y2 = SWIPES[direction]
    cmd = f'"{ADB_PATH}" shell input swipe {x1} {y1} {x2} {y2} 100'
    result = os.system(cmd)

    if result == 0:
        print(f"✅ Swiped {direction.upper()}")
    else:
        print(f"❌ Failed to swipe {direction.upper()} — check ADB path or connection.")

VALID_TILES = np.array([0, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048])

def closest_valid_tile(val):
    if val in VALID_TILES:
        return val
    else:
        diffs = np.abs(VALID_TILES - val)
        return VALID_TILES[np.argmin(diffs)]

def extract_board_from_image(image_path):
    image = cv2.imread(image_path)
    # image = cv2.resize(image, (400, 400))  # optional debug step
    board_img = image[155:325, 40:365]  # OLD crop size

    tile_height = board_img.shape[0] // 4
    tile_width = board_img.shape[1] // 4

    board = []
    for i in range(4):
        row = []
        for j in range(4):
            tile = board_img[i*tile_height:(i+1)*tile_height, j*tile_width:(j+1)*tile_width]
            cv2.imwrite(f"tile_{i}_{j}.png", tile)  # save cropped tiles for debug
            gray = cv2.cvtColor(tile, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
            text = pytesseract.image_to_string(thresh, config='--psm 10 digits')
            try:
                num = int(text.strip())
                num = closest_valid_tile(num)
            except:
                num = 0
            print(f"Tile ({i},{j}) → OCR='{text.strip()}' → {num}")
            row.append(num)
        board.append(row)

    return np.array(board)

# === Auto-play loop ===
while True:
    print("\n📸 Capturing screenshot...")
    os.system(f'"{ADB_PATH}" shell screencap -p /sdcard/screen2048.png')
    os.system(f'"{ADB_PATH}" pull /sdcard/screen2048.png screen2048.png')

    board = extract_board_from_image("screen2048.png")
    print("🧠 Extracted Board:")
    print(board)

    move = best_move(board)
    if move:
        print(f"🤖 Best Move: {move.upper()}")
        swipe(move)
    else:
        print("❌ No valid moves. Stopping.")
        break

    time.sleep(1.5)
