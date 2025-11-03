# Navigation System - Quick Reference

## 🚀 Quick Start

### Run the navigation system
```bash
./run_navigation.sh
```

Or directly:
```bash
export PYTHONPATH=/home/shanu/Projects/Python/rpi-object-detection
uv run python -m src.navigation.navigation_system
```

### Run tests
```bash
PYTHONPATH=/home/shanu/Projects/Python/rpi-object-detection uv run python src/navigation/tests/test_zone_logic.py
```

## 📋 Prerequisites

### Check if espeak is installed
```bash
espeak --version
# or
espeak-ng --version
```

### Install espeak (if needed)
```bash
# Arch Linux
sudo pacman -S espeak-ng

# Debian/Ubuntu/Raspberry Pi OS
sudo apt-get install espeak-ng
```

### Test TTS
```bash
espeak "Navigation system ready"
```

## 🎯 Command-Line Options

```bash
# Basic usage
./run_navigation.sh

# Use different camera
./run_navigation.sh --camera 1

# Disable audio (testing mode)
./run_navigation.sh --no-audio

# Headless mode (no video window)
./run_navigation.sh --no-video

# Custom YOLO model
./run_navigation.sh --model yolov8n.pt
```

## ⌨️ Controls

- **`q`** or **`ESC`** - Quit application
- **`m`** - Toggle mute/unmute audio

## 🔧 Configuration

Edit `src/navigation/config.py` for:
- Zone boundaries (left/center/right split)
- Detection confidence threshold
- Persistence filtering
- Audio settings (rate, cooldowns)
- Object priorities
- Camera resolution

## 📊 Performance Tips

### For Raspberry Pi
1. Lower resolution in config:
   ```python
   CAMERA_WIDTH = 320
   CAMERA_HEIGHT = 320
   ```

2. Increase persistence:
   ```python
   PERSISTENCE_FRAMES = 5
   ```

3. Use quantized model (future optimization)

## 🧪 Testing Components

### Test zone mapping
```python
from src.navigation.zone_mapper import ZoneMapper
mapper = ZoneMapper(frame_width=640)
zone = mapper.get_zone(100)  # 'left'
```

### Test message generation
```python
from src.navigation.announcer import AudioAnnouncer
announcer = AudioAnnouncer(enabled=False)
message = announcer.generate_message(zone_dict)
```

## 🐛 Troubleshooting

### No audio
1. Check espeak: `espeak "test"`
2. Check audio device: `aplay -l`
3. Test pyttsx3: `python -c "import pyttsx3; pyttsx3.speak('test')"`

### Camera not found
1. List cameras: `ls /dev/video*`
2. Test camera: `uv run python src/camera-test/cv_camera_test.py`
3. Try different ID: `--camera 1`

### Low FPS
1. Reduce resolution in config
2. Increase PERSISTENCE_FRAMES
3. Use smaller YOLO model

## 📁 File Structure

```
src/navigation/
├── config.py              # All settings
├── detector.py            # YOLO inference
├── zone_mapper.py         # Zone logic + filtering
├── announcer.py           # TTS engine
├── sensor.py              # Ultrasonic stub
├── navigation_system.py   # Main app
├── README.md              # Full documentation
└── tests/
    └── test_zone_logic.py # Unit tests
```

## 🎤 Example Announcements

- "person on your left"
- "2 persons on your right"
- "person on your left and car on your center"
- "2 persons on your left, car on your center, and chair on your right"

## 🔮 Future: Ultrasonic Sensor

To integrate HC-SR04:
1. Connect to GPIO pins (see `sensor.py` comments)
2. Implement GPIO reading in `sensor.py`
3. Enable: `ULTRASONIC_ENABLED = True` in config
4. Set critical distance thresholds

## 📝 Notes

- System requires 3 consecutive frames before announcing (reduces false positives)
- Messages throttled to avoid spam (3s per message, 0.8s global)
- High-priority objects (person, car) announced first
- Works on x86 for testing, ARM for deployment
