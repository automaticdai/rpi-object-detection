# ------------------------------------------------------------------------------
# rpi-object-detection
# ------------------------------------------------------------------------------
# Detect and track geometric shapes in the camera frame:
#   - Circles via cv2.HoughCircles()
#   - Triangles and rectangles via cv2.findContours() + cv2.approxPolyDP()
# ------------------------------------------------------------------------------
# automaticdai
# YF Robotics Laboratory
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

# Add src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.picamera_utils import is_raspberry_camera, get_picamera

CAMERA_DEVICE_ID = 0
IMAGE_WIDTH = 320
IMAGE_HEIGHT = 240
IS_RASPI_CAMERA = is_raspberry_camera()
fps = 0

# Contour-based polygon detection parameters.
MIN_CONTOUR_AREA = 500          # reject noise: contours with area below this are ignored
POLY_APPROX_EPSILON = 0.04      # approxPolyDP epsilon as a fraction of contour perimeter
CANNY_LOW = 50
CANNY_HIGH = 150

# BGR colors for each shape label.
SHAPE_COLORS = {
    "Triangle":  (0, 255, 255),   # yellow
    "Rectangle": (255, 0, 255),   # magenta
}

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

            # --- Circles via HoughCircles ---
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 100)
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                for (x, y, r) in circles:
                    cv2.circle(output, (x, y), r, (0, 255, 0), 4)
                    cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
                    cv2.putText(output, "Circle", (x - 20, y - r - 8),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # --- Triangles & rectangles via contour polygon approximation ---
            edges = cv2.Canny(gray, CANNY_LOW, CANNY_HIGH)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                if cv2.contourArea(cnt) < MIN_CONTOUR_AREA:
                    continue
                perimeter = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, POLY_APPROX_EPSILON * perimeter, True)
                vertices = len(approx)
                if vertices == 3:
                    label = "Triangle"
                elif vertices == 4:
                    label = "Rectangle"
                else:
                    continue
                color = SHAPE_COLORS[label]
                cv2.drawContours(output, [approx], -1, color, 2)
                m = cv2.moments(cnt)
                if m["m00"] != 0:
                    cx = int(m["m10"] / m["m00"])
                    cy = int(m["m01"] / m["m00"])
                    cv2.putText(output, label, (cx - 25, cy),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

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
    finally:
        # Clean up and exit the program
        cv2.destroyAllWindows()
        cap.close() if IS_RASPI_CAMERA else cap.release()
