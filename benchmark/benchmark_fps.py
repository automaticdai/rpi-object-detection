# ------------------------------------------------------------------------------
# rpi-object-detection
# ------------------------------------------------------------------------------
# Frame rate (FPS) benchmark for the examples in src/. Each example is measured
# in two ways:
#
# - Camera FPS: the example runs as normal on the live camera. This is what you
#   see in practice, but it is capped by the camera (often 30 FPS) and by the
#   waitKey() delay in the example's loop.
# - Processing FPS: the example is fed a clip recorded from the camera
#   beforehand, as fast as it can take frames, with no windows and no waitKey()
#   delay. This shows how fast the board can run the example's processing.
#
# Every example prints a line per frame, which is timestamped here; the
# average FPS after a warm-up period is reported as a Markdown table.
#
# Usage (from the repository root, with the venv activated):
#   python3 benchmark/benchmark_fps.py                  # all examples, both modes
#   python3 benchmark/benchmark_fps.py --headless       # no display needed
#   python3 benchmark/benchmark_fps.py --mode processing --video clip.mp4
#   python3 benchmark/benchmark_fps.py --only face yolo --duration 30
# ------------------------------------------------------------------------------
# automaticdai
# YF Robotics Laboratory
# Instagram: yfrobotics
# Twitter: @yfrobotics
# Website: https://yfrobotics.github.io/
# ------------------------------------------------------------------------------

import argparse
import os
import platform
import re
import runpy
import signal
import subprocess
import sys
import tempfile
import threading
import time

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT_DIR, 'src')

# Most examples print "Estimated fps:..." once per frame. Ultralytics YOLO
# prints a "Speed: ..." line once per frame instead.
FPS_LINE = re.compile(r'Estimated fps')
YOLO_LINE = re.compile(r'^Speed: ')

# (key, name, script relative to src/, per-frame line, files the example needs)
# Camera test and camera streaming are not included, as they do no processing.
EXAMPLES = [
    ('motion-detection', 'Motion Detection', 'motion-detection/cv_motion_detection.py', FPS_LINE, []),
    ('color', 'Color-based Tracking', 'object-tracking-color/cv_object_tracking_color.py', FPS_LINE, []),
    ('shape', 'Shape-based Tracking', 'object-tracking-shape/cv_object_tracking_shape.py', FPS_LINE, []),
    ('orb', 'Feature-based Tracking (ORB)', 'object-tracking-feature/orb.py', FPS_LINE, []),
    ('face', 'Face Detection', 'face-detection/face-detection.py', FPS_LINE, []),
    ('tflite', 'TensorFlow Lite (EfficientDet-Lite0)', 'object-detection-tflite/object_detection_tflite.py', FPS_LINE,
     ['efficientdet_lite0.tflite', 'coco_labels.txt']),
    ('yolo', 'YOLO11n (Ultralytics, 640x480)', 'object-detection-yolo/object_detection_yolo.py', YOLO_LINE, []),
]

DEFAULT_DURATION = 20   # seconds measured per example
DEFAULT_WARMUP = 5      # seconds skipped after the first frame
STARTUP_TIMEOUT = 120   # seconds to wait for the first frame (YOLO loads slowly)
CLIP_WIDTH = 640        # the clip is recorded at the largest resolution used by
CLIP_HEIGHT = 480       # the examples, and scaled down for the others
DEFAULT_CLIP_FRAMES = 60


# ------------------------------------------------------------------------------
# Inside the example's process
# ------------------------------------------------------------------------------
class ClipCapture:
    """Stands in for cv2.VideoCapture, returning the recorded clip in a loop."""

    def __init__(self, frames, width, height):
        import cv2
        self.frames = [cv2.resize(f, (width, height)) for f in frames]
        self.index = 0

    def isOpened(self):
        return True

    def read(self):
        frame = self.frames[self.index].copy()   # examples draw on the frame
        self.index = (self.index + 1) % len(self.frames)
        return True, frame

    def set(self, prop_id, value):
        return True

    def release(self):
        pass


def run_patched_example(script, no_display, clip):
    """Run an example with OpenCV's windows and/or the camera replaced.

    Without a display, waitKey() still sleeps for its delay so the frame timing
    stays the same. With a clip, waitKey() returns at once so that only the
    processing is measured.
    """
    import cv2
    import numpy as np

    def wait_key(delay=0):
        if clip is None:
            time.sleep(max(delay, 1) / 1000.0)
        return -1

    if no_display:
        cv2.imshow = lambda *args, **kwargs: None
        cv2.namedWindow = lambda *args, **kwargs: None
        cv2.setMouseCallback = lambda *args, **kwargs: None
        cv2.destroyAllWindows = lambda *args, **kwargs: None
        cv2.waitKey = wait_key

    if clip is not None:
        frames = np.load(clip)
        sys.path.insert(0, SRC_DIR)
        import utils.picamera_utils
        import utils.camera_utils
        utils.picamera_utils.is_raspberry_camera = lambda: False
        utils.camera_utils.open_camera = lambda device_id, width, height: ClipCapture(frames, width, height)

    sys.argv = [script]
    runpy.run_path(script, run_name='__main__')


# ------------------------------------------------------------------------------
# Benchmark driver
# ------------------------------------------------------------------------------
def record_clip(path, num_frames, video):
    """Save num_frames BGR frames from a video file or the camera to path (.npy)."""
    import cv2
    import numpy as np
    sys.path.insert(0, SRC_DIR)
    from utils.picamera_utils import is_raspberry_camera, get_picamera
    from utils.camera_utils import open_camera

    frames = []
    if video:
        cap = cv2.VideoCapture(video)
        while len(frames) < num_frames:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(cv2.resize(frame, (CLIP_WIDTH, CLIP_HEIGHT)))
        cap.release()
    elif is_raspberry_camera():
        cap = get_picamera(CLIP_WIDTH, CLIP_HEIGHT)
        cap.start()
        time.sleep(1)   # let auto exposure settle
        for _ in range(num_frames):
            frames.append(cv2.cvtColor(cap.capture_array(), cv2.COLOR_BGRA2BGR))
        cap.close()
    else:
        cap = open_camera(0, CLIP_WIDTH, CLIP_HEIGHT)
        cap.set(3, CLIP_WIDTH)
        cap.set(4, CLIP_HEIGHT)
        for _ in range(30):   # let auto exposure settle
            cap.read()
        while len(frames) < num_frames:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(cv2.resize(frame, (CLIP_WIDTH, CLIP_HEIGHT)))
        cap.release()

    if not frames:
        return False
    np.save(path, np.stack(frames))
    return True


def run_example(script, frame_line, duration, warmup, no_display, clip, verbose):
    """Run one example and return (frames, fps, error); fps is None on failure."""
    script_path = os.path.join(SRC_DIR, script)
    if no_display or clip:
        cmd = [sys.executable, '-u', os.path.abspath(__file__), '--run-example', script_path]
        if no_display:
            cmd.append('--no-display')
        if clip:
            cmd += ['--clip', clip]
    else:
        cmd = [sys.executable, '-u', script_path]
    # Run from the example's own folder, as some examples load files by
    # relative path (e.g. orb.py reads simple.png).
    proc = subprocess.Popen(cmd, cwd=os.path.dirname(script_path),
                            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, errors='replace')

    timestamps = []
    tail = []

    def reader():
        for line in proc.stdout:
            if frame_line.search(line):
                timestamps.append(time.monotonic())
            if line.strip():
                tail.append(line.rstrip())
                del tail[:-10]
            if verbose:
                print('    ' + line.rstrip())

    thread = threading.Thread(target=reader, daemon=True)
    thread.start()

    start = time.monotonic()
    while proc.poll() is None:
        if timestamps:
            if time.monotonic() - timestamps[0] >= warmup + duration:
                break
        elif time.monotonic() - start > STARTUP_TIMEOUT:
            break
        time.sleep(0.2)

    # Stop with Ctrl+C first so the example releases the camera cleanly
    if proc.poll() is None:
        proc.send_signal(signal.SIGINT)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
    thread.join(timeout=2)

    if not timestamps:
        return 0, None, (tail[-1] if tail else 'no output')
    window = [t for t in timestamps if t >= timestamps[0] + warmup]
    if len(window) < 2:
        return len(window), None, 'too few frames after warm-up (try a longer --duration)'
    return len(window), (len(window) - 1) / (window[-1] - window[0]), None


def format_fps(fps, note):
    return note if fps is None else '{:.1f} FPS'.format(fps)


def main():
    parser = argparse.ArgumentParser(description='Measure the frame rate of the examples in src/.')
    parser.add_argument('--mode', choices=['both', 'camera', 'processing'], default='both',
                        help='camera: live camera, as the examples normally run; processing: recorded '
                             'clip as fast as possible, without the camera frame rate limit '
                             '(default: %(default)s)')
    parser.add_argument('--only', nargs='+', metavar='EXAMPLE', choices=[e[0] for e in EXAMPLES],
                        help='examples to run (default: all): ' + ', '.join(e[0] for e in EXAMPLES))
    parser.add_argument('--duration', type=float, default=DEFAULT_DURATION,
                        help='seconds to measure each example (default: %(default)s)')
    parser.add_argument('--warmup', type=float, default=DEFAULT_WARMUP,
                        help='seconds skipped after the first frame (default: %(default)s)')
    parser.add_argument('--headless', action='store_true',
                        help='do not open any windows, for running over SSH without a display')
    parser.add_argument('--video', metavar='FILE',
                        help='video file to use for processing FPS instead of recording from the camera')
    parser.add_argument('--clip-frames', type=int, default=DEFAULT_CLIP_FRAMES,
                        help='number of frames in the clip for processing FPS (default: %(default)s)')
    parser.add_argument('--verbose', action='store_true', help="show each example's output")
    # Used internally to run an example in a patched process
    parser.add_argument('--run-example', help=argparse.SUPPRESS)
    parser.add_argument('--no-display', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--clip', help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.run_example:
        run_patched_example(args.run_example, args.no_display, args.clip)
        return

    camera_mode = args.mode in ('both', 'camera')
    processing_mode = args.mode in ('both', 'processing')
    if camera_mode and not args.headless and not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
        print('Warning: no display found; the examples need one to open their windows. '
              'Use --headless to run without a display.')

    examples = [e for e in EXAMPLES if not args.only or e[0] in args.only]
    print('Benchmarking {} example(s), {:.0f}s each after a {:.0f}s warm-up, on {} (Python {})'.format(
        len(examples), args.duration, args.warmup, platform.node(), platform.python_version()))

    clip = None
    tmp_dir = tempfile.TemporaryDirectory()
    if processing_mode:
        clip = os.path.join(tmp_dir.name, 'clip.npy')
        print('Recording a {}-frame clip from {} ...'.format(args.clip_frames, args.video or 'the camera'), flush=True)
        if not record_clip(clip, args.clip_frames, args.video):
            print('Error: could not read any frames for the clip.')
            sys.exit(1)

    results = []
    for key, name, script, frame_line, needed in examples:
        missing = [f for f in needed if not os.path.exists(os.path.join(SRC_DIR, os.path.dirname(script), f))]
        if missing:
            note = 'skipped (missing {})'.format(', '.join(missing))
            print('[{}] {}'.format(key, note))
            results.append((name, None, None, note))
            continue

        fps = {}
        for mode, enabled, mode_clip in (('camera', camera_mode, None), ('processing', processing_mode, clip)):
            if not enabled:
                continue
            print('[{}] {} ...'.format(key, mode), end=' ', flush=True)
            frames, fps[mode], error = run_example(script, frame_line, args.duration, args.warmup,
                                                   args.headless or mode == 'processing', mode_clip, args.verbose)
            print('failed: {}'.format(error) if fps[mode] is None else '{:.1f} FPS ({} frames)'.format(fps[mode], frames))
            # Give the camera a moment to be released before the next run
            time.sleep(1)
        results.append((name, fps.get('camera'), fps.get('processing'), 'failed'))

    tmp_dir.cleanup()

    print()
    header = ['Example']
    if camera_mode:
        header.append('Camera FPS')
    if processing_mode:
        header += ['Processing FPS', 'Time per frame']
    print('| ' + ' | '.join(header) + ' |')
    print('|' + '---|' * len(header))
    for name, camera_fps, processing_fps, note in results:
        row = [name]
        if camera_mode:
            row.append(format_fps(camera_fps, note))
        if processing_mode:
            row.append(format_fps(processing_fps, note))
            row.append('-' if processing_fps is None else '{:.1f} ms'.format(1000.0 / processing_fps))
        if note.startswith('skipped'):
            # Show the reason once, not in every column
            row = [name, note] + ['-'] * (len(row) - 2)
        print('| ' + ' | '.join(row) + ' |')


if __name__ == '__main__':
    main()
