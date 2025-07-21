import cv2
import os

ADB_PATH = r'C:\platform-tools\adb'
SCALE_PERCENT = 40  # Scale image down to fit screen

def capture_screenshot():
    print("📸 Capturing screenshot from phone...")
    os.system(f'"{ADB_PATH}" shell screencap -p /sdcard/screen2048.png')
    os.system(f'"{ADB_PATH}" pull /sdcard/screen2048.png')

def crop_image():
    original = cv2.imread("screen2048.png")
    if original is None:
        print("❌ Failed to load image.")
        return

    # Resize image for display
    scale = SCALE_PERCENT / 100.0
    resized = cv2.resize(original, (0, 0), fx=scale, fy=scale)

    cropping = False
    start_point = end_point = ()

    def mouse_crop(event, x, y, flags, param):
        nonlocal start_point, end_point, cropping, resized, original

        if event == cv2.EVENT_LBUTTONDOWN:
            start_point = (x, y)
            cropping = True

        elif event == cv2.EVENT_MOUSEMOVE and cropping:
            temp = resized.copy()
            cv2.rectangle(temp, start_point, (x, y), (0, 255, 0), 2)
            cv2.imshow("Crop Tool", temp)

        elif event == cv2.EVENT_LBUTTONUP:
            end_point = (x, y)
            cropping = False

            x1, y1 = sorted([start_point[0], end_point[0]])
            x2, y2 = sorted([start_point[1], end_point[1]])

            # Scale back to original coordinates
            x1_full, x2_full = int(x1 / scale), int(end_point[0] / scale)
            y1_full, y2_full = int(y1 / scale), int(end_point[1] / scale)

            print(f"\n✅ Crop Coordinates (original resolution):")
            print(f"x1 = {x1_full}, x2 = {x2_full}")
            print(f"y1 = {y1_full}, y2 = {y2_full}")

            # Optional: Show and save cropped area
            crop = original[y1_full:y2_full, x1_full:x2_full]
            cv2.imshow("Cropped", crop)
            cv2.imwrite("cropped_preview.png", crop)

    cv2.namedWindow("Crop Tool")
    cv2.setMouseCallback("Crop Tool", mouse_crop)
    cv2.imshow("Crop Tool", resized)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_screenshot()
    crop_image()
