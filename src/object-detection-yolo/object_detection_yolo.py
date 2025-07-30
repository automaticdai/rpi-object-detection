# Use Ultralytics YOLO to detect objects in a video stream
import cv2
from ultralytics import YOLO

def main():
    # Load a YOLO11n PyTorch model
    model = YOLO("yolo11n.pt")

    # Open default camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to grab frame.")
            break

        # Run YOLO inference on the frame
        results = model(frame)

        # Draw results on the frame
        annotated_frame = results[0].plot()

        # Show the frame
        cv2.imshow("YOLOv11 Object Detection", annotated_frame)

        # Exit on 'q' or ESC key
        key = cv2.waitKey(1)
        if key == 27 or key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
