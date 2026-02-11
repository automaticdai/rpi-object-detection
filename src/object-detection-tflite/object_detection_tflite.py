# ------------------------------------------------------------------------------
# rpi-object-detection
# ------------------------------------------------------------------------------
# Use TensorFlow Lite to detect objects in a video stream
# Supports EfficientDet-Lite and SSD MobileNet models with COCO labels
# ------------------------------------------------------------------------------
# automaticdai
# YF Robotics Labrotary
# Instagram: yfrobotics
# Twitter: @yfrobotics
# Website: https://yfrobotics.github.io/
# ------------------------------------------------------------------------------
# References:
# - https://github.com/tensorflow/examples/tree/master/lite/examples/object_detection/raspberry_pi
# - https://ai.google.dev/edge/litert
# ------------------------------------------------------------------------------

import os
import sys
import cv2
import time
import numpy as np

# Add src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.picamera_utils import is_raspberry_camera, get_picamera

# Flexible import: try tflite-runtime first, then ai-edge-litert, then full TF
try:
    from tflite_runtime.interpreter import Interpreter
except ImportError:
    try:
        from ai_edge_litert.interpreter import Interpreter
    except ImportError:
        from tensorflow.lite.python.interpreter import Interpreter

CAMERA_DEVICE_ID = 0
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480
IS_RASPI_CAMERA = is_raspberry_camera()

# Model configuration
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'efficientdet_lite0.tflite')
LABELS_PATH = os.path.join(os.path.dirname(__file__), 'coco_labels.txt')
MIN_CONFIDENCE = 0.5
NUM_THREADS = 4

cnt_frame = 0
fps = 0

print("Using raspi camera: ", IS_RASPI_CAMERA)


def load_labels(label_path):
    """Load label file. Each line is a class name, index = line number."""
    with open(label_path, 'r') as f:
        return [line.strip() for line in f.readlines()]


def visualize_fps(image, fps: int):
    if len(np.shape(image)) < 3:
        text_color = (255, 255, 255)  # white
    else:
        text_color = (0, 255, 0)  # green
    row_size = 20  # pixels
    left_margin = 24  # pixels

    font_size = 1
    font_thickness = 1

    fps_text = 'FPS = {:.1f}'.format(fps)
    text_location = (left_margin, row_size)
    cv2.putText(image, fps_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                font_size, text_color, font_thickness)

    return image


if __name__ == "__main__":
    # Load labels
    if not os.path.exists(LABELS_PATH):
        print("Error: Label file not found at", LABELS_PATH)
        print("Download with: wget https://raw.githubusercontent.com/google-coral/test_data/master/coco_labels.txt")
        sys.exit(1)

    if not os.path.exists(MODEL_PATH):
        print("Error: Model file not found at", MODEL_PATH)
        print("Download with: wget https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/int8/1/efficientdet_lite0.tflite")
        sys.exit(1)

    labels = load_labels(LABELS_PATH)
    print("Loaded {} labels".format(len(labels)))

    # Load TFLite model
    interpreter = Interpreter(model_path=MODEL_PATH, num_threads=NUM_THREADS)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    model_height = input_details[0]['shape'][1]
    model_width = input_details[0]['shape'][2]
    is_floating = (input_details[0]['dtype'] == np.float32)

    print("Model input: {}x{}, float={}".format(model_width, model_height, is_floating))

    try:
        # Create video capture
        if IS_RASPI_CAMERA:
            cap = get_picamera(IMAGE_WIDTH, IMAGE_HEIGHT)
            cap.start()
        else:
            cap = cv2.VideoCapture(CAMERA_DEVICE_ID)
            cap.set(3, IMAGE_WIDTH)
            cap.set(4, IMAGE_HEIGHT)

        while True:
            # Record start time
            start_time = time.time()

            # Read frame
            if IS_RASPI_CAMERA:
                frame = cap.capture_array()
            else:
                _, frame = cap.read()

            frame_h, frame_w = frame.shape[:2]

            # Preprocess: BGR -> RGB, resize to model input
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (model_width, model_height))
            input_data = np.expand_dims(frame_resized, axis=0)

            if is_floating:
                input_data = (input_data.astype(np.float32) - 127.5) / 127.5

            # Run inference
            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()

            # Parse outputs: boxes, classes, scores, num_detections
            boxes = interpreter.get_tensor(output_details[0]['index'])[0]
            classes = interpreter.get_tensor(output_details[1]['index'])[0]
            scores = interpreter.get_tensor(output_details[2]['index'])[0]
            num_detections = int(interpreter.get_tensor(output_details[3]['index'])[0])

            # Draw detections
            for i in range(num_detections):
                if scores[i] < MIN_CONFIDENCE:
                    continue

                # Denormalize box coordinates [ymin, xmin, ymax, xmax]
                ymin, xmin, ymax, xmax = boxes[i]
                x1 = int(xmin * frame_w)
                y1 = int(ymin * frame_h)
                x2 = int(xmax * frame_w)
                y2 = int(ymax * frame_h)

                class_id = int(classes[i])
                label = labels[class_id] if class_id < len(labels) else "id:{}".format(class_id)
                text = "{} {:.0%}".format(label, scores[i])

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, text, (x1, y1 - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Show frame with FPS
            visualize_fps(frame, fps)
            cv2.imshow('TFLite Object Detection', frame)

            # Calculate FPS
            end_time = time.time()
            seconds = end_time - start_time
            fps = 1.0 / seconds
            print("Frame{}: Estimated fps:{:.1f}".format(cnt_frame, fps))

            cnt_frame += 1

            # ESC to exit
            if cv2.waitKey(1) == 27:
                break
    except Exception as e:
        print(e)
    finally:
        cv2.destroyAllWindows()
        cap.close() if IS_RASPI_CAMERA else cap.release()
