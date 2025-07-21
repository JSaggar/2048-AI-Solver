import cv2
import numpy as np
import os
import time
from ai_solver import best_move

# --- Your calibrated REFERENCE_COLORS dictionary ---
# IMPORTANT: This dictionary MUST be fully populated with ALL possible tile values (0, 2, 4, 8, ... up to 2048/4096)
# and their average BGR values calibrated from your specific game/device.
# The accuracy of this method relies entirely on having a complete and accurate set of reference colors.
REFERENCE_COLORS = {
    0: [186, 194, 209],  # Empty tile
    2: [194, 210, 219],  # Tile '2'
    4: [148, 210, 221],  # Example placeholder for '4'. YOU MUST CALIBRATE THIS if you haven't yet.
    8: [120, 187, 229],  # Tile '8'
    16: [109, 152, 232], # Tile '16'
    32: [115, 128, 230], # Tile '32'
    64: [226, 191, 134], # Tile '64'
    128: [217, 125, 229],# Tile '128'
    256: [102, 197, 135],# Tile '256'
    512: [192, 194, 70]
    # Add other tiles here as you calibrate them (e.g., 512, 1024, 2048, 4096)
    # Example: 512: [B_VAL, G_VAL, R_VAL],
}

# --- Color Distance Threshold ---
# This value defines how much "leeway" there is for a color match.
# Adjust this value based on your calibration tests.
# A smaller value means a stricter match; a larger value means more leeway.
# Start with 15-30 and adjust.
COLOR_MATCH_THRESHOLD = 25 # Example threshold for Euclidean distance

# --- Screen Cropping and ADB Configuration ---
x1 = 90
x2 = 1350
y1 = 1205
y2 = 2550
ROWS, COLS = 4, 4
ADB_PATH = r'C:\platform-tools\adb'

internal_board = np.zeros((ROWS, COLS), dtype=int)

def capture_board_image():
    """Captures a screenshot from the Android device and pulls it to the local machine."""
    os.system(f'"{ADB_PATH}" shell screencap -p /sdcard/screen2048.png')
    os.system(f'"{ADB_PATH}" pull /sdcard/screen2048.png')
    img = cv2.imread("screen2048.png")
    if img is None:
        print("❌ Image not loaded. Ensure ADB is connected, device screen is on, and 'screen2048.png' exists.")
    return img

def extract_tiles(cropped_img):
    """Divides the cropped 2048 board image into individual tile images."""
    tiles = []
    h, w = cropped_img.shape[:2]
    tile_h, tile_w = h // ROWS, w // COLS
    for row_idx in range(ROWS):
        row_tiles = []
        for col_idx in range(COLS):
            x_start = col_idx * tile_w + int(tile_w * 0.1)
            y_start = row_idx * tile_h + int(tile_h * 0.1)
            x_end = x_start + int(tile_w * 0.8)
            y_end = y_start + int(tile_h * 0.8)
            tile = cropped_img[y_start:y_end, x_start:x_end]
            row_tiles.append(tile)
        tiles.append(row_tiles)
    return tiles

def calculate_average_color(tile_img):
    """Calculates the average BGR color of a tile image, converted to int."""
    mean_bgr = np.mean(tile_img, axis=(0, 1))
    return [int(c) for c in mean_bgr]

def color_distance(color1, color2):
    """Calculates Euclidean distance between two BGR colors."""
    return np.sqrt(np.sum((np.array(color1) - np.array(color2))**2))

def read_tile_number(tile_img):
    """
    Identifies the tile number based on its average color by finding the closest match
    within a defined threshold.
    """
    current_color = calculate_average_color(tile_img)
    
    best_match_value = 0 # Default to 0 (empty tile) if no valid match found
    min_distance = float('inf')

    for value, ref_color in REFERENCE_COLORS.items():
        dist = color_distance(current_color, ref_color)
        if dist < min_distance:
            min_distance = dist
            best_match_value = value
            
    # Apply the leeway (threshold)
    if min_distance > COLOR_MATCH_THRESHOLD:
        # If the closest match is still too far, consider it an unrecognized tile
        print(f"⚠️ Warning: Unrecognized tile color {current_color} (closest was {best_match_value} at {min_distance}). Treating as 0.")
        return 0

    # print(f"Current tile color: {current_color} -> Best match: {best_match_value} (Distance: {min_distance})") # Debugging color matches
    return best_match_value

def read_board(img):
    """
    Reads the entire 2048 board from a screenshot image.
    """
    cropped = img[y1:y2, x1:x2]
    tiles = extract_tiles(cropped)
    board = np.zeros((ROWS, COLS), dtype=int)
    
    for r in range(ROWS):
        for c in range(COLS):
            tile_image = tiles[r][c]
            
            # --- Visual Debugging for Color Strategy (Optional) ---
            # Uncomment these lines to display each raw tile for visual verification
            # cv2.imshow(f"Tile ({r},{c})", tile_image)
            # cv2.waitKey(0) # Wait for key press on the image window
            # cv2.destroyAllWindows() # Close the window
            # ---------------------------------------------------
            
            num = read_tile_number(tile_image) # Use the new color-based function
            board[r, c] = num
            print(f"Tile ({r},{c}) → {num}")
    
    # These wait/destroy calls are for the overall board display.
    # If using tile-by-tile debugging above, they might be redundant or you can comment them out.
    # print("Press any key to close tile windows and continue...")
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
    return board

def swipe(direction):
    """Performs a swipe action on the Android device using ADB."""
    directions = {
        "UP": (500, 1700, 500, 1000),
        "DOWN": (500, 1000, 500, 1700),
        "LEFT": (800, 1400, 200, 1400),
        "RIGHT": (200, 1400, 800, 1400)
    }
    if direction in directions:
        x1_s, y1_s, x2_s, y2_s = directions[direction]
        os.system(f'"{ADB_PATH}" shell input swipe {x1_s} {y1_s} {x2_s} {y2_s} 200')
        print(f"✅ Swiped {direction}")
    else:
        print("❌ Invalid swipe direction.")

def main():
    """Main execution loop for the 2048 AI autoplay."""
    global internal_board

    print("\U0001F4F8 Capturing screenshot...")
    img = capture_board_image()
    if img is None:
        print("Stopping due to image capture failure.")
        return

    print("\U0001F9E0 Reading board from screen...")
    scanned_board = read_board(img)
    print("Scanned Board:")
    print(scanned_board)

    move = best_move(scanned_board)

    if move:
        move = move.upper()
        print(f"\U0001F916 Best Move: {move}")
        swipe(move)
        time.sleep(0.5)

        print("\U0001F4F8 Re-scanning board after move to update internal state...")
        img = capture_board_image()
        if img is None:
            print("Stopping due to post-move image capture failure.")
            return
        internal_board = read_board(img)
        print("Updated Internal Board (from screen):")
        print(internal_board)
    else:
        print("❌ No valid moves found by AI. Game likely over or stuck. Stopping.")

if __name__ == "__main__":
    internal_board = np.zeros((ROWS, COLS), dtype=int)
    print("Starting 2048 AI Autoplay...")
    while True:
        main()
        time.sleep(0)