"""
<Description>
Display the image captured from the camera. Used as a test program to verify if
SimpleCV has been properly installed.

<Author>
Xiaotian Dai
YunFei Robotics Labrotary
htttp://www.yfworld.com

<Version>
V1.0, 2015 Dec 06

"""

from SimpleCV import *

# Initialize the camera
cam = Camera()
disp = Display()

# Loop to continuously get images
while disp.isNotDone():
	# Get Image from camera
	img = cam.getImage()

	# Draw the text "Hello World" on image
	img.drawText("YunFei Robotics Lab")

	# Show the image
	img.show()

	# quit if mouse clicked
	if disp.mouseLeft:
		break
