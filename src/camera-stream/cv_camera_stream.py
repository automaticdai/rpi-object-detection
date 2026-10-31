# ------------------------------------------------------------------------------
# rpi-object-detection
# ------------------------------------------------------------------------------
# Stream the Raspberry Pi camera as MJPEG over HTTP, so it can be viewed from
# any browser on the network at http://<raspberry-pi-ip>:8000/
# Requires the Raspberry Pi camera and Picamera2. Runs in the foreground by
# default (Ctrl+C to stop); use --nohup to keep it running in the background
# after you log out.
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
from threading import Condition

from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput

IMAGE_WIDTH = 1280
IMAGE_HEIGHT = 720
PORT = 8000
LOG_FILE = "camera_stream.log"

PAGE = b"""<html><head><title>Raspberry Pi camera</title></head>
<body style="margin:0;background:#111;display:flex;justify-content:center;align-items:center;height:100vh">
<img src="stream.mjpg" style="max-width:100%;max-height:100%"/></body></html>"""


class StreamingOutput(io.BufferedIOBase):
    """Holds the latest JPEG frame from the encoder and wakes up waiting clients."""

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
    parser = argparse.ArgumentParser(description="Stream the Raspberry Pi camera as MJPEG over HTTP.")
    parser.add_argument("--nohup", action="store_true",
                        help="run in the background, surviving logout (output goes to " + LOG_FILE + ")")
    if parser.parse_args().nohup:
        run_nohup()
        sys.exit(0)

    picam2 = Picamera2()
    picam2.configure(picam2.create_video_configuration(main={"size": (IMAGE_WIDTH, IMAGE_HEIGHT)}))
    output = StreamingOutput()
    picam2.start_recording(MJPEGEncoder(), FileOutput(output))
    print(f"Streaming on http://0.0.0.0:{PORT}/ (Ctrl+C to stop)")
    try:
        StreamingServer(("", PORT), StreamingHandler).serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        picam2.stop_recording()
