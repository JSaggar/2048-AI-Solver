import cv2
import numpy as np
import os

# Your cropping and ADB paths
x1, x2 = 90, 1350
y1, y2 = 1205, 2550
ROWS, COLS = 4, 4
ADB_PATH = r'C:\platform-tools\adb'

def capture_board_image():
    os.system(f'"{ADB_PATH}" shell screencap -p /sdcard/screen2048.png')
    os.system(f'"{ADB_PATH}" pull /sdcard/screen2048.png')
    img = cv2.imread("screen2048.png")
    if img is None:
        print("❌ Image not loaded.")
    return img

def extract_tiles(cropped_img):
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
    mean_bgr = np.mean(tile_img, axis=(0, 1))
    return [int(c) for c in mean_bgr]

calibrated_colors = {}

print("--- Starting Color Calibration (Tile-by-Tile) ---")
print("Instructions:")
print("1. Start a 2048 game and get a board state with various numbers (2, 4, 8, etc.).")
print("2. Press Enter when prompted to capture the screen.")
print("3. For each displayed tile, observe the number on it (or if it's empty).")
print("4. Input that number (e.g., '2', '4', '0' for empty) in the console and press Enter.")
print("5. Repeat this for all tiles. You'll need to do this for multiple screenshots to capture all numbers (e.g., 128, 256, etc.).")
print("6. The script will print the 'REFERENCE_COLORS' dictionary at the end.")
print("-" * 50)

while True:
    input("\nPress Enter to capture a new screenshot for calibration (or Ctrl+C to quit)...")
    img = capture_board_image()
    
    if img is None:
        print("Could not capture image. Please ensure ADB is authorized and device screen is on.")
        continue

    print("Image captured. Processing tiles...")
    cropped = img[y1:y2, x1:x2]
    tiles = extract_tiles(cropped)

    for r in range(ROWS):
        for c in range(COLS):
            tile_image = tiles[r][c]
            avg_color = calculate_average_color(tile_image)

            # Display the tile for visual inspection
            cv2.imshow(f"Tile ({r},{c})", tile_image)
            # IMPORTANT: Wait for a key press on the *OpenCV window itself*
            # You must click on the OpenCV window and press ANY key to close it.
            print(f"\nTile ({r},{c}): Average Color (BGR): {avg_color}")
            print(f"Look at the 'Tile ({r},{c})' window. Press any key on that window to close it and enter the number.")
            cv2.waitKey(0) # Wait indefinitely until a key is pressed on the imshow window
            cv2.destroyAllWindows() # Close the window after key press

            while True:
                try:
                    num_input = input(f"What number is on Tile ({r},{c})? (Enter '0' for empty): ")
                    num_val = int(num_input.strip())
                    if num_val >= 0 and (num_val == 0 or num_val in [2**i for i in range(1, 13)]): # Check for powers of 2 (up to 4096)
                        break
                    else:
                        print("Invalid input. Please enter 0 or a power of 2 (2, 4, 8, ...).")
                except ValueError:
                    print("Invalid input. Please enter a number.")
            
            if num_val not in calibrated_colors:
                calibrated_colors[num_val] = avg_color
                print(f"Added color for {num_val}: {avg_color}")
            else:
                current_ref_color = np.array(calibrated_colors[num_val])
                new_avg_color = np.array(avg_color)
                if np.linalg.norm(current_ref_color - new_avg_color) > 10: # Threshold for "significant difference"
                     print(f"Note: Already have color for {num_val}. New sample {avg_color} is different from stored {calibrated_colors[num_val]}.")
                     # You could add logic here to average colors or choose the new one if desired
                
    print("\nCurrent calibrated colors:")
    print(calibrated_colors)
    print("\nCapture more screenshots to get all tile types (e.g., 128, 256, 512, etc.).")
    print("When done, copy the final dictionary below into your main script.")

    sorted_colors = dict(sorted(calibrated_colors.items()))
    print("\nFINAL REFERENCE_COLORS = {")
    for val, color in sorted_colors.items():
        print(f"    {val}: {color},")
    print("}")
    print("\nCopy this dictionary to your main autoplay script.")