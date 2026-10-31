# ------------------------------------------------------------------------------
# rpi-object-detection
# ------------------------------------------------------------------------------
# Frame rate (FPS) benchmark for the examples in src/. Each example is run for
# a fixed time; every frame it prints a line, which is timestamped here, and
# the average FPS after a warm-up period is reported as a Markdown table.
#
# Usage (from the repository root, with the venv activated):
#   python3 benchmark/benchmark_fps.py                 # all examples
#   python3 benchmark/benchmark_fps.py --headless      # no display needed
#   python3 benchmark/benchmark_fps.py --only camera-test yolo --duration 30
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
import signal
import subprocess
import sys
import threading
import time

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT_DIR, 'src')

# Most examples print "Estimated fps:..." once per frame. Ultralytics YOLO
# prints a "Speed: ..." line once per frame instead.
FPS_LINE = re.compile(r'Estimated fps')
YOLO_LINE = re.compile(r'^Speed: ')

# (key, name, script relative to src/, per-frame line, files the example needs)
EXAMPLES = [
    ('camera-test', 'Camera Test', 'camera-test/cv_camera_test.py', FPS_LINE, []),
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

# Runs an example with OpenCV's window functions replaced, so it works without a
# display. waitKey() still sleeps for its delay to keep the frame timing the same.
HEADLESS_LAUNCHER = '''
import runpy, sys, time, cv2
def wait_key(delay=0):
    time.sleep(max(delay, 1) / 1000.0)
    return -1
cv2.imshow = lambda *args, **kwargs: None
cv2.namedWindow = lambda *args, **kwargs: None
cv2.setMouseCallback = lambda *args, **kwargs: None
cv2.destroyAllWindows = lambda *args, **kwargs: None
cv2.waitKey = wait_key
script = sys.argv[1]
sys.argv = sys.argv[1:]
runpy.run_path(script, run_name='__main__')
'''


def run_example(script, frame_line, duration, warmup, headless, verbose):
    """Run one example and return (frames, fps, error); fps is None on failure."""
    script_path = os.path.join(SRC_DIR, script)
    # Run from the example's own folder, as some examples load files by
    # relative path (e.g. orb.py reads simple.png).
    if headless:
        cmd = [sys.executable, '-u', '-c', HEADLESS_LAUNCHER, script_path]
    else:
        cmd = [sys.executable, '-u', script_path]
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


def main():
    parser = argparse.ArgumentParser(description='Measure the frame rate of the examples in src/.')
    parser.add_argument('--only', nargs='+', metavar='EXAMPLE', choices=[e[0] for e in EXAMPLES],
                        help='examples to run (default: all): ' + ', '.join(e[0] for e in EXAMPLES))
    parser.add_argument('--duration', type=float, default=DEFAULT_DURATION,
                        help='seconds to measure each example (default: %(default)s)')
    parser.add_argument('--warmup', type=float, default=DEFAULT_WARMUP,
                        help='seconds skipped after the first frame (default: %(default)s)')
    parser.add_argument('--headless', action='store_true',
                        help='do not open any windows, for running over SSH without a display')
    parser.add_argument('--verbose', action='store_true', help="show each example's output")
    args = parser.parse_args()

    if not args.headless and not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
        print('Warning: no display found; the examples need one to open their windows. '
              'Use --headless to run without a display.')

    examples = [e for e in EXAMPLES if not args.only or e[0] in args.only]
    print('Benchmarking {} example(s), {:.0f}s each after a {:.0f}s warm-up, on {} (Python {})'.format(
        len(examples), args.duration, args.warmup, platform.node(), platform.python_version()))

    results = []
    for key, name, script, frame_line, needed in examples:
        missing = [f for f in needed if not os.path.exists(os.path.join(SRC_DIR, os.path.dirname(script), f))]
        if missing:
            print('[{}] skipped: missing {}'.format(key, ', '.join(missing)))
            results.append((name, None, 'skipped (missing {})'.format(', '.join(missing))))
            continue
        print('[{}] running ...'.format(key), flush=True)
        frames, fps, error = run_example(script, frame_line, args.duration, args.warmup, args.headless, args.verbose)
        if fps is None:
            print('[{}] failed: {}'.format(key, error))
            results.append((name, None, 'failed'))
        else:
            print('[{}] {:.1f} FPS ({} frames)'.format(key, fps, frames))
            results.append((name, fps, None))
        # Give the camera a moment to be released before the next example
        time.sleep(1)

    print()
    print('| Example | FPS |')
    print('|---|---|')
    for name, fps, note in results:
        print('| {} | {} |'.format(name, note if fps is None else '{:.1f} FPS'.format(fps)))


if __name__ == '__main__':
    main()
