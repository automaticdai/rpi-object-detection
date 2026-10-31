# ------------------------------------------------------------------------------
# rpi-object-detection
# ------------------------------------------------------------------------------
# Stream the camera as MJPEG over HTTP, so it can be viewed from any browser on
# the network at http://<raspberry-pi-ip>:8000/
# Uses the Raspberry Pi camera (hardware JPEG encoder) when Picamera2 is
# installed and a camera is connected, and a USB camera (via OpenCV) otherwise.
# Runs in the foreground by default (Ctrl+C to stop); use --nohup to keep it
# running in the background after you log out.
# ------------------------------------------------------------------------------
# automaticdai
# YF Robotics Laboratory
# Instagram: yfrobotics
# Twitter: @yfrobotics
# Website: https://yfrobotics.github.io/
# ------------------------------------------------------------------------------

import argparse
import io
import logging
import os
import socketserver
import subprocess
import sys
from http import server
from threading import Condition, Thread

# Add src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.picamera_utils import is_raspberry_camera

CAMERA_DEVICE_ID = 0
IMAGE_WIDTH = 1280
IMAGE_HEIGHT = 720
JPEG_QUALITY = 80   # USB camera only; the Raspberry Pi camera uses its encoder's default
PORT = 8000
LOG_FILE = "camera_stream.log"

PAGE = b"""<html><head><title>Raspberry Pi camera</title></head>
<body style="margin:0;background:#111;display:flex;justify-content:center;align-items:center;height:100vh">
<img src="stream.mjpg" style="max-width:100%;max-height:100%"/></body></html>"""


class StreamingOutput(io.BufferedIOBase):
    """Holds the latest JPEG frame and wakes up waiting clients."""

    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", len(PAGE))
            self.end_headers()
            self.wfile.write(PAGE)
        elif self.path == "/stream.mjpg":
            self.send_response(200)
            self.send_header("Cache-Control", "no-cache, private")
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=FRAME")
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b"--FRAME\r\n")
                    self.send_header("Content-Type", "image/jpeg")
                    self.send_header("Content-Length", len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b"\r\n")
            except Exception as e:
                logging.info("Client %s disconnected: %s", self.client_address, e)
        else:
            self.send_error(404)


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def has_raspberry_camera():
    """Check that Picamera2 is installed and a Raspberry Pi camera is connected."""
    if not is_raspberry_camera():
        return False
    from picamera2 import Picamera2
    return len(Picamera2.global_camera_info()) > 0


def stream_raspberry_camera(output):
    """Start the Raspberry Pi camera, JPEG-encoded in hardware. Returns a stop function."""
    from picamera2 import Picamera2
    from picamera2.encoders import MJPEGEncoder
    from picamera2.outputs import FileOutput

    picam2 = Picamera2()
    picam2.configure(picam2.create_video_configuration(main={"size": (IMAGE_WIDTH, IMAGE_HEIGHT)}))
    picam2.start_recording(MJPEGEncoder(), FileOutput(output))
    print(f"Using the Raspberry Pi camera at {IMAGE_WIDTH}x{IMAGE_HEIGHT}")
    return picam2.stop_recording


def stream_usb_camera(output, on_error):
    """Start a thread that reads a USB camera and JPEG-encodes it with OpenCV.

    Returns a stop function, or None if the camera cannot be opened.
    """
    # Imported here so that the Raspberry Pi camera works without OpenCV
    import cv2
    from utils.camera_utils import open_camera

    cap = open_camera(CAMERA_DEVICE_ID, IMAGE_WIDTH, IMAGE_HEIGHT)
    if not cap.isOpened():
        print("Error: Could not open the camera.")
        return None
    cap.set(3, IMAGE_WIDTH)
    cap.set(4, IMAGE_HEIGHT)
    # The camera may not support the requested size, so report what it gives
    width, height = int(cap.get(3)), int(cap.get(4))
    print(f"Using USB camera {CAMERA_DEVICE_ID} at {width}x{height}")

    running = True

    def capture():
        while running:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to grab frame.")
                on_error()
                break
            ok, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
            if ok:
                output.write(jpeg.tobytes())

    thread = Thread(target=capture, daemon=True)
    thread.start()

    def stop():
        nonlocal running
        running = False
        thread.join(timeout=2)
        cap.release()
    return stop


def run_nohup():
    """Relaunch this script detached from the terminal, like `nohup`."""
    with open(LOG_FILE, "ab") as log:
        proc = subprocess.Popen([sys.executable, "-u", os.path.abspath(__file__)],
                                stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                start_new_session=True)
    print(f"Streaming in the background on http://0.0.0.0:{PORT}/ (PID {proc.pid})")
    print(f"Log: {os.path.abspath(LOG_FILE)}")
    print(f"Stop with: kill {proc.pid}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stream the camera as MJPEG over HTTP.")
    parser.add_argument("--nohup", action="store_true",
                        help="run in the background, surviving logout (output goes to " + LOG_FILE + ")")
    if parser.parse_args().nohup:
        run_nohup()
        sys.exit(0)

    output = StreamingOutput()
    httpd = StreamingServer(("", PORT), StreamingHandler)
    if has_raspberry_camera():
        stop_camera = stream_raspberry_camera(output)
    else:
        # Stop the server if the camera stops delivering frames
        stop_camera = stream_usb_camera(output, on_error=httpd.shutdown)
        if stop_camera is None:
            sys.exit(1)

    print(f"Streaming on http://0.0.0.0:{PORT}/ (Ctrl+C to stop)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop_camera()
        httpd.server_close()
