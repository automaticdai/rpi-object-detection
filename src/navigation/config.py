# ------------------------------------------------------------------------------
# Navigation System Configuration
# ------------------------------------------------------------------------------
# Configuration for visually impaired navigation system using YOLO detection
# ------------------------------------------------------------------------------

# Camera settings
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# YOLO model settings
YOLO_MODEL = "yolo11n.pt"  # Nano model for speed
CONFIDENCE_THRESHOLD = 0.45  # Minimum confidence to consider detection
IOU_THRESHOLD = 0.5  # Non-max suppression threshold

# Zone boundaries (as fraction of frame width)
# Adjust these to change zone sizes
ZONE_LEFT_END = 0.33      # Left zone: 0 to 33%
ZONE_RIGHT_START = 0.67   # Right zone: 67% to 100%
# Center zone is between LEFT_END and RIGHT_START

# Persistence settings (reduce false positives)
PERSISTENCE_FRAMES = 3  # Object must appear for N frames to be announced
MAX_TRACKING_DISTANCE = 100  # Max pixel distance to match same object across frames

# Audio settings
TTS_ENABLED = True
TTS_RATE = 175  # Words per minute (adjust for speed/clarity)
MESSAGE_COOLDOWN = 5.0  # Seconds between repeating same message (increased)
GLOBAL_COOLDOWN = 1.5  # Minimum seconds between any messages (increased)

# Priority classes (higher priority = announced first)
# Objects not in this list have priority 0
CLASS_PRIORITIES = {
    'person': 10,
    'bicycle': 9,
    'car': 9,
    'motorcycle': 9,
    'bus': 9,
    'truck': 9,
    'dog': 7,
    'cat': 6,
    'chair': 3,
    'bench': 3,
    'potted plant': 2,
    'backpack': 2,
    'handbag': 2,
    'suitcase': 2,
}

# Maximum objects to announce at once
MAX_ANNOUNCE_OBJECTS = 3

# Ultrasonic sensor settings (placeholder for future)
ULTRASONIC_ENABLED = False
ULTRASONIC_CRITICAL_DISTANCE = 1.0  # meters
ULTRASONIC_WARNING_DISTANCE = 2.0   # meters

# Performance settings
INFERENCE_THREADS = 2  # CPU threads for YOLO
FRAME_QUEUE_SIZE = 2   # Drop old frames if processing is slow
