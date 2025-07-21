# 2048 AI Solver with ADB Integration and Color-Based Recognition

This project implements an AI solver for the popular 2048 game, designed to play automatically on an Android device. It leverages ADB (Android Debug Bridge) for screen interaction and uses a robust color-based recognition system to read the game board, making it resilient to various visual challenges. The AI's decision-making is powered by an Expectimax algorithm with a custom heuristic.

## ✨ Features

* **Automated Gameplay**: Plays 2048 on a connected Android device.
* **ADB Integration**: Captures screenshots and performs swipe gestures via ADB commands.
* **Color-Based Tile Recognition**: Accurately identifies tile values (0, 2, 4, ..., 2048+) by analyzing their background colors, providing a highly robust alternative to traditional OCR.
* **Expectimax AI**: Employs an Expectimax search algorithm to make strategic moves, considering both player actions and the random nature of new tile spawns.
* **Custom Heuristic**: Utilizes a sophisticated evaluation function that prioritizes empty cells, tile monotonicity, smoothness, and keeping the highest tile in a corner.
* **Modular Design**: Separates game logic, AI decision-making, and autoplay/screen interaction into distinct Python files.

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

1.  **Python 3.x**:
    ```bash
    python --version
    ```
2.  **Required Python Libraries**:
    ```bash
    pip install numpy opencv-python
    ```
3.  **Android Debug Bridge (ADB)**:
    * Download the platform-tools from the [Android Developers website](https://developer.android.com/tools/releases/platform-tools).
    * Extract the downloaded ZIP file to a convenient location (e.g., `C:\platform-tools`).
    * **Crucially, add the `platform-tools` directory to your system's PATH environment variable**, or update the `ADB_PATH` variable in `autoplay1.2.py` to the full path of your `adb.exe` executable.
    * **Enable USB Debugging on your Android device**: Go to `Settings` > `About phone` > tap `Build number` 7 times. Then go to `Developer options` and enable `USB debugging`.
    * **Authorize your device**: Connect your device via USB. On your device, you should see a pop-up asking to "Allow USB debugging". Check "Always allow from this computer" and tap "Allow".
    * **Verify ADB connection**: In your terminal, run `adb devices`. Your device should be listed as `device`.

### Project Structure

* `ai_solver.py`: Contains the core AI logic, including the Expectimax algorithm and the board evaluation heuristic.
* `game_logic.py`: Implements the fundamental 2048 game mechanics (tile movement, merging).
* `autoplay1.2.py`: Handles screen capture, tile recognition (color-based), ADB commands, and orchestrates the AI's play.
* `color_calibration.py` (or similar name): A temporary script used to calibrate the `REFERENCE_COLORS`.

## 🎨 Color Calibration (Essential Step!)

The AI relies on recognizing tile colors. You **MUST** calibrate these colors for your specific device and 2048 game app, as colors can vary.

1.  **Run the Calibration Script**:
    Use the `color_calibration.py` script (or the relevant section of your `autoplay1.2.py` if you kept it integrated) to gather the average BGR values for each tile.

    ```bash
    python color_calibration.py
    ```

2.  **Follow On-Screen Instructions**:
    The script will guide you to:
    * Place specific board states on your Android device (empty, 2, 4, 8, etc.).
    * Capture screenshots.
    * For each tile displayed, you will manually input the number you see.
    * The script will print the average BGR color for that tile.

3.  **Populate `REFERENCE_COLORS`**:
    Once you've collected all necessary tile colors (0, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, and potentially higher), copy the generated `REFERENCE_COLORS` dictionary from the calibration script's output and paste it into your `autoplay1.2.py` file.

    **Example `REFERENCE_COLORS` (from your calibration):**
    ```python
    REFERENCE_COLORS = {
        0: [186, 194, 209],  # Empty tile
        2: [194, 210, 219],  # Tile '2'
        4: [148, 210, 221],  # Tile '4'
        8: [120, 187, 229],  # Tile '8'
        16: [109, 152, 232], # Tile '16'
        32: [115, 128, 230], # Tile '32'
        64: [226, 191, 134], # Tile '64'
        128: [217, 125, 229],# Tile '128'
        256: [102, 197, 135],# Tile '256'
        512: [192, 194, 70], # Tile '512'
        # Add 1024, 2048, etc. here once calibrated
    }
    ```

4.  **Adjust `COLOR_MATCH_THRESHOLD`**:
    In `autoplay1.2.py`, fine-tune `COLOR_MATCH_THRESHOLD`. This value determines the "leeway" for color matching.
    * If tiles are misidentified, try **lowering** the threshold (stricter match).
    * If tiles are consistently returned as '0' (unrecognized), try **increasing** the threshold (more leeway).

## 🎮 How to Run the AI

1.  **Ensure ADB is connected and authorized.**
2.  **Start the 2048 game on your Android device.**
3.  **Run the `autoplay1.2.py` script**:
    ```bash
    python autoplay1.2.py
    ```
4.  The AI will start capturing screenshots, reading the board, calculating the best move, and performing swipes.

## 🤖 AI Strategy Details

The AI employs an **Expectimax algorithm** to navigate the game's stochastic (random) nature.

* **Maximizing Player**: The AI chooses moves (Up, Down, Left, Right) to maximize the expected score.
* **Chance Nodes**: After each AI move, a new tile (2 or 4) appears randomly on an empty spot. The Expectimax algorithm averages the expected values of all possible new tile placements, weighted by their probabilities (90% for 2, 10% for 4).
* **Heuristic Evaluation**: The `evaluate_board` function assigns a score to each board state, considering:
    * **Empty Cells**: More empty cells provide more flexibility.
    * **Max Tile Position**: Rewards keeping the highest tile in a corner.
    * **Monotonicity**: Encourages tiles to be in increasing/decreasing order across rows/columns, promoting an organized board.
    * **Smoothness**: Penalizes large differences between adjacent tiles, facilitating merges.
    * **Sum of Tiles**: Rewards overall progress by summing tile values.
* **Search Depth (`MAX_DEPTH`)**: The AI looks `MAX_DEPTH` moves ahead (defaulting to 4 in `ai_solver.py`). Increasing this depth improves strategic foresight but significantly increases computation time.

## ⚠️ Troubleshooting

* **`adb.exe: device unauthorized`**: Re-enable USB debugging, revoke authorizations, then reconnect and allow the dialog on your phone.
* **`Image not loaded`**: Check ADB connection (`adb devices`), ensure your phone screen is on, and the 2048 app is in the foreground.
* **Incorrect Tile Reading (Color-Based)**:
    * **Recalibrate `REFERENCE_COLORS`**: Colors can vary slightly between devices or game versions. Recalibrate all tile values carefully.
    * **Adjust `COLOR_MATCH_THRESHOLD`**: Fine-tune this value in `autoplay1.2.py`.
    * **Verify `x1, x2, y1, y2` and `tile_w * 0.1` offsets**: Ensure your cropping accurately isolates the tile area without including borders or glare.
* **AI makes bad moves / Fills up quickly**:
    * **Increase `MAX_DEPTH` in `ai_solver.py`**: A deeper search allows more foresight. Be mindful of performance.
    * **Refine `evaluate_board` heuristic**: Experiment with the weights of different factors (empty cells, monotonicity, smoothness, corner max tile) in `ai_solver.py` to better reflect optimal 2048 strategy.

## 💡 Future Improvements

* **Dynamic Thresholding for Color Matching**: Instead of a fixed `COLOR_MATCH_THRESHOLD`, use a percentage difference or adapt it based on tile value.
* **Advanced Heuristics**: Implement more complex heuristics, such as snake patterns, or use machine learning to learn optimal weights.
* **Performance Optimization**:
    * Implement **Memoization/Transposition Tables** in the Expectimax algorithm to cache evaluated board states, significantly speeding up deeper searches.
    * Implement **Iterative Deepening** for Expectimax to ensure a move is always made within a time limit.
* **Game Over Detection**: Implement robust detection for the "Game Over" screen to automatically restart or stop.
* **GUI/Visualizer**: Create a simple GUI to visualize the AI's thought process or the current board state without relying on `cv2.imshow` windows.
