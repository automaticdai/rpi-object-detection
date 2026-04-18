# ------------------------------------------------------------------------------
# rpi-object-detection
# ------------------------------------------------------------------------------
# Detect motion in the camera frame.
#
# Pipeline: grayscale + Gaussian blur, per-pixel absdiff against the previous
# blurred frame, threshold, dilate, and keep only contours whose area exceeds
# MIN_MOTION_AREA. A debounce requires MOTION_CONSECUTIVE_FRAMES consecutive
# motion frames before reporting, which rejects one-shot sensor noise and
# lighting wobble. Tunables at the top of the file.
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

CAMERA_DEVICE_ID = 0
IMAGE_WIDTH = 320
IMAGE_HEIGHT = 240
IS_RASPI_CAMERA = is_raspberry_camera()

# Motion-detection tuning. Raise BLUR_KERNEL / MIN_MOTION_AREA / MOTION_CONSECUTIVE_FRAMES
# to cut false positives further (at the cost of sensitivity to small / brief motion).
BLUR_KERNEL = (21, 21)
DIFF_THRESHOLD = 25
DILATE_ITERATIONS = 2
MIN_MOTION_AREA = 500
MOTION_CONSECUTIVE_FRAMES = 3

cnt_frame = 0
motion_streak = 0
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
            # ----------------------------------------------------------------------
            # Read the frames from a camera
            if IS_RASPI_CAMERA:
                frame_raw = cap.capture_array()
            else:
                _, frame_raw = cap.read()

            # Grayscale + blur. The blur kernel sets the minimum feature size
            # below which pixel differences are ignored — larger kernel means
            # sensor noise and compression artefacts are smoothed away before
            # they can trip the absdiff below.
            frame_gray = cv2.cvtColor(frame_raw, cv2.COLOR_BGR2GRAY)
            frame_blur = cv2.GaussianBlur(frame_gray, BLUR_KERNEL, 0)

            display = frame_raw.copy()
            thresh = None

            if cnt_frame > 0:
                diff = cv2.absdiff(frame_blur_p, frame_blur)
                _, thresh = cv2.threshold(diff, DIFF_THRESHOLD, 255, cv2.THRESH_BINARY)
                thresh = cv2.dilate(thresh, None, iterations=DILATE_ITERATIONS)

                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                motion_regions = [c for c in contours if cv2.contourArea(c) >= MIN_MOTION_AREA]
                for c in motion_regions:
                    x, y, w, h = cv2.boundingRect(c)
                    cv2.rectangle(display, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Debounce: require consecutive motion frames to reject
                # one-frame transients (brief lighting wobble, shutter noise).
                if motion_regions:
                    motion_streak += 1
                else:
                    motion_streak = 0
                if motion_streak >= MOTION_CONSECUTIVE_FRAMES:
                    print('Frame{0}: Motion Detected! ({1} region(s))'.format(
                        cnt_frame, len(motion_regions)))

            # Show the raw frame with bounding boxes, plus the threshold mask
            # to make tuning DIFF_THRESHOLD / MIN_MOTION_AREA easier.
            cv2.imshow('frame', visualize_fps(display, fps))
            if thresh is not None:
                cv2.imshow('thresh', visualize_fps(thresh, fps))

            # ----------------------------------------------------------------------
            # record end time
            end_time = time.time()

            # calculate FPS
            seconds = end_time - start_time
            fps = 1.0 / seconds
            print("Estimated fps:{0:0.1f}".format(fps))

            cnt_frame = cnt_frame + 1
            frame_blur_p = frame_blur
            # ----------------------------------------------------------------------

            # if key pressed is 'Esc' then exit the loop
            if cv2.waitKey(1)== 27:
                break
    finally:
        # Clean up and exit the program
        cv2.destroyAllWindows()
        cap.close() if IS_RASPI_CAMERA else cap.release()
