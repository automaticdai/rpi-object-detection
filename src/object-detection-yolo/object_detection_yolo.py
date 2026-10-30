# ------------------------------------------------------------------------------
# rpi-object-detection
# ------------------------------------------------------------------------------
# Use Ultralytics YOLO to detect objects in a video stream
# ------------------------------------------------------------------------------
# automaticdai
# YF Robotics Laboratory
# Instagram: yfrobotics
# Twitter: @yfrobotics
# Website: https://yfrobotics.github.io/
# ------------------------------------------------------------------------------
# References:
# - https://docs.ultralytics.com/guides/raspberry-pi/
# ------------------------------------------------------------------------------

import os
import sys
import cv2
from ultralytics import YOLO

# Add src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.picamera_utils import is_raspberry_camera, get_picamera
from utils.camera_utils import open_camera

CAMERA_DEVICE_ID = 0
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480
IS_RASPI_CAMERA = is_raspberry_camera()

print("Using raspi camera: ", IS_RASPI_CAMERA)

def main():
    # Load a YOLO11n PyTorch model
    model = YOLO("yolo11n.pt")

    # Open default camera
    if IS_RASPI_CAMERA:
        cap = get_picamera(IMAGE_WIDTH, IMAGE_HEIGHT)
        cap.start()
    else:
        cap = open_camera(CAMERA_DEVICE_ID, IMAGE_WIDTH, IMAGE_HEIGHT)
        if not cap.isOpened():
            print("Error: Could not open video stream.")
            return

    while True:
        if IS_RASPI_CAMERA:
            # picamera2 returns 4-channel XRGB frames, YOLO expects 3-channel BGR
            frame = cv2.cvtColor(cap.capture_array(), cv2.COLOR_BGRA2BGR)
        else:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to grab frame.")
                break

        # Run YOLO inference on the frame
        results = model(frame)

        # Draw results on the frame
        annotated_frame = results[0].plot()

        # Show the frame
        cv2.imshow("YOLOv11 Object Detection", annotated_frame)

        # Exit on 'q' or ESC key
        key = cv2.waitKey(1)
        if key == 27 or key == ord('q'):
            break

    cap.close() if IS_RASPI_CAMERA else cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
