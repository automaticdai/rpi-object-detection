#!/usr/bin/python3

# ------------------------------------------------------------------------------
# rpi-object-detection
# ------------------------------------------------------------------------------
# Find geometric shaped objects in the image using houghCircles().
# ------------------------------------------------------------------------------
# automaticdai
# YF Robotics Labrotary
# Instagram: yfrobotics
# Twitter: @yfrobotics
# Website: https://yfrobotics.github.io/
# ------------------------------------------------------------------------------
# Reference:
# - https://www.pyimagesearch.com/2014/07/21/detecting-circles-images-using-opencv-hough-circles/
# ------------------------------------------------------------------------------

import os
import sys
import cv2
import time
import numpy as np
import time

# Add src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.picamera_utils import is_raspberry_camera, get_picamera

CAMERA_DEVICE_ID = 0
IMAGE_WIDTH = 320
IMAGE_HEIGHT = 240
IS_RASPI_CAMERA = is_raspberry_camera()
fps = 0
print("Using raspi camera: ", IS_RASPI_CAMERA)

def isset(v):
    try:
        type (eval(v))
    except:
        return 0
    else:
        return 1


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
        # create video capture
        if IS_RASPI_CAMERA:
            cap = get_picamera(IMAGE_WIDTH, IMAGE_HEIGHT)
            cap.start()
        else:
            # create video capture
            cap = cv2.VideoCapture(CAMERA_DEVICE_ID)
            # set resolution to 320x240 to reduce latency
            cap.set(3, IMAGE_WIDTH)
            cap.set(4, IMAGE_HEIGHT)

        while True:
            # ----------------------------------------------------------------------
            # record start time
            start_time = time.time()
            # Read the frames frome a camera
            if IS_RASPI_CAMERA:
                frame = cap.capture_array()
            else:
                _, frame = cap.read()

            frame = cv2.blur(frame,(3,3))

            # Or get it from a JPEG
            # frame = cv2.imread('frame0010.jpg', 1)

            # convert the image into gray color
            output = frame.copy()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # detect circles in the image
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 100)

            # ensure at least some circles were found
            if circles is not None:
                # convert the (x, y) coordinates and radius of the circles to integers
                circles = np.round(circles[0, :]).astype("int")
                # loop over the (x, y) coordinates and radius of the circles
                for (x, y, r) in circles:
                    # draw the circle in the output image, then draw a rectangle
                    # corresponding to the center of the circle
                    cv2.circle(output, (x, y), r, (0, 255, 0), 4)
                    cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

            # show the output image
            cv2.imshow('img', np.hstack([frame, output]))
            # cv2.imshow("frame", np.hstack([visualize_fps(frame, fps), visualize_fps(output, fps)]))
            # ----------------------------------------------------------------------
            # record end time
            end_time = time.time()
            # calculate FPS
            seconds = end_time - start_time
            fps = 1.0 / seconds
            print("Estimated fps:{0:0.1f}".format(fps))
            # if key pressed is 'Esc' then exit the loop
            if cv2.waitKey(33) == 27:
                break
    except Exception as e:
        print(e)
    finally:
        # Clean up and exit the program
        cv2.destroyAllWindows()
        cap.close() if IS_RASPI_CAMERA else cap.release()
