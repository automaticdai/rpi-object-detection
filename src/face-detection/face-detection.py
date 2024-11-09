#!/usr/bin/python3

# ------------------------------------------------------------------------------
# rpi-object-detection
# ------------------------------------------------------------------------------
# automaticdai
# YF Robotics Labrotary
# Instagram: yfrobotics
# Twitter: @yfrobotics
# Website: https://yfrobotics.github.io/
# ------------------------------------------------------------------------------
# Reference:
# - https://towardsdatascience.com/face-detection-in-2-minutes-using-opencv-python-90f89d7c0f81
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
base_dir = os.path.dirname(os.path.abspath(__file__))

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


# Load the cascade
face_cascade = cv2.CascadeClassifier(os.path.join(base_dir, 'haarcascade_frontalface_default.xml'))

# To capture video from webcam.
if IS_RASPI_CAMERA:
    cap = get_picamera(IMAGE_WIDTH, IMAGE_HEIGHT)
    cap.start()
else:
    # create video capture
    cap = cv2.VideoCapture(CAMERA_DEVICE_ID)
    # set resolution to 320x240 to reduce latency
    cap.set(3, IMAGE_WIDTH)
    cap.set(4, IMAGE_HEIGHT)
# To use a video file as input
# cap = cv2.VideoCapture('filename.mp4')

while True:
    # ----------------------------------------------------------------------
    # record start time
    start_time = time.time()
    # Read the frames from a camera
    if IS_RASPI_CAMERA:
        frame = cap.capture_array()
    else:
        _, frame = cap.read()
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Detect the faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    # Draw the rectangle around each face
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    # Display
    cv2.imshow('img', visualize_fps(frame, fps))
    # ----------------------------------------------------------------------
    # record end time
    end_time = time.time()
    # calculate FPS
    seconds = end_time - start_time
    fps = 1.0 / seconds
    print("Estimated fps:{0:0.1f}".format(fps))
    # Stop if escape key is pressed
    k = cv2.waitKey(30) & 0xff
    if k==27:
        break

# Release the VideoCapture object
cap.close() if IS_RASPI_CAMERA else cap.release()
