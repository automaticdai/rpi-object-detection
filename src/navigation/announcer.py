# ------------------------------------------------------------------------------
# Audio Announcer Module
# ------------------------------------------------------------------------------
# Text-to-speech engine with message queue, throttling, and smart announcements
# ------------------------------------------------------------------------------

import threading
import queue
import time
import subprocess
import shutil
from typing import List, Dict, Optional
from collections import defaultdict

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    print("Warning: pyttsx3 not available. Install with: uv pip install pyttsx3")

# Check for espeak command-line tool
ESPEAK_AVAILABLE = shutil.which('espeak') or shutil.which('espeak-ng')

from .zone_mapper import ZoneDetection
from . import config


class AudioAnnouncer:
    """Manages text-to-speech announcements with intelligent throttling"""
    
    def __init__(self, enabled: bool = None, rate: int = None):
        """
        Initialize audio announcer
        
        Args:
            enabled: Enable/disable TTS
            rate: Speech rate (words per minute)
        """
        self.enabled = enabled if enabled is not None else config.TTS_ENABLED
        self.rate = rate or config.TTS_RATE
        
        # Message queue and worker thread
        self.message_queue = queue.Queue()
        self.worker_thread = None
        self.running = False
        
        # Throttling: track last announcement time per message
        self.last_announced = {}  # message -> timestamp
        self.last_global_announce = 0  # timestamp of last announcement
        
        # TTS engine (initialized in worker thread)
        self.engine = None
        self.use_espeak_direct = False
        
        # Prefer direct espeak if available (more reliable on Linux)
        if self.enabled:
            if ESPEAK_AVAILABLE:
                self.use_espeak_direct = True
                self.espeak_cmd = 'espeak-ng' if shutil.which('espeak-ng') else 'espeak'
                print(f"AudioAnnouncer ready (using {self.espeak_cmd})")
            elif PYTTSX3_AVAILABLE:
                print("AudioAnnouncer ready (using pyttsx3)")
            else:
                print("Warning: No TTS engine available (install espeak-ng or pyttsx3)")
                self.enabled = False
        
        if self.enabled:
            self.start()
        else:
            print("AudioAnnouncer disabled")
    
    def start(self):
        """Start the announcer worker thread"""
        if self.running:
            return
        
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
    
    def stop(self):
        """Stop the announcer worker thread"""
        if not self.running:
            return
        
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=2)
    
    def _init_engine(self):
        """Initialize TTS engine (called in worker thread)"""
        if self.use_espeak_direct:
            # Using direct espeak, no initialization needed
            return
        
        # Initialize pyttsx3
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', self.rate)
            
            # Try to use a better voice if available
            voices = self.engine.getProperty('voices')
            if voices:
                # Prefer English voices
                for voice in voices:
                    if 'english' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
        except Exception as e:
            print(f"Warning: Failed to initialize pyttsx3: {e}")
            print("Falling back to direct espeak if available")
            if ESPEAK_AVAILABLE:
                self.use_espeak_direct = True
                self.espeak_cmd = 'espeak-ng' if shutil.which('espeak-ng') else 'espeak'
            else:
                self.enabled = False
    
    def _worker(self):
        """Worker thread that processes message queue"""
        # Initialize engine in this thread
        self._init_engine()
        
        if not self.enabled:
            return
        
        while self.running:
            try:
                # Get message with timeout
                message = self.message_queue.get(timeout=0.5)
                
                # Check throttling
                current_time = time.time()
                
                # Global cooldown
                if current_time - self.last_global_announce < config.GLOBAL_COOLDOWN:
                    time.sleep(config.GLOBAL_COOLDOWN - (current_time - self.last_global_announce))
                    current_time = time.time()
                
                # Per-message cooldown
                if message in self.last_announced:
                    time_since_last = current_time - self.last_announced[message]
                    if time_since_last < config.MESSAGE_COOLDOWN:
                        # Skip this message (too soon)
                        continue
                
                # Also check for similar messages (fuzzy match to reduce repetition)
                should_skip = False
                for prev_msg, prev_time in list(self.last_announced.items()):
                    time_since = current_time - prev_time
                    if time_since < config.MESSAGE_COOLDOWN:
                        # Check if messages are similar (same classes mentioned)
                        # Extract key words from both messages
                        msg_words = set(message.lower().split())
                        prev_words = set(prev_msg.lower().split())
                        
                        # Remove common words
                        common_words = {'on', 'your', 'and', 'the', 'a', 'an', 'in', '2', '3', '4', '5'}
                        msg_words -= common_words
                        prev_words -= common_words
                        
                        # If significant overlap (>50% of words), skip
                        if msg_words and prev_words:
                            overlap = len(msg_words & prev_words) / min(len(msg_words), len(prev_words))
                            if overlap > 0.6:
                                should_skip = True
                                break
                
                if should_skip:
                    continue
                
                # Speak the message
                try:
                    print(f"🔊 {message}")
                    
                    if self.use_espeak_direct:
                        # Use espeak directly via subprocess (more reliable)
                        subprocess.run(
                            [self.espeak_cmd, '-s', str(self.rate), message],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            timeout=10
                        )
                    else:
                        # Use pyttsx3
                        self.engine.say(message)
                        self.engine.runAndWait()
                except subprocess.TimeoutExpired:
                    print(f"Warning: TTS timeout for message: {message}")
                except Exception as e:
                    print(f"Warning: TTS error: {e}")
                
                # Update timestamps
                self.last_announced[message] = current_time
                self.last_global_announce = current_time
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in announcer worker: {e}")
    
    def announce(self, message: str, priority: bool = False):
        """
        Queue a message for announcement
        
        Args:
            message: Text to speak
            priority: If True, clear queue and speak immediately (for urgent messages)
        """
        if not self.enabled:
            return
        
        if priority:
            # Clear queue for urgent message
            while not self.message_queue.empty():
                try:
                    self.message_queue.get_nowait()
                except queue.Empty:
                    break
        
        self.message_queue.put(message)
    
    def generate_message(self, zone_dict: Dict[str, List[ZoneDetection]]) -> Optional[str]:
        """
        Generate a concise message from zone detections
        
        Args:
            zone_dict: Dictionary mapping zone names to detections
            
        Returns:
            Message string or None if nothing to announce
        """
        if not zone_dict:
            return None
        
        # Collect all detections across zones, sorted by priority
        all_detections = []
        for zone, detections in zone_dict.items():
            all_detections.extend(detections)
        
        # Sort by priority (highest first)
        all_detections.sort(key=lambda x: x.priority, reverse=True)
        
        # Take top N detections
        top_detections = all_detections[:config.MAX_ANNOUNCE_OBJECTS]
        
        if not top_detections:
            return None
        
        # Group by class and zone
        class_zone_count = defaultdict(lambda: defaultdict(int))
        for zd in top_detections:
            class_zone_count[zd.detection.class_name][zd.zone] += 1
        
        # Build message parts - sort by priority to ensure consistent ordering
        parts = []
        # Sort class names by priority (get max priority for each class)
        class_priorities = []
        for class_name in class_zone_count.keys():
            priority = config.CLASS_PRIORITIES.get(class_name, 0)
            class_priorities.append((priority, class_name))
        class_priorities.sort(reverse=True)
        
        for _, class_name in class_priorities:
            zones = class_zone_count[class_name]
            # Sort zones by left, center, right
            zone_order = {'left': 0, 'center': 1, 'right': 2}
            for zone in sorted(zones.keys(), key=lambda z: zone_order.get(z, 3)):
                count = zones[zone]
                # Use "in front" for center, "on your left/right" for sides
                if zone == 'center':
                    location = "in front"
                else:
                    location = f"on your {zone}"
                
                if count == 1:
                    part = f"{class_name} {location}"
                else:
                    part = f"{count} {self._pluralize(class_name)} {location}"
                parts.append(part)
        
        # Combine parts
        if len(parts) == 1:
            message = parts[0]
        elif len(parts) == 2:
            message = f"{parts[0]} and {parts[1]}"
        else:
            message = ", ".join(parts[:-1]) + f", and {parts[-1]}"
        
        return message
    
    def _pluralize(self, word: str) -> str:
        """Simple pluralization"""
        if word.endswith('s') or word.endswith('ch') or word.endswith('sh'):
            return word + "es"
        elif word.endswith('y') and word[-2] not in 'aeiou':
            return word[:-1] + "ies"
        else:
            return word + "s"
    
    def announce_detections(self, zone_dict: Dict[str, List[ZoneDetection]], priority: bool = False):
        """
        Generate and announce message from detections
        
        Args:
            zone_dict: Dictionary mapping zone names to detections
            priority: If True, announce immediately (urgent)
        """
        message = self.generate_message(zone_dict)
        if message:
            self.announce(message, priority=priority)
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.stop()
