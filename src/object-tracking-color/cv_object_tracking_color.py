#!/usr/bin/python3

# ------------------------------------------------------------------------------
# rpi-object-detection
# ------------------------------------------------------------------------------
# This is a blob detection program which intend to find the biggest blob
# in a given picture taken by a camera and return its central position.
#
# Key Steps:
# 1. Image Filtering
# 2. Image Segmentation
# 3. Detect Blobs
# 4. Filter Blobs using a criteria
# 5. Track Blobs
# ------------------------------------------------------------------------------
# automaticdai
# YF Robotics Labrotary
# Instagram: yfrobotics
# Twitter: @yfrobotics
# Website: https://yfrobotics.github.io/
# ------------------------------------------------------------------------------

import os
import sys
import cv2
import time
import numpy as np
import time
import math

# Add src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.picamera_utils import is_raspberry_camera, get_picamera

CAMERA_DEVICE_ID = 0
IMAGE_WIDTH = 320
IMAGE_HEIGHT = 240
IS_RASPI_CAMERA = is_raspberry_camera()

fps = 0
hsv_min = np.array((50, 80, 80))
hsv_max = np.array((120, 255, 255))

colors = []

print("Using raspi camera: ", IS_RASPI_CAMERA)

def isset(v):
    try:
        type (eval(v))
    except:
        return 0
    else:
        return 1


def on_mouse_click(event, x, y, flags, frame):
    global colors

    if event == cv2.EVENT_LBUTTONUP:
        color_bgr = frame[y, x]
        color_rgb = tuple(reversed(color_bgr))
        #frame[y,x].tolist()

        print(color_rgb)

        color_hsv = rgb2hsv(color_rgb[0], color_rgb[1], color_rgb[2])
        print(color_hsv)

        colors.append(color_hsv)

        print(colors)


# R, G, B values are [0, 255].
# Normally H value is [0, 359]. S, V values are [0, 1].
# However in opencv, H is [0,179], S, V values are [0, 255].
# Reference: https://docs.opencv.org/3.4/de/d25/imgproc_color_conversions.html
def hsv2rgb(h, s, v):
    h = float(h) * 2
    s = float(s) / 255
    v = float(v) / 255
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0: r, g, b = v, t, p
    elif hi == 1: r, g, b = q, v, p
    elif hi == 2: r, g, b = p, v, t
    elif hi == 3: r, g, b = p, q, v
    elif hi == 4: r, g, b = t, p, v
    elif hi == 5: r, g, b = v, p, q
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return (r, g, b)


def rgb2hsv(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = df/mx
    v = mx

    h = int(h / 2)
    s = int(s * 255)
    v = int(v * 255)

    return (h, s, v)


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

            # Convert the image to hsv space and find range of colors
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            cv2.namedWindow('frame')
            cv2.setMouseCallback('frame', on_mouse_click, frame)

            # Uncomment this for RED tag
            # thresh = cv2.inRange(hsv,np.array((120, 80, 80)), np.array((180, 255, 255)))

            # find the color using a color threshhold
            if colors:
                # find max & min h, s, v
                minh = min(c[0] for c in colors)
                mins = min(c[1] for c in colors)
                minv = min(c[2] for c in colors)
                maxh = max(c[0] for c in colors)
                maxs = max(c[1] for c in colors)
                maxv = max(c[2] for c in colors)

                print("New HSV threshold: ", (minh, mins, minv), (maxh, maxs, maxv))
                hsv_min = np.array((minh, mins, minv))
                hsv_max = np.array((maxh, maxs, maxv))

            thresh = cv2.inRange(hsv, hsv_min, hsv_max)
            thresh2 = thresh.copy()

            # find contours in the threshold image
            (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
            #print(major_ver, minor_ver, subminor_ver)

            # findContours() has different form for opencv2 and opencv3
            if major_ver == "2" or major_ver == "3":
                _, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            else:
                contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            # finding contour with maximum area and store it as best_cnt
            max_area = 0
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > max_area:
                    max_area = area
                    best_cnt = cnt

            # finding centroids of best_cnt and draw a circle there
            if isset('best_cnt'):
                M = cv2.moments(best_cnt)
                cx,cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
                cv2.circle(frame,(cx,cy),5,255,-1)
                print("Central pos: (%d, %d)" % (cx,cy))
            else:
                print("[Warning]Tag lost...")

            # Show the original and processed image
            #res = cv2.bitwise_and(frame, frame, mask=thresh2)
            cv2.imshow('frame', visualize_fps(frame, fps))
            cv2.imshow('thresh', visualize_fps(thresh2, fps))
            # ----------------------------------------------------------------------
            # record end time
            end_time = time.time()
            # calculate FPS
            seconds = end_time - start_time
            fps = 1.0 / seconds
            print("Estimated fps:{0:0.1f}".format(fps));
            # if key pressed is 'Esc' then exit the loop
            if cv2.waitKey(33) == 27:
                break
    except Exception as e:
        print(e)
    finally:
        # Clean up and exit the program
        cv2.destroyAllWindows()
        cap.close() if IS_RASPI_CAMERA else cap.release()
