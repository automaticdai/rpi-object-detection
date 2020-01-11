# Raspberry Pi Object Detection

Use a Raspberry Pi and a USB web camera for computer vision with OpenCV and TensorFlow Lite. This project aims to provide a starting point of using Pi & CV in your own projects.


## Package Dependency
This project is dependent on the following packages:
- Python 3.5, 3.6, 3.7
- OpenCV-Python
- TensorFlow Lite


## Hardware Support
- Raspberry 1 Model B, Raspberry Pi 2, Raspberry Pi Zero and Raspberry Pi 3/4 (preferable)  
- Any USB camera supported by Raspberry Pi  
  - To see a list of all supportive cameras, visit http://elinux.org/RPi_USB_Webcams
- The official camera module is **NOT** yet supported by this code, but you can modify the code to use it (Google Raspberry Pi Offical Camera with OpenCV). In the future I will add support.


## Applications
Currently the following applications are implemented:

### 1. Camera Test
Test the RPi and OpenCV environment. You are expected to see video streams from your USB camera if everything is set right.

![alt text](./doc/cv_camera_test.jpg)

### 2. Motion Detection
Detect object movements in the image and print a warning message if any movement is detected. This detection is based on the mean squared error (MSE) of the difference between two images.

### 3. Object Tracking (color-based)
Track an object based on its color (green/blue) and print its center position.
![alt text](./doc/cv_object_tracking.jpg)

### 4. Object Tracking (feature-based)
(unfinished) Track an object based on its feature. Sample images have to be provided.

### 5. Object Detection with TensorFlow
(unfinished) Use TensorFlow Lite to recognise objects. 


## How to Run
### 1. Install the environment on Raspberry Pi
```
$sudo apt-get install libopencv-dev python3-opencv
```

### 2. Install TensorFlow Lite
```
wget https://github.com/PINTO0309/Tensorflow-bin/raw/master/tensorflow-2.1.0-cp37-cp37m-linux_armv7l.whl
pip3 install --upgrade setuptools
pip3 install tensorflow-2.1.0-cp37-cp37m-linux_armv7l.whl
pip3 install -e .
```

### 3. Run Scripts
Run scripts in the `/src` folder: `$python3 script_name.py`

To stop, press the `ESC` key