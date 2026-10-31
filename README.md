# Raspberry Pi Real-Time Object Detection and Tracking

![](https://img.shields.io/github/stars/automaticdai/rpi-object-detection) ![](https://img.shields.io/github/forks/automaticdai/rpi-object-detection) ![](https://img.shields.io/github/license/automaticdai/rpi-object-detection)

![rpi-logo](./images/cover.png)

- [Raspberry Pi Real-Time Object Detection and Tracking](#raspberry-pi-real-time-object-detection-and-tracking)
  * [1. Introduction](#1-introduction)
  * [2. Dependency](#2-dependency)
    + [2.1. Packages requirement](#21-packages-requirement)
    + [2.2. Hardware support](#22-hardware-support)
    + [2.3. Camera support](#23-camera-support)
    + [2.4. Tested platforms](#24-tested-platforms)
  * [3. What's in this repository](#3-what-s-in-this-repository)
    + [3.1. Camera Test](#31-camera-test)
    + [3.2. Camera Streaming over HTTP](#32-camera-streaming-over-http)
    + [3.3. Motion Detection](#33-motion-detection)
    + [3.4. Color-based Object Detection and Tracking](#34-color-based-object-detection-and-tracking)
    + [3.5. Shape-based Object Detection and Tracking](#35-shape-based-object-detection-and-tracking)
    + [3.6. Feature-based Object Detection and Tracking (with ORB)](#36-feature-based-object-detection-and-tracking--with-orb-)
    + [3.7. Face Detection and Tracking](#37-face-detection-and-tracking)
    + [3.8. Object Detection using YOLO](#38-object-detection-using-yolo)
    + [3.9. Object Detection using TensorFlow Lite](#39-object-detection-using-neural-network-tensorflow-lite)
  * [4. How to Run](#4-how-to-run)
    + [4.1. Install the environment](#41-install-the-environment)
    + [4.2. Run the scripts](#42-run-the-scripts)
    + [4.3. Change camera resolution](#43-change-camera-resolution)
    + [4.4. Benchmark the frame rate](#44-benchmark-the-frame-rate)
  * [5. Q&A](#5-q-a)
  * [License](#license)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>



![rpi-logo](./images/rpi-logo.png)

## 1. Introduction
Using a Raspberry Pi and a camera module for computer vision with OpenCV, YOLO, and TensorFlow Lite. The aim of this project is to provide a starting point for using RPi & CV in your own DIY / maker projects. Computer vision based on cameras is very powerful and will bring your project to the next level. This allows you to track complicated objects that would otherwise not be possible with other types of sensors (infrared, ultrasonic, LiDAR, etc).

Note the code is based on Python and OpenCV meaning it is cross-platform. You can run this on other Linux-based platforms as well, e.g. x86/x64 PC, IPC, Jetson, Banana Pi, LattaPanda, BeagleBoard, etc.


## 2. Dependency
### 2.1. Packages requirement
This project is dependent on the following packages:
- Python >= 3.6.9 (tested with Python 3.12 and 3.13)
- OpenCV-Python
- OpenCV-Contrib-Python
- NumPy
- SciPy
- Matplotlib
- Ultralytics (with CPU-only PyTorch on Raspberry Pi)
- `ai-edge-litert` (optional, for the TensorFlow Lite example)

### 2.2. Hardware support
- Support Raspberry Pi 1 Model B, Raspberry Pi 2, Raspberry Pi Zero, and Raspberry Pi 3/4/5 (preferable)
  - Raspberry Pi 5 and Raspberry Pi 4 have been tested (on Compute Module 5 and Compute Module 4), see [2.4. Tested platforms](#24-tested-platforms).
  - Both Raspberry Pi OS and Ubuntu are supported.
  - Different boards will have very varied performances.
  - RPi 3/4/5 are preferable as they have more powerful CPUs;
  - RPi 1/2 may be struggling and produce very low FPS, in which case you can further reduce the camera resolution (160 x 120).
- Nvidia Jetson
  - Jetson Nano (A01) also passed the test.
  - Jetson Orin Nano should work as well.
  - Jetson has its own repo now: [jetson-object-detection](https://github.com/automaticdai/jetson-object-detection)

### 2.3. Camera support
- Any USB camera supported by Raspberry Pi
  - To see a list of all supportive cameras, visit http://elinux.org/RPi_USB_Webcams
- The official RPi camera module is supported through `Picamera2`.
  - All scripts use `Picamera2` automatically when it is installed (`sudo apt install python3-picamera2` on Raspberry Pi OS), and fall back to a USB camera otherwise.
  - On a Compute Module, the camera has to be declared in `/boot/firmware/config.txt`. For example, for a Camera Module v2 (IMX219) on the `CAM1` connector, set `camera_auto_detect=0` and add `dtoverlay=imx219,cam1`, then reboot. Use `ov5647` for Camera Module v1, `imx708` for v3, and `imx477` for the HQ camera. Run `rpicam-hello --list-cameras` to check that the camera is detected.
  - On Ubuntu, `python3-picamera2` is not available from the Ubuntu archive, so use a USB camera.
- CSI cameras on Nvidia Jetson (e.g. Raspberry Pi Camera Module v2 / IMX219 on Jetson Nano) are supported through GStreamer.
  - On Jetson, CSI cameras output raw Bayer frames through V4L2, so OpenCV cannot read them with a plain `cv2.VideoCapture(0)`. The scripts detect a Jetson CSI camera automatically and open it with an `nvarguscamerasrc` GStreamer pipeline instead (see `src/utils/camera_utils.py`). USB cameras on Jetson still use V4L2.
  - This needs the OpenCV that ships with JetPack, which is built with GStreamer. Do **not** `pip install opencv-python` on Jetson: the pip wheels have no GStreamer support and will shadow JetPack's OpenCV.
  - If the camera fails to open (e.g. `Failed to create CaptureSession`), restart the camera daemon: `sudo systemctl restart nvargus-daemon`.

### 2.4. Tested platforms
All the examples have been tested on the following setups:

| Board | OS | Python | Camera |
|---|---|---|---|
| Raspberry Pi Compute Module 5 (RPi 5) | Ubuntu 24.04 LTS | 3.12 | Sony PlayStation Eye (USB) |
| Raspberry Pi Compute Module 4 (RPi 4) | Raspberry Pi OS (Debian 13 trixie) | 3.13 | Camera Module v2.1 (IMX219) on `CAM1` |

Measured with the benchmark script (`python3 benchmark/benchmark_fps.py --headless`, 20 s per example after a 5 s warm-up, OpenCV 5.0). See [4.4. Benchmark the frame rate](#44-benchmark-the-frame-rate) to measure your own board.

**Processing FPS** shows how fast each board runs the example's processing, without the camera's frame rate limit (time per frame in brackets):

| Example | RPi 5 (CM5) | RPi 4 (CM4) |
|---|---|---|
| Motion Detection | 2312 FPS (0.4 ms) | 666 FPS (1.5 ms) |
| Color-based Tracking | 1569 FPS (0.6 ms) | 436 FPS (2.3 ms) |
| Shape-based Tracking | 514 FPS (1.9 ms) | 247 FPS (4.0 ms) |
| Feature-based Tracking (ORB) | 55.3 FPS (18.1 ms) | 25.0 FPS (39.9 ms) |
| Face Detection | 159 FPS (6.3 ms) | 84.4 FPS (11.8 ms) |
| TensorFlow Lite (EfficientDet-Lite0) | 35.5 FPS (28.2 ms) | 12.4 FPS (80.9 ms) |
| YOLO11n (Ultralytics, 640x480) | 2.1 FPS (466 ms) | 1.3 FPS (760 ms) |

**Camera FPS** is the frame rate you see when running the examples on the live camera:

| Example | RPi 5 (CM5) | RPi 4 (CM4) |
|---|---|---|
| Motion Detection | 30.0 FPS | 15.0 FPS |
| Color-based Tracking | 29.1 FPS | 15.0 FPS |
| Shape-based Tracking | 28.0 FPS | 15.0 FPS |
| Feature-based Tracking (ORB) | 30.0 FPS | 15.0 FPS |
| Face Detection | 26.6 FPS | 15.0 FPS |
| TensorFlow Lite (EfficientDet-Lite0) | 30.0 FPS | 11.5 FPS |
| YOLO11n (Ultralytics, 640x480) | 2.1 FPS | 0.8 FPS |

Most camera FPS results are limited by the camera, not the CPU. The PlayStation Eye on the RPi 5 runs at up to 30 FPS. The Camera Module v2 on the RPi 4 ran at 15 FPS because the room was dim (about 16 lux): in low light the camera's auto exposure lengthens each frame (here to 66 ms), which lowers its frame rate. In good light, or with the frame duration fixed through `Picamera2`'s `FrameDurationLimits` control, it runs at 30 FPS. Only TensorFlow Lite on the RPi 4 and YOLO on both boards are limited by the CPU.


## 3. What's in this repository
Currently, the following applications are implemented:

- `src/camera-test`: Test if the camera is working
- `src/camera-stream`: Stream the camera to a web browser
- `src/motion-detection`: Detect any motion in the frame
- `src/object-tracking-color`: Object detection & tracking based on color
- `src/object-tracking-shape`: Object detection & tracking based on shape
- `src/object-tracking-feature`: Object detection & tracking based on features using ORB
- `src/face-detection`: Face detection & tracking
- `src/object-detection-yolo`: Object detection using YOLO (RPi 3/4/5 only)
- `src/object-detection-tflite`: Object detection using TensorFlow Lite (RPi 3/4/5 only)


### 3.1. Camera Test
Test the RPi and OpenCV environment. You are expected to see a pop-up window that has video streams from your USB camera if everything is set up correctly. If the window does not appear, you need to check both of (1) your environment; (2) camera connection.

![alt text](./images/cv_camera_test.png)

### 3.2. Camera Streaming over HTTP
Stream the camera as MJPEG over HTTP, so you can watch it from any browser on the same network, without a display attached to the Pi. With the Raspberry Pi camera, frames are JPEG-encoded by the Pi's hardware encoder through `Picamera2`, so CPU usage stays low. With a USB camera, frames are read and JPEG-encoded with OpenCV.

```
python3 src/camera-stream/cv_camera_stream.py
```

Then open `http://<raspberry-pi-ip>:8000/` in a browser (the raw stream is at `/stream.mjpg`, which can also be opened in VLC). The script runs in the foreground by default. To keep it running in the background after you log out (like `nohup`), add `--nohup`:

```
python3 src/camera-stream/cv_camera_stream.py --nohup
```

It prints the process ID to stop it with (`kill <PID>`), and writes its output to `camera_stream.log` in the current directory. The resolution and port are set by `IMAGE_WIDTH`, `IMAGE_HEIGHT` and `PORT` at the top of the script. If a USB camera does not support the requested resolution, it uses the closest one it has, and the script prints the resolution it actually streams at. Tested at about 30 FPS with a Camera Module v2 (IMX219) on a Compute Module 4 at 1280 x 720, and with a PlayStation Eye USB camera on a Compute Module 5 at 640 x 480.

Like the other examples, the script uses the Raspberry Pi camera when `Picamera2` is installed and a camera is connected, and the USB camera otherwise. The Raspberry Pi camera does not need OpenCV. In the foreground, press `Ctrl+C` to stop it. The stream has no authentication, so anyone on your network can view it. Only one program can use the camera at a time, so stop the stream before running the other examples.

### 3.3. Motion Detection
Detect object movements in the camera frame and print a warning message when motion is sustained.

Pipeline: the current and previous frames are converted to grayscale, Gaussian-blurred to suppress sensor noise, then compared with a per-pixel `cv2.absdiff`. The resulting diff is thresholded, dilated, and passed through `cv2.findContours`; only connected regions with area ≥ `MIN_MOTION_AREA` count as motion, and a debounce (`MOTION_CONSECUTIVE_FRAMES`) rejects one-frame transients. All thresholds are constants at the top of the script, so you can trade sensitivity for false-positive rate without touching the loop.

![alt text](./images/cv_motion_detection.png)

### 3.4. Color-based Object Detection and Tracking
Track an object based on its color in HSV and print its center position. You can choose your own color by clicking on the object of interest. Click multiple times on different points so a full color space is covered. You can hard code the parameters so you don't need to pick them again for the next run. The following demo shows how I track a Nintendo game controller in real-time:

![alt text](./images/cv_object_tracking_color.png)

### 3.5. Shape-based Object Detection and Tracking
Detect and track geometric shapes in the frame:

- **Circles** via `cv2.HoughCircles()`
- **Triangles** and **rectangles** via contour approximation (`cv2.findContours()` + `cv2.approxPolyDP()`)

Contours below `MIN_CONTOUR_AREA` pixels are filtered out to reduce noise; the epsilon used for polygon approximation and the Canny edge thresholds are configurable at the top of the script.

![alt text](./images/cv_object_tracking_shape.png)

### 3.6. Feature-based Object Detection and Tracking (with ORB)
Detect and track an object using its feature. The algorithm I selected here is ORB (Oriented FAST and Rotated BRIEF) for its fast calculation speed to enable real-time detection. To use the example, please prepare an Arduino UNO board in hand (or replace the `simple.png`).

![alt text](./images/cv_orb.png)

### 3.7. Face Detection and Tracking
Detecting face using Harr Cascade detector.

![cv_face-detection](images/cv_face-detection.png)

### 3.8. Object Detection using YOLO
Use YOLO (You Only Look Once) for object detection.  
Note this code is based on Ultralytics YOLO. The instruction can be found at their website: [Quick Start Guide: Raspberry Pi with Ultralytics YOLO11](https://docs.ultralytics.com/guides/raspberry-pi/). Double check if you need to use it in a commercialised project! 

### 3.9. Object Detection using Neural Network (TensorFlow Lite)
Use TensorFlow Lite to recognise objects.

To use it, download the model and labels into the module directory:
```
cd src/object-detection-tflite

# COCO labels
wget https://raw.githubusercontent.com/google-coral/test_data/master/coco_labels.txt

# EfficientDet-Lite0 model (INT8 quantized, ~4MB, with built-in NMS post-processing)
wget -O efficientdet_lite0.tflite https://storage.googleapis.com/download.tensorflow.org/models/tflite/task_library/object_detection/rpi/lite-model_efficientdet_lite0_detection_metadata_1.tflite
```

Then install the TensorFlow Lite runtime and run:

```
pip install ai-edge-litert
python3 src/object-detection-tflite/object_detection_tflite.py
```

## 4. How to Run
### 4.1. Install the environment

Run the installation script. It creates a virtual environment under `./venv` and installs all Python dependencies from `requirements.txt`:

```
chmod +x install.sh
./install.sh
```

On Raspberry Pi, the venv is created with `--system-site-packages` so that `libcamera` and `picamera2` (installed in the system Python by Raspberry Pi OS) remain accessible from inside it. The script also installs the CPU-only build of PyTorch first, because the default PyPI build for ARM64 pulls in several GB of CUDA packages that a Raspberry Pi cannot use.

The face detection example uses the Haar cascade files from the `libopencv-dev` system package (installed by `install.sh`), since the OpenCV 5 pip wheels no longer ship them.

Activate the environment in your shell before running any of the scripts:

```
source venv/bin/activate
```

The TensorFlow Lite example (§3.9) has an extra optional dependency — install it into the same venv only if you plan to use it:

```
pip install ai-edge-litert
```

### 4.2. Run the scripts
Run scripts in the `/src` folder by:

```
python3 src/$FOLDER_NAME$/$SCRIPT_NAME$.py
```

To stop the code, press the `ESC` key on your keyboard.

### 4.3. Change camera resolution
Changing the resolution will significantly impact the FPS. By default it is set to be `320 x 240`, but you can change it to any value that your camera supports at the beginning of each source code (defined by `IMAGE_WIDTH` and `IMAGE_HEIGHT`). Typical resolutions are:

- 160 x 120
- 320 x 240
- 640 x 480 (480p)
- 1280 x 720 (720p)
- 1920 x 1080 (1080p: make sure your camera supports this high resolution.)

### 4.4. Benchmark the frame rate
`benchmark/benchmark_fps.py` runs each example for a fixed time and reports its average frame rate as a Markdown table. It counts the frames each example prints, skips a warm-up period (model loading, camera start-up), and stops each example before starting the next one.

```
python3 benchmark/benchmark_fps.py
```

Each example is measured in two ways:

- **Camera FPS**: the example runs as normal on the live camera. This is the frame rate you see in practice, but it can never exceed the camera's frame rate (often 30 FPS), and several examples also wait 30 ms per frame in `cv2.waitKey()`.
- **Processing FPS**: a short clip is recorded from the camera first, then fed to each example as fast as it can take frames, with no windows and no `waitKey()` delay. This shows how much processing headroom the board has, and the time per frame shows the cost of each algorithm. The examples' own code is not changed: the benchmark replaces the camera with the clip when it starts them.

See [2.4. Tested platforms](#24-tested-platforms) for results on the RPi 5 and RPi 4. Processing FPS does not include drawing the windows, which also takes time when a display is attached. Camera FPS also depends on the lighting, as many cameras lower their frame rate in low light.

Options:

- `--mode camera` / `--mode processing`: measure only one of the two (default: both).
- `--video clip.mp4`: use the first frames of a video file for processing FPS instead of recording from the camera, so no camera is needed with `--mode processing`.
- `--headless`: do not open any windows for camera FPS, so it can be run over SSH without a display. Frame timing is kept the same as with a display. (Processing FPS never opens windows.)
- `--only face yolo`: run only some of the examples (`motion-detection`, `color`, `shape`, `orb`, `face`, `tflite`, `yolo`).
- `--duration 20` / `--warmup 5`: seconds measured per example, and seconds skipped after its first frame.
- `--verbose`: show the output of each example.

The TensorFlow Lite example is skipped if its model and labels have not been downloaded (see [3.9](#39-object-detection-using-neural-network-tensorflow-lite)). The camera test (§3.1) and camera streaming (§3.2) examples are not included, as they do no processing.

## 5. Q&A
**Q: Does this support Nvidia Jetson?**  
A: Yes. I have tested with my Jetson Nano 4GB. Note that Jetson has its own repo now: [jetson-object-detection](https://github.com/automaticdai/jetson-object-detection).

**Q: Does this support the Raspberry Pi camera?**  
A: This is implemented in [issue [#16]](https://github.com/automaticdai/rpi-object-detection/pull/16).

**Q: Does this support Raspberry Pi 5?**  
A: Yes. All examples have been tested on a Raspberry Pi Compute Module 5, which uses the same processor as the Raspberry Pi 5. See [2.4. Tested platforms](#24-tested-platforms).

**Q: Can we run this project on Ubuntu?**  
A: Yes. All examples have been tested on Ubuntu 24.04 LTS on a Raspberry Pi Compute Module 5 with a USB camera. `picamera2` is not available from the Ubuntu archive, so use a USB camera on Ubuntu.

**Q: I am using virtual environment and get a message "no module called libcamera" issue**  
A: A simple solution would be [(Reference)](https://forums.raspberrypi.com/viewtopic.php?t=361758):  
`python3 -m venv --system-site-packages env`

Thanks [VgerTest](https://github.com/VgerTest) for [issue [#20]](https://github.com/automaticdai/rpi-object-detection/issues/20).

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=automaticdai/rpi-object-detection&type=date&legend=top-left)](https://www.star-history.com/#automaticdai/rpi-object-detection&type=date&legend=top-left)

## License
© This source code is licensed under the [MIT License](LICENSE).
