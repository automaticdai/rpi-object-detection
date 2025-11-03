# Navigation System for Visually Impaired Users

A real-time navigation assistance system using YOLO object detection and spatial zone mapping to help visually impaired users navigate their environment safely.

## Features

- **Real-time Object Detection**: Uses YOLOv11 (nano model) for fast, accurate object detection
- **Spatial Zone Mapping**: Divides camera view into three zones (left, center, right) to provide directional guidance
- **Audio Announcements**: Offline text-to-speech (TTS) provides clear, concise spoken directions
- **Smart Filtering**: Persistence filtering and throttling reduce false positives and avoid announcement spam
- **Priority System**: Safety-critical objects (people, vehicles) are prioritized in announcements
- **Extensible Design**: Ready for ultrasonic sensor integration for proximity detection
- **Cross-platform**: Works on both development machines (Arch Linux, etc.) and Raspberry Pi

## Architecture

```
Camera → YOLO Detector → Zone Mapper → Audio Announcer
                              ↓
                       [Persistence Filter]
                              ↓
                       [Priority Sorting]
```

### Components

- **`detector.py`**: YOLO inference engine
- **`zone_mapper.py`**: Maps detections to left/center/right zones with temporal filtering
- **`announcer.py`**: TTS engine with message queue and throttling
- **`sensor.py`**: Ultrasonic sensor stub (for future integration)
- **`navigation_system.py`**: Main application coordinator
- **`config.py`**: Centralized configuration

## Installation

### 1. Install dependencies

```bash
# Install pyttsx3 for TTS
uv pip install pyttsx3

# Or reinstall all requirements
uv pip install -r requirements.txt
```

### 2. System dependencies (Linux)

For text-to-speech to work, you need espeak:

```bash
# Arch Linux
sudo pacman -S espeak-ng

# Debian/Ubuntu/Raspberry Pi OS
sudo apt-get install espeak-ng

# Or use espeak (older version)
sudo pacman -S espeak  # Arch
sudo apt-get install espeak  # Debian/Ubuntu
```

## Usage

### Basic usage

```bash
# Run with default settings (camera 0, audio enabled, video window)
uv run python -m src.navigation.navigation_system
```

### Command-line options

```bash
# Use different camera
uv run python -m src.navigation.navigation_system --camera 1

# Disable audio for testing
uv run python -m src.navigation.navigation_system --no-audio

# Headless mode (no video window, e.g., for deployment)
uv run python -m src.navigation.navigation_system --no-video

# Custom YOLO model
uv run python -m src.navigation.navigation_system --model yolov8n.pt
```

### Controls

- **`q` or `ESC`**: Quit application
- **`m`**: Toggle mute/unmute audio

## Configuration

Edit `src/navigation/config.py` to customize:

- **Zone boundaries**: Adjust `ZONE_LEFT_END` and `ZONE_RIGHT_START`
- **Detection thresholds**: Modify `CONFIDENCE_THRESHOLD`
- **Persistence filtering**: Change `PERSISTENCE_FRAMES`
- **Audio settings**: Adjust `TTS_RATE`, `MESSAGE_COOLDOWN`, `GLOBAL_COOLDOWN`
- **Object priorities**: Edit `CLASS_PRIORITIES` dictionary
- **Camera resolution**: Set `CAMERA_WIDTH` and `CAMERA_HEIGHT`

### Key configuration options

```python
# Zone boundaries (fraction of frame width)
ZONE_LEFT_END = 0.33      # Left zone: 0-33%
ZONE_RIGHT_START = 0.67   # Right zone: 67-100%

# Detection settings
CONFIDENCE_THRESHOLD = 0.45  # Minimum confidence
PERSISTENCE_FRAMES = 3       # Frames before announcing

# Audio settings
TTS_RATE = 175              # Words per minute
MESSAGE_COOLDOWN = 3.0      # Seconds between same message
GLOBAL_COOLDOWN = 0.8       # Seconds between any messages

# Priority classes (higher = more important)
CLASS_PRIORITIES = {
    'person': 10,
    'bicycle': 9,
    'car': 9,
    # ... etc
}
```

## Testing

Run unit tests to verify zone logic and message generation:

```bash
uv run python src/navigation/tests/test_zone_logic.py
```

Expected output:
```
test_aggregate_by_zone (__main__.TestZoneMapper) ... ok
test_get_priority (__main__.TestZoneMapper) ... ok
test_get_zone_boundaries (__main__.TestZoneMapper) ... ok
test_get_zone_center (__main__.TestZoneMapper) ... ok
test_get_zone_left (__main__.TestZoneMapper) ... ok
test_get_zone_right (__main__.TestZoneMapper) ... ok
test_map_detections (__main__.TestZoneMapper) ... ok
test_message_different_zones (__main__.TestMessageGeneration) ... ok
test_message_multiple_same_class (__main__.TestMessageGeneration) ... ok
test_message_single_object (__main__.TestMessageGeneration) ... ok
test_pluralization (__main__.TestMessageGeneration) ... ok
test_zone_boundaries (__main__.TestZoneMapper) ... ok

----------------------------------------------------------------------
Ran 12 tests in 0.XXXs

OK
```

## Example Announcements

The system generates natural language announcements:

- Single object: **"person on your left"**
- Multiple objects: **"2 persons on your right"**
- Multiple zones: **"person on your left and car on your right"**
- Complex scene: **"2 persons on your left, car on your center, and chair on your right"**

## Performance

### Development Machine (x86_64)
- ~3-4ms inference time with YOLOv11n
- 200-300 FPS (limited by display refresh)

### Raspberry Pi 4/5 (estimated)
- ~50-150ms inference time with YOLOv11n
- 5-15 FPS (sufficient for navigation)
- Lower resolution (320x320) recommended for better performance

### Optimization Tips

1. **Use smaller models**: yolo11n is already the smallest; consider yolo8n if available
2. **Reduce resolution**: Set `CAMERA_WIDTH=320, CAMERA_HEIGHT=320` in config
3. **Convert to TFLite/ONNX**: See "Performance Tuning" section below
4. **Increase persistence threshold**: Reduce false positives and processing load

## Future Enhancements

### Ultrasonic Sensor Integration

The system includes a stub for HC-SR04 ultrasonic sensors. To integrate:

1. Connect HC-SR04 to Raspberry Pi GPIO pins
2. Edit `sensor.py` to implement actual GPIO reading
3. Enable in config: `ULTRASONIC_ENABLED = True`
4. Set critical distances in config

Example GPIO setup (commented code in `sensor.py`):
- Trigger pin: GPIO 23
- Echo pin: GPIO 24

### Performance Tuning for Raspberry Pi

For deployment, consider:

1. **Model quantization**: Convert YOLO to TFLite INT8
2. **Hardware acceleration**: Use Coral TPU or Intel Movidius
3. **Frame skipping**: Process every Nth frame
4. **Resolution tuning**: Balance accuracy vs speed

## Troubleshooting

### No audio output

1. Check espeak is installed: `espeak --version`
2. Test TTS: `espeak "hello world"`
3. Check audio device: `aplay -l`
4. Verify pyttsx3 installation: `uv pip list | grep pyttsx3`

### Low FPS on Raspberry Pi

1. Reduce camera resolution in config
2. Use smaller YOLO model (yolo8n)
3. Increase `PERSISTENCE_FRAMES` to reduce processing
4. Consider model quantization/conversion

### Camera not detected

1. Check camera connection: `ls /dev/video*`
2. Test with: `uv run python src/camera-test/cv_camera_test.py`
3. Try different camera ID: `--camera 1`

### Import errors

Make sure all dependencies are installed:
```bash
uv pip install -r requirements.txt
```

## Project Structure

```
src/navigation/
├── __init__.py
├── config.py              # Configuration settings
├── detector.py            # YOLO object detector
├── zone_mapper.py         # Zone mapping and filtering
├── announcer.py           # TTS audio announcer
├── sensor.py              # Ultrasonic sensor (stub)
├── navigation_system.py   # Main application
└── tests/
    ├── __init__.py
    └── test_zone_logic.py # Unit tests
```

## License

This project extends the [rpi-object-detection](https://github.com/automaticdai/rpi-object-detection) repository.

## Contributing

Contributions welcome! Areas for improvement:
- Object tracking for stable IDs
- Depth estimation from stereo cameras
- Haptic feedback integration
- Multi-language support
- Performance optimizations for embedded devices
