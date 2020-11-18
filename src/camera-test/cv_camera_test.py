"""
Display the image captured from the camera. Used as a test program to verify if OpenCV has been properly installed.

YunFei Robotics Labrotary
Twitter: @yfrobotics
Website: https://www.yfrl.org
"""

import cv2

CAMERA_DEVICE_ID = 0


if __name__ == "__main__":
    try:
        # create video capture
        cap = cv2.VideoCapture(CAMERA_DEVICE_ID, cv2.CAP_V4L)

        # set resolution to 320x240 to reduce latency 
        cap.set(3, 320)
        cap.set(4, 240)

        # Loop to continuously get images
        while True:
            # Read the frames from a camera
            _, frame = cap.read()

            # show image
            cv2.imshow('frame', frame)

            # if key pressed is 'Esc' then exit the loop
            if cv2.waitKey(33) == 27:
                break
    except Exception as e:
        print(e)
    finally:
        # Clean up and exit the program
        cv2.destroyAllWindows()
        cap.release()
