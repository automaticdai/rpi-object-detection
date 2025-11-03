#!/usr/bin/env python3
# ------------------------------------------------------------------------------
# Navigation System Main Runner
# ------------------------------------------------------------------------------
# Main application for visually impaired navigation using YOLO + zones + TTS
# ------------------------------------------------------------------------------

import cv2
import sys
import time
import argparse
from typing import Optional

from . import config
from .detector import ObjectDetector
from .zone_mapper import ZoneMapper
from .announcer import AudioAnnouncer
from .sensor import UltrasonicSensor


class NavigationSystem:
    """Main navigation system coordinator"""
    
    def __init__(self, 
                 camera_id: int = 0,
                 model_path: str = None,
                 enable_tts: bool = True,
                 show_video: bool = True):
        """
        Initialize navigation system
        
        Args:
            camera_id: Camera device ID
            model_path: Path to YOLO model
            enable_tts: Enable text-to-speech
            show_video: Show video window with detections
        """
        self.camera_id = camera_id
        self.show_video = show_video
        
        print("=" * 60)
        print("NAVIGATION SYSTEM FOR VISUALLY IMPAIRED")
        print("=" * 60)
        
        # Initialize camera
        print(f"\nInitializing camera {camera_id}...")
        self.cap = cv2.VideoCapture(camera_id)
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera {camera_id}")
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, config.CAMERA_FPS)
        
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Camera opened: {actual_width}x{actual_height}")
        
        # Initialize components
        print("\nInitializing detection system...")
        self.detector = ObjectDetector(model_path=model_path)
        self.zone_mapper = ZoneMapper(frame_width=actual_width)
        self.announcer = AudioAnnouncer(enabled=enable_tts)
        self.sensor = UltrasonicSensor(enabled=config.ULTRASONIC_ENABLED)
        
        # Stats
        self.frame_count = 0
        self.start_time = time.time()
        self.fps_history = []
        
        print("\n" + "=" * 60)
        print("System ready! Press 'q' or ESC to quit")
        print("=" * 60 + "\n")
    
    def draw_zones(self, frame):
        """Draw zone boundaries on frame"""
        height, width = frame.shape[:2]
        
        # Zone boundaries
        left_x = int(self.zone_mapper.left_boundary)
        right_x = int(self.zone_mapper.right_boundary)
        
        # Draw vertical lines
        cv2.line(frame, (left_x, 0), (left_x, height), (255, 255, 0), 2)
        cv2.line(frame, (right_x, 0), (right_x, height), (255, 255, 0), 2)
        
        # Draw labels
        cv2.putText(frame, "LEFT", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(frame, "CENTER", (left_x + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(frame, "RIGHT", (right_x + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    
    def draw_detections(self, frame, zone_dict):
        """Draw bounding boxes and labels on frame"""
        # Colors for zones
        zone_colors = {
            'left': (255, 0, 0),    # Blue
            'center': (0, 255, 0),  # Green
            'right': (0, 0, 255),   # Red
        }
        
        for zone, detections in zone_dict.items():
            color = zone_colors.get(zone, (255, 255, 255))
            
            for zd in detections:
                det = zd.detection
                x1, y1, x2, y2 = det.bbox
                
                # Draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                # Draw label
                label = f"{det.class_name} ({det.confidence:.2f})"
                label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                cv2.rectangle(frame, (x1, y1 - label_size[1] - 4), (x1 + label_size[0], y1), color, -1)
                cv2.putText(frame, label, (x1, y1 - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    def process_frame(self, frame):
        """Process a single frame"""
        # Run detection
        detections, inference_time = self.detector.detect_with_timing(frame)
        
        # Map to zones and filter
        zone_dict = self.zone_mapper.process(detections)
        
        # Check ultrasonic sensor (if enabled)
        if self.sensor.enabled:
            distance = self.sensor.read_distance()
            if distance and distance < config.ULTRASONIC_CRITICAL_DISTANCE:
                # Priority announcement for obstacle
                self.announcer.announce("Stop! Obstacle ahead!", priority=True)
        
        # Announce detections
        self.announcer.announce_detections(zone_dict)
        
        # Update stats
        self.frame_count += 1
        
        return zone_dict, inference_time
    
    def run(self):
        """Main processing loop"""
        try:
            while True:
                # Read frame
                ret, frame = self.cap.read()
                if not ret:
                    print("Error: Failed to read frame")
                    break
                
                frame_start = time.time()
                
                # Process frame
                zone_dict, inference_time = self.process_frame(frame)
                
                # Calculate FPS
                frame_time = (time.time() - frame_start) * 1000
                fps = 1000 / frame_time if frame_time > 0 else 0
                self.fps_history.append(fps)
                if len(self.fps_history) > 30:
                    self.fps_history.pop(0)
                avg_fps = sum(self.fps_history) / len(self.fps_history)
                
                # Display video with annotations
                if self.show_video:
                    display_frame = frame.copy()
                    self.draw_zones(display_frame)
                    self.draw_detections(display_frame, zone_dict)
                    
                    # Draw stats
                    stats_text = [
                        f"FPS: {avg_fps:.1f}",
                        f"Inference: {inference_time:.1f}ms",
                        f"Frame: {frame_time:.1f}ms",
                        f"Detections: {sum(len(d) for d in zone_dict.values())}",
                    ]
                    
                    y_offset = frame.shape[0] - 20
                    for text in reversed(stats_text):
                        cv2.putText(display_frame, text, (10, y_offset), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                        y_offset -= 20
                    
                    cv2.imshow("Navigation System", display_frame)
                
                # Check for quit
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # q or ESC
                    break
                elif key == ord('m'):  # Toggle mute
                    self.announcer.enabled = not self.announcer.enabled
                    status = "enabled" if self.announcer.enabled else "disabled"
                    print(f"Audio {status}")
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        print("\nCleaning up...")
        
        # Print stats
        elapsed = time.time() - self.start_time
        avg_fps = self.frame_count / elapsed if elapsed > 0 else 0
        print(f"\nSession statistics:")
        print(f"  Frames processed: {self.frame_count}")
        print(f"  Total time: {elapsed:.1f}s")
        print(f"  Average FPS: {avg_fps:.1f}")
        
        # Release resources
        self.cap.release()
        cv2.destroyAllWindows()
        self.announcer.stop()
        self.sensor.cleanup()
        
        print("Cleanup complete")


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Navigation system for visually impaired users",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings
  python -m src.navigation.navigation_system
  
  # Use different camera
  python -m src.navigation.navigation_system --camera 1
  
  # Disable audio for testing
  python -m src.navigation.navigation_system --no-audio
  
  # Headless mode (no video window)
  python -m src.navigation.navigation_system --no-video

Controls:
  q or ESC  - Quit
  m         - Toggle mute/unmute audio
        """
    )
    
    parser.add_argument('--camera', type=int, default=0,
                       help='Camera device ID (default: 0)')
    parser.add_argument('--model', type=str, default=None,
                       help=f'Path to YOLO model (default: {config.YOLO_MODEL})')
    parser.add_argument('--no-audio', action='store_true',
                       help='Disable text-to-speech audio')
    parser.add_argument('--no-video', action='store_true',
                       help='Disable video window (headless mode)')
    
    args = parser.parse_args()
    
    try:
        nav_system = NavigationSystem(
            camera_id=args.camera,
            model_path=args.model,
            enable_tts=not args.no_audio,
            show_video=not args.no_video
        )
        nav_system.run()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
