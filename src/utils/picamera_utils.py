try:
    from picamera2 import Picamera2
    picam2_available = True
except ImportError:
    picam2_available = False


def is_raspberry_camera():
    """Check if the Raspberry Pi Camera is being used."""
    if picam2_available:
        try:
            _ = Picamera2()
            return True
        except Exception:
            return False
    return False

def get_picamera(width, height):
    """Get the camera object."""
    if picam2_available:
        picam2 =  Picamera2()
        picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (width, height)}))
    return None