# Raspberry Pi Object Detection

![](https://img.shields.io/github/stars/automaticdai/rpi-object-detection) ![](https://img.shields.io/github/forks/automaticdai/rpi-object-detection) ![](https://img.shields.io/github/license/automaticdai/rpi-object-detection)

- [Raspberry Pi Object Detection](#raspberry-pi-object-detection)
  - [1. Introduction](#1-introduction)
  - [2. Dependency](#2-dependency)
    - [2.1. Packages requirement](#21-packages-requirement)
    - [2.2. Hardware Support](#22-hardware-support)
  - [3. About this package](#3-about-this-package)
    - [3.1. Camera Test](#31-camera-test)
    - [3.2. Motion Detection](#32-motion-detection)
    - [3.3. Object Tracking (color-based)](#33-object-tracking-color-based)
    - [3.4. Object Tracking (shape-based)](#34-object-tracking-shape-based)
    - [3.5. Object Tracking (feature-based)](#35-object-tracking-feature-based)
    - [3.6. Object Detection using Neural Network (TensorFlow Lite)](#36-object-detection-using-neural-network-tensorflow-lite)
  - [4. How to Run](#4-how-to-run)
    - [4.1. Install the environment on Raspberry Pi](#41-install-the-environment-on-raspberry-pi)
    - [4.2. Install TensorFlow Lite (optional; only if you want to use neural network)](#42-install-tensorflow-lite-optional-only-if-you-want-to-use-neural-network)
    - [4.3. Run the scripts](#43-run-the-scripts)
    - [4.4. Change camera resolution](#44-change-camera-resolution)
  - [License](#license)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>

![rpi-logo](rpi-logo.png)

## 1. Introduction
Using a Raspberry Pi and a camera for computer vision (CV) with OpenCV and TensorFlow Lite. The aim of this project is to provide you a starting point of using Pi & CV in your own DIY/hacking projects.


## 2. Dependency
### 2.1. Packages requirement
This project is dependent on the following packages:
- Python > 3.5
- OpenCV-Python
- TensorFlow Lite (*optional*)

### 2.2. Hardware Support
- Support Raspberry 1 Model B, Raspberry Pi 2, Raspberry Pi Zero and Raspberry Pi 3/4 (preferable)
  - Different boards will have very different performance: RPi 3/4 are preferable as they have more powerful CPUs. RPi 1/2 may be struggling and produce very low FPS. 
- Any USB camera supported by Raspberry Pi  
  - To see a list of all supportive cameras, visit http://elinux.org/RPi_USB_Webcams
- The official camera module is **NOT** yet supported by this code, but you can modify the code to use it (Google Raspberry Pi Offical Camera with OpenCV). 
  - (*Todo*) I will add support in the future.
- Jetson Nano also passed the test.


## 3. About this package
Currently the following applications are implemented:

1. Camera test
2. Motion detection
3. Object detection & tracking  based on color
4. (*Todo*) Object detection & tracking  based on shape
5. (*Todo*) Object detection & tracking based on features
6. (*Todo*) Object detection using Neural Network (TensorFlow Lite)

### 3.1. Camera Test
Test the RPi and OpenCV environment. You are expected to see a pop-up window that has video streams from your USB camera if everything is set up correctly. If the window does not appear, you need to check both of (1) your environment; (2) camera connection.

![alt text](./images/cv_camera_test.png)

### 3.2. Motion Detection
Detect object movements in the image and print a warning message if any movement is detected. This detection is based on the mean squared error (MSE) of the difference between two images.

![alt text](./images/cv_motion_detection.png)

### 3.3. Object Tracking (color-based)
Track an object based on its color in HSV (you can choose your own color by clicking on the object of interest; click multiple times on different points to have a full color coverage) and print its center position. The following demo shows how I track a Nintendo game controller in real-time:

![alt text](./images/cv_object_tracking_color.png)

### 3.4. Object Tracking (shape-based)
(ongoing) Detect and track round objects.

### 3.5. Object Tracking (feature-based)
(ongoing) Detect and track an object based on its feature. Sample images have to be provided.

### 3.6. Object Detection using Neural Network (TensorFlow Lite)
(ongoing) Use TensorFlow Lite to recognise objects. 


## 4. How to Run
### 4.1. Install the environment on Raspberry Pi
```
sudo apt-get install libopencv-dev
sudo apt-get install libatlas-base-dev
pip3 install virtualenv Pillow numpy scipy
pip3 install opencv-python
```

### 4.2. Install TensorFlow Lite (optional; only if you want to use neural network)
```
wget https://github.com/PINTO0309/Tensorflow-bin/raw/master/tensorflow-2.1.0-cp37-cp37m-linux_armv7l.whl
pip3 install --upgrade setuptools
pip3 install tensorflow-2.1.0-cp37-cp37m-linux_armv7l.whl
pip3 install -e .
```

### 4.3. Run the scripts
Run scripts in the `/src` folder by: `python3 src/$FOLDER_NAME$/$SCRIPT_NAME$.py`

To stop the code, press the `ESC` key on your keyboard.

### 4.4. Change camera resolution
Changing the resolution will siginicantly impact the FPS. By default it is set to be `320 x 240`, but you can change it to any value that your camera supports at the beginning of each source code (`IMAGE_WIDTH` and `IMAGE_HEIGHT`).


## License
© This source code is licensed under the [MIT License](LICENSE).