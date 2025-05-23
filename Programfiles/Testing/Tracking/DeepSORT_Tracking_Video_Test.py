import cv2
import time
import os
from DetectorDeepSort import YoloDetector
from TrackerDeepSort import Tracker

MODEL_PATH = "../../../Models/customYolov8n.pt"
VIDEO_PATH = "../Test_Videos/Tracking_occlution.mp4"

image_save_path = os.path.join(os.path.dirname(__file__), "..", "Results", "Tracking", "saved_frames_deepsort_occlusion_torchreid_1")
image_save_path = os.path.normpath(image_save_path)
os.makedirs(image_save_path, exist_ok=True)

frame_count = 0

def main():
  detector = YoloDetector(model_path=MODEL_PATH, confidence=0.6)
  tracker = Tracker()
  global frame_count

  cap = cv2.VideoCapture(VIDEO_PATH)

  if not cap.isOpened():
    print("Error: Unable to open video file.")
    exit()

  while True:
    ret, frame = cap.read()
    if not ret:
      break

    start_time = time.perf_counter()
    detections = detector.detect(frame)
    tracking_ids, boxes = tracker.track(detections, frame)

    for tracking_id, bounding_box in zip(tracking_ids, boxes):
      cv2.rectangle(frame, (int(bounding_box[0]), int(bounding_box[1])), (int(
          bounding_box[2]), int(bounding_box[3])), (0, 0, 255), 2)
      cv2.putText(frame, f"{str(tracking_id)}", (int(bounding_box[0]), int(
          bounding_box[1] - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    end_time = time.perf_counter()
    fps = 1 / (end_time - start_time)
    print(f"Current fps: {fps}")

    cv2.imshow("Frame", frame)


    frame_id = frame_count
    image_filename = f"frame_{frame_id:05d}.jpg"
    image_path = os.path.join(image_save_path, image_filename)
    cv2.imwrite(image_path, frame)
    cap.grab()
    frame_count += 1

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q") or key == 27:
      break

  cap.release()
  cv2.destroyAllWindows()


if __name__ == "__main__":
  main()