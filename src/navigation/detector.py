# ------------------------------------------------------------------------------
# Object Detector Module
# ------------------------------------------------------------------------------
# Runs YOLO inference and returns structured detection results
# ------------------------------------------------------------------------------

import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Tuple
import time

from . import config


class Detection:
    """Structured detection result"""
    def __init__(self, class_name: str, confidence: float, bbox: Tuple[int, int, int, int]):
        self.class_name = class_name
        self.confidence = confidence
        self.bbox = bbox  # (x1, y1, x2, y2)
        self.center_x = (bbox[0] + bbox[2]) / 2
        self.center_y = (bbox[1] + bbox[3]) / 2
        self.width = bbox[2] - bbox[0]
        self.height = bbox[3] - bbox[1]
        self.area = self.width * self.height
        
    def __repr__(self):
        return f"Detection({self.class_name}, conf={self.confidence:.2f}, center=({self.center_x:.0f},{self.center_y:.0f}))"


class ObjectDetector:
    """YOLO-based object detector"""
    
    def __init__(self, model_path: str = None, conf_threshold: float = None):
        """
        Initialize detector
        
        Args:
            model_path: Path to YOLO model weights
            conf_threshold: Confidence threshold (0-1)
        """
        self.model_path = model_path or config.YOLO_MODEL
        self.conf_threshold = conf_threshold or config.CONFIDENCE_THRESHOLD
        
        print(f"Loading YOLO model: {self.model_path}")
        self.model = YOLO(self.model_path)
        
        # Set model parameters
        self.model.overrides['conf'] = self.conf_threshold
        self.model.overrides['iou'] = config.IOU_THRESHOLD
        self.model.overrides['verbose'] = False
        
        print(f"Detector ready (conf={self.conf_threshold}, iou={config.IOU_THRESHOLD})")
        
    def detect(self, frame: np.ndarray) -> List[Detection]:
        """
        Run detection on a frame
        
        Args:
            frame: BGR image from OpenCV
            
        Returns:
            List of Detection objects
        """
        # Run inference
        results = self.model(frame, verbose=False)
        
        # Parse results
        detections = []
        for result in results:
            boxes = result.boxes
            for i in range(len(boxes)):
                # Extract data
                bbox = boxes.xyxy[i].cpu().numpy().astype(int)  # x1, y1, x2, y2
                conf = float(boxes.conf[i].cpu().numpy())
                cls_id = int(boxes.cls[i].cpu().numpy())
                class_name = result.names[cls_id]
                
                # Create detection object
                detection = Detection(
                    class_name=class_name,
                    confidence=conf,
                    bbox=tuple(bbox)
                )
                detections.append(detection)
        
        return detections
    
    def detect_with_timing(self, frame: np.ndarray) -> Tuple[List[Detection], float]:
        """
        Run detection and return results with inference time
        
        Returns:
            (detections, inference_time_ms)
        """
        start = time.time()
        detections = self.detect(frame)
        elapsed = (time.time() - start) * 1000
        return detections, elapsed
