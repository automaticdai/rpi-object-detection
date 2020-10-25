"""
Display the image captured from the camera. Used as a test program to verify if OpenCV has been properly installed.

<Author>
Xiaotian Dai
YunFei Robotics Labrotary
Website: http://www.yfrl.org
</Author>
"""

import cv2

CAMERA_DEVICE_ID = 0


if __name__=="__main__":
    try:
        # create video capture
        cap = cv2.VideoCapture(CAMERA_DEVICE_ID)

        # Loop to continuously get images
        while True:
            # Read the frames from a camera
            _, frame = cap.read()

            # show image
            cv2.imshow('frame', frame)

            # if key pressed is 'Esc' then exit the loop
            if cv2.waitKey(33) == 27:
                break
    except:
        pass
    finally:
        # Clean up and exit the program
        cv2.destroyAllWindows()
        cap.release()
