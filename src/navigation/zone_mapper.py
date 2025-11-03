# ------------------------------------------------------------------------------
# Zone Mapper Module
# ------------------------------------------------------------------------------
# Maps detections to spatial zones (left/center/right) and applies filtering
# ------------------------------------------------------------------------------

from typing import List, Dict, Tuple, Optional
from collections import defaultdict, deque
import time
import math

from .detector import Detection
from . import config


class ZoneDetection:
    """Detection with zone information"""
    def __init__(self, detection: Detection, zone: str, priority: int):
        self.detection = detection
        self.zone = zone
        self.priority = priority
        self.timestamp = time.time()
        
    def __repr__(self):
        return f"ZoneDetection({self.detection.class_name} in {self.zone}, pri={self.priority})"


class ZoneMapper:
    """Maps detections to zones and applies temporal filtering"""
    
    def __init__(self, frame_width: int = None):
        """
        Initialize zone mapper
        
        Args:
            frame_width: Width of camera frame for zone calculation
        """
        self.frame_width = frame_width or config.CAMERA_WIDTH
        
        # Zone boundaries
        self.left_boundary = self.frame_width * config.ZONE_LEFT_END
        self.right_boundary = self.frame_width * config.ZONE_RIGHT_START
        
        # Tracking for persistence filtering
        # Key: (class_name, zone), Value: deque of recent detections
        self.detection_history = defaultdict(lambda: deque(maxlen=config.PERSISTENCE_FRAMES))
        
        print(f"ZoneMapper ready (L:{self.left_boundary:.0f}, R:{self.right_boundary:.0f})")
        
    def get_zone(self, center_x: float) -> str:
        """
        Determine which zone a detection belongs to
        
        Args:
            center_x: X coordinate of object center
            
        Returns:
            'left', 'center', or 'right'
        """
        if center_x < self.left_boundary:
            return 'left'
        elif center_x > self.right_boundary:
            return 'right'
        else:
            return 'center'
    
    def get_priority(self, class_name: str) -> int:
        """Get priority for a class (higher = more important)"""
        return config.CLASS_PRIORITIES.get(class_name, 0)
    
    def map_detections(self, detections: List[Detection]) -> List[ZoneDetection]:
        """
        Map detections to zones with priority
        
        Args:
            detections: List of Detection objects
            
        Returns:
            List of ZoneDetection objects
        """
        zone_detections = []
        
        for det in detections:
            zone = self.get_zone(det.center_x)
            priority = self.get_priority(det.class_name)
            
            zone_det = ZoneDetection(
                detection=det,
                zone=zone,
                priority=priority
            )
            zone_detections.append(zone_det)
        
        return zone_detections
    
    def apply_persistence_filter(self, zone_detections: List[ZoneDetection]) -> List[ZoneDetection]:
        """
        Filter detections to only keep those that persist across frames
        
        Args:
            zone_detections: Current frame detections
            
        Returns:
            Filtered detections that have persisted
        """
        # Update history with current detections
        current_keys = set()
        for zd in zone_detections:
            key = (zd.detection.class_name, zd.zone)
            current_keys.add(key)
            self.detection_history[key].append(time.time())
        
        # Remove old entries from history (cleanup)
        keys_to_remove = []
        current_time = time.time()
        for key in self.detection_history:
            if key not in current_keys:
                # Remove entries older than 1 second
                history = self.detection_history[key]
                while history and current_time - history[0] > 1.0:
                    history.popleft()
                if not history:
                    keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.detection_history[key]
        
        # Filter: only keep detections that have appeared enough times
        filtered = []
        for zd in zone_detections:
            key = (zd.detection.class_name, zd.zone)
            history_count = len(self.detection_history[key])
            
            if history_count >= config.PERSISTENCE_FRAMES:
                filtered.append(zd)
        
        return filtered
    
    def aggregate_by_zone(self, zone_detections: List[ZoneDetection]) -> Dict[str, List[ZoneDetection]]:
        """
        Group detections by zone
        
        Returns:
            Dict mapping zone name to list of detections in that zone
        """
        by_zone = defaultdict(list)
        for zd in zone_detections:
            by_zone[zd.zone].append(zd)
        
        # Sort each zone by priority (highest first)
        for zone in by_zone:
            by_zone[zone].sort(key=lambda x: x.priority, reverse=True)
        
        return dict(by_zone)
    
    def process(self, detections: List[Detection]) -> Dict[str, List[ZoneDetection]]:
        """
        Full processing pipeline: map to zones, filter, and aggregate
        
        Args:
            detections: Raw detections from detector
            
        Returns:
            Dict of zone -> filtered detections
        """
        # Map to zones
        zone_detections = self.map_detections(detections)
        
        # Apply persistence filter
        filtered = self.apply_persistence_filter(zone_detections)
        
        # Aggregate by zone
        by_zone = self.aggregate_by_zone(filtered)
        
        return by_zone
