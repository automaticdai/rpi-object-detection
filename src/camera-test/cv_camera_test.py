# ------------------------------------------------------------------------------
# rpi-object-detection
# ------------------------------------------------------------------------------
# Display the image captured from the camera. Used as a test program to verify
# if OpenCV has been properly installed.
# ------------------------------------------------------------------------------
# automaticdai
# YF Robotics Laboratory
# Instagram: yfrobotics
# Twitter: @yfrobotics
# Website: https://yfrobotics.github.io/
# ------------------------------------------------------------------------------

import os
import sys
import cv2
import time
import numpy as np

# Add src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.picamera_utils import is_raspberry_camera, get_picamera
from utils.camera_utils import open_camera

CAMERA_DEVICE_ID = 0
IMAGE_WIDTH = 320
IMAGE_HEIGHT = 240
IS_RASPI_CAMERA = is_raspberry_camera()
fps = 0

print("Using raspi camera: ", IS_RASPI_CAMERA)

def visualize_fps(image, fps: int):
    if len(np.shape(image)) < 3:
        text_color = (255, 255, 255)  # white
    else:
        text_color = (0, 255, 0)  # green
    row_size = 20  # pixels
    left_margin = 24  # pixels

    font_size = 1
    font_thickness = 1

    # Draw the FPS counter
    fps_text = 'FPS = {:.1f}'.format(fps)
    text_location = (left_margin, row_size)
    cv2.putText(image, fps_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                font_size, text_color, font_thickness)

    return image

if __name__ == "__main__":
    try:
        if IS_RASPI_CAMERA:
            cap = get_picamera(IMAGE_WIDTH, IMAGE_HEIGHT)
            cap.start()
        else:
            # create video capture
            cap = open_camera(CAMERA_DEVICE_ID, IMAGE_WIDTH, IMAGE_HEIGHT)
            # set resolution to 320x240 to reduce latency
            cap.set(3, IMAGE_WIDTH)
            cap.set(4, IMAGE_HEIGHT)

        # Loop to continuously get images
        prev_time = time.time()
        while True:
            # ----------------------------------------------------------------------

            # Read the frames from a camera
            if IS_RASPI_CAMERA:
                frame = cap.capture_array()
            else:
                _, frame = cap.read()

            # show image
            cv2.imshow('frame', visualize_fps(frame, fps))

            # ----------------------------------------------------------------------
            # record end time
            end_time = time.time()

            # calculate FPS from the time between consecutive frames, so it
            # includes waiting for the camera and waitKey(), not just processing
            seconds = end_time - prev_time
            prev_time = end_time
            fps = 1.0 / seconds
            print("Estimated fps:{0:0.1f}".format(fps))

            # if key pressed is 'Esc' then exit the loop
            if cv2.waitKey(33) == 27:
                break
    finally:
        # Clean up and exit the program
        cv2.destroyAllWindows()
        cap.close() if IS_RASPI_CAMERA else cap.release()
