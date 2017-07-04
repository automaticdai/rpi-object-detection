# pi-object-detection
Applications using RaspberryPI and OpenCV to detect objects with a USB camera.


## Software
This project is mainly based on the following packages:
- Python 2.7
- OpenCV 2.0
- ~~SimpleCV 1.3~~

## Hardware
- Raspberry 1 Model B,Raspberry Pi 2 or Raspberry Pi 3 (preferrable)  
- Any USB camera supported by Raspberry Pi  
	- Too see a list of all supportive cameras, visit http://elinux.org/RPi_USB_Webcams
- Official camera module is NOT supported for this code, but you can modify the code to use it (Google Raspberry Pi Offical Camera with OpenCV).


## Application Programs
1. Camera Test  
Test the RPi and OpenCV environment. You are expected to see stream from your usb camera.
![alt text][pic_camera_test]

2. Object Tracking  
Tracks an object (in the current version is any green object) and gets its central position!  
![alt text][pic_object_tracking]

3. Motion Detection  
Detect any movements in the house and take a snapshoot!


## How to Run
1. Install the environment on a Raspberry Pi:
	`$sudo apt-get install libopencv-dev python-opencv`

2. Run scripts in the `/src` folder



[pic_camera_test]: https://github.com/automaticdai/pi-object-detection/blob/master/doc/cv_camera_test.jpg
[pic_object_tracking]: https://github.com/automaticdai/pi-object-detection/blob/master/doc/cv_object_tracking.jpg