import os

import cv2


def is_jetson():
    """Check if we are running on an Nvidia Jetson board."""
    return os.path.exists('/etc/nv_tegra_release')


def is_jetson_csi_camera(device_id):
    """Check if /dev/video<device_id> is a Jetson CSI camera (e.g. IMX219).

    CSI cameras on Jetson output raw Bayer frames through V4L2, so OpenCV
    cannot read them directly and they must go through nvarguscamerasrc.
    """
    name_file = '/sys/class/video4linux/video{}/name'.format(device_id)
    if not is_jetson() or not os.path.exists(name_file):
        return False
    with open(name_file) as f:
        return f.read().startswith('vi-output')


def jetson_csi_pipeline(sensor_id, width, height, framerate=30):
    """GStreamer pipeline that reads a Jetson CSI camera and outputs BGR frames."""
    return ('nvarguscamerasrc sensor-id={} ! '
            'video/x-raw(memory:NVMM), width=1280, height=720, framerate={}/1 ! '
            'nvvidconv ! video/x-raw, width={}, height={}, format=BGRx ! '
            'videoconvert ! video/x-raw, format=BGR ! '
            'appsink drop=1 max-buffers=1').format(sensor_id, framerate, width, height)


def open_camera(device_id, width, height):
    """Open a camera with OpenCV.

    Uses a GStreamer pipeline for Jetson CSI cameras and plain V4L2 otherwise
    (USB webcams on any platform).
    """
    if is_jetson_csi_camera(device_id):
        return cv2.VideoCapture(jetson_csi_pipeline(device_id, width, height), cv2.CAP_GSTREAMER)
    return cv2.VideoCapture(device_id)
