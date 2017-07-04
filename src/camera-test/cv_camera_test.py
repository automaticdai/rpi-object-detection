"""
<Description>
Display the image captured from the camera. Used as a test program to verify if
SimpleCV has been properly installed.

<Author>
Xiaotian Dai
YunFei Robotics Labrotary
htttp://www.yfworld.com

<Version>
V1.1, 2017 July 04

"""

import cv2
import numpy as np

# create video capture
cap = cv2.VideoCapture(0)

# Loop to continuously get images
while(1):
    # Read the frames frome a camera
    _,frame = cap.read()

	# show image
	cv2.imshow('frame', frame)

    # if key pressed is 'Esc' then exit the loop
    if cv2.waitKey(33)== 27:
        break
    
# Clean up and exit the program
cv2.destroyAllWindows()
cap.release()
