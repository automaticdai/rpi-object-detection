#!/usr/bin/python3

# ------------------------------------------------------------------------------
# rpi-object-detection
# ------------------------------------------------------------------------------
# Detect any motion in the frame.
# ------------------------------------------------------------------------------
# automaticdai
# YF Robotics Labrotary
# Instagram: yfrobotics
# Twitter: @yfrobotics
# Website: https://yfrobotics.github.io/
# --------------------------------------------

import cv2
import time
import numpy as np

from picamera2 import Picamera2

MOTION_BLUR = True

cnt_frame = 0
fps = 0

# Initialize Picamera2 and configure the camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

def mse(image_a, image_b):
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    err = np.sum((image_a.astype("float") - image_b.astype("float")) ** 2)
    err /= float(image_a.shape[0] * image_a.shape[1])

    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err


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

        while True:
            # ----------------------------------------------------------------------
            # record start time
            start_time = time.time()
            # ----------------------------------------------------------------------
            # Read the frames from a camera
            frame_raw = picam2.capture_array()

            if MOTION_BLUR:
                # Denoise the frame
                frame = cv2.GaussianBlur(frame_raw, (3,3),0)
            else:
                frame = frame_raw

            # Convert to gray image
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Find edges
            edges = cv2.Canny(frame_gray,100,200)

            # Show the original and processed image
            cv2.imshow('gray', visualize_fps(frame_gray, fps))
            cv2.imshow('edge', visualize_fps(edges, fps))

            # Calculate MSE
            if cnt_frame > 0:
                if mse(frame_gray, frame_gray_p) > 100:
                    print('Frame{0}: Motion Detected!'.format(cnt_frame))

            # ----------------------------------------------------------------------
            # record end time
            end_time = time.time()

            # calculate FPS
            seconds = end_time - start_time
            fps = 1.0 / seconds
            print("Estimated fps:{0:0.1f}".format(fps));

            cnt_frame = cnt_frame + 1
            edges_p = edges
            frame_gray_p = frame_gray
            # ----------------------------------------------------------------------

            # if key pressed is 'Esc' then exit the loop
            if cv2.waitKey(1)== 27:
                break
    except Exception as e:
        print(e)
    finally:
        # Clean up and exit the program
        cv2.destroyAllWindows()
        picam2.close()
