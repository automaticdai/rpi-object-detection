# ------------------------------------------------------------------------------
# Ultrasonic Sensor Module (Stub for Future Integration)
# ------------------------------------------------------------------------------
# Placeholder for ultrasonic distance sensor integration
# ------------------------------------------------------------------------------

import time
from typing import Optional


class UltrasonicSensor:
    """
    Stub for ultrasonic distance sensor
    
    This is a placeholder for future integration with HC-SR04 or similar sensors.
    On Raspberry Pi, you would use GPIO pins to trigger and read echo signals.
    """
    
    def __init__(self, enabled: bool = False):
        """
        Initialize ultrasonic sensor
        
        Args:
            enabled: Enable sensor (False for now as it's a stub)
        """
        self.enabled = enabled
        self.last_distance = None
        self.last_read_time = 0
        
        if self.enabled:
            print("UltrasonicSensor: Stub mode (not implemented yet)")
            # TODO: Initialize GPIO pins for trigger and echo
            # import RPi.GPIO as GPIO
            # GPIO.setmode(GPIO.BCM)
            # GPIO.setup(TRIGGER_PIN, GPIO.OUT)
            # GPIO.setup(ECHO_PIN, GPIO.IN)
    
    def read_distance(self) -> Optional[float]:
        """
        Read distance from sensor
        
        Returns:
            Distance in meters, or None if sensor disabled or read failed
        """
        if not self.enabled:
            return None
        
        # TODO: Implement actual sensor reading
        # This would involve:
        # 1. Send trigger pulse (10us HIGH)
        # 2. Wait for echo pin to go HIGH
        # 3. Measure time until echo pin goes LOW
        # 4. Calculate distance: distance = (time * speed_of_sound) / 2
        
        # For now, return None (stub)
        return None
    
    def get_status(self) -> str:
        """
        Get human-readable status
        
        Returns:
            Status string
        """
        if not self.enabled:
            return "disabled"
        
        if self.last_distance is None:
            return "no reading"
        elif self.last_distance < 1.0:
            return "obstacle close"
        elif self.last_distance < 2.0:
            return "obstacle near"
        else:
            return "clear"
    
    def is_obstacle_detected(self, critical_distance: float = 1.0) -> bool:
        """
        Check if obstacle is within critical distance
        
        Args:
            critical_distance: Distance threshold in meters
            
        Returns:
            True if obstacle detected within threshold
        """
        if not self.enabled or self.last_distance is None:
            return False
        
        return self.last_distance < critical_distance
    
    def cleanup(self):
        """Cleanup GPIO resources"""
        if self.enabled:
            # TODO: Cleanup GPIO
            # GPIO.cleanup()
            pass


# Example integration code for future reference:
"""
# On Raspberry Pi with HC-SR04 sensor:

import RPi.GPIO as GPIO
import time

TRIGGER_PIN = 23  # GPIO pin for trigger
ECHO_PIN = 24     # GPIO pin for echo

def read_distance():
    # Send trigger pulse
    GPIO.output(TRIGGER_PIN, True)
    time.sleep(0.00001)  # 10 microseconds
    GPIO.output(TRIGGER_PIN, False)
    
    # Wait for echo
    start_time = time.time()
    while GPIO.input(ECHO_PIN) == 0:
        start_time = time.time()
        if time.time() - start_time > 0.1:  # Timeout
            return None
    
    stop_time = time.time()
    while GPIO.input(ECHO_PIN) == 1:
        stop_time = time.time()
        if time.time() - start_time > 0.1:  # Timeout
            return None
    
    # Calculate distance
    elapsed = stop_time - start_time
    distance = (elapsed * 34300) / 2  # Speed of sound = 343 m/s
    
    return distance / 100  # Convert cm to meters
"""
