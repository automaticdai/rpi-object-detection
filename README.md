# Raspberry Pi Object Detection
- [Raspberry Pi Object Detection](#raspberry-pi-object-detection)
  - [1. Introduction](#1-introduction)
  - [2. Dependency](#2-dependency)
    - [2.1. Packages requirement](#21-packages-requirement)
    - [2.2. Hardware Support](#22-hardware-support)
  - [3. Applications in this package](#3-applications-in-this-package)
    - [3.1. Camera Test](#31-camera-test)
    - [3.2. Motion Detection](#32-motion-detection)
    - [3.3. Object Tracking (color-based)](#33-object-tracking-color-based)
    - [3.4. Object Tracking (shape-based)](#34-object-tracking-shape-based)
    - [3.5. Object Tracking (feature-based)](#35-object-tracking-feature-based)
    - [3.6. Object Detection with TensorFlow](#36-object-detection-with-tensorflow)
  - [4. How to Run](#4-how-to-run)
    - [4.1. Install the environment on Raspberry Pi](#41-install-the-environment-on-raspberry-pi)
    - [4.2. Install TensorFlow Lite (optional)](#42-install-tensorflow-lite-optional)
    - [4.3. Run the Scripts](#43-run-the-scripts)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>

## 1. Introduction
Using a Raspberry Pi and a USB web camera for computer vision with OpenCV and TensorFlow Lite. The aim of this project is to provide you a starting point of using Pi & CV in your own projects.


## 2. Dependency
### 2.1. Packages requirement
This project is dependent on the following packages:
- Python > 3.5
- OpenCV-Python
- TensorFlow Lite (*optional*)

### 2.2. Hardware Support
- Raspberry 1 Model B, Raspberry Pi 2, Raspberry Pi Zero and Raspberry Pi 3/4 (preferable)
  - These will have very different performance. RPi 3/4 are preferable as they have powerful CPUs. 
- Any USB camera supported by Raspberry Pi  
  - To see a list of all supportive cameras, visit http://elinux.org/RPi_USB_Webcams
- The official camera module is **NOT** yet supported by this code, but you can modify the code to use it (Google Raspberry Pi Offical Camera with OpenCV). 
  - (*Todo*) In the future I will add support.
- Jetson Nano also passed the test.


## 3. Applications in this package
Currently the following applications are implemented:

1. Camera test
2. Motion detection
3. Object detection & tracking  based on color
4. (*Todo*) Object detection & tracking  based on shape
5. (*Todo*) Object detection & tracking based on features
6. (*Todo*) Object detection based on TensorFlow Lite

### 3.1. Camera Test
Test the RPi and OpenCV environment. You are expected to see a pop-up window that has video streams from your USB camera if everything is set up correctly.

![alt text](./doc/cv_camera_test.jpg)

### 3.2. Motion Detection
Detect object movements in the image and print a warning message if any movement is detected. This detection is based on the mean squared error (MSE) of the difference between two images.

### 3.3. Object Tracking (color-based)
Track an object based on its color (you can choose between green/red) and print its center position.
![alt text](./doc/cv_object_tracking.jpg)

### 3.4. Object Tracking (shape-based)
(ongoing) Detect and track round objects.

### 3.5. Object Tracking (feature-based)
(ongoing) Detect and track an object based on its feature. Sample images have to be provided.

### 3.6. Object Detection with TensorFlow
(ongoing) Use TensorFlow Lite to recognise objects. 


## 4. How to Run
### 4.1. Install the environment on Raspberry Pi
```
sudo apt-get install libopencv-dev
sudo apt-get install libatlas-base-dev
pip3 install virtualenv Pillow numpy scipy
pip3 install opencv-python
```

### 4.2. Install TensorFlow Lite (optional)
```
wget https://github.com/PINTO0309/Tensorflow-bin/raw/master/tensorflow-2.1.0-cp37-cp37m-linux_armv7l.whl
pip3 install --upgrade setuptools
pip3 install tensorflow-2.1.0-cp37-cp37m-linux_armv7l.whl
pip3 install -e .
```

### 4.3. Run the Scripts
Run scripts in the `/src` folder by: `python3 src/$FOLDER_NAME$/$SCRIPT_NAME$.py`

To stop the code, press the `ESC` key on your keyboard.
