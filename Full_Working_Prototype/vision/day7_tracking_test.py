from ultralytics import YOLO
import cv2


MODEL_PATH = "yolov8n.pt"
VIDEO_PATH = "demo_footage.f398.mp4"

CLASS_IDS = [0, 1, 2, 3, 5, 7]

MAX_FRAMES = 100


print("Starting Day 7 tracking test...")
print("Loading YOLO model...")

model = YOLO(MODEL_PATH)

print("Opening video...")

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print("ERROR: Could not open video.")
    exit()

idx = 0
tracked_ids = set()

while cap.isOpened() and idx < MAX_FRAMES:

    ok, frame = cap.read()

    if not ok:
        break

    results = model.track(
        frame,
        persist=True,
        classes=CLASS_IDS,
        verbose=False
    )

    result = results[0]

    if result.boxes.id is not None:

        ids = result.boxes.id.int().cpu().tolist()

        for object_id in ids:
            tracked_ids.add(object_id)

    idx += 1

cap.release()

print()
print("DAY 7 TRACKING TEST")
print("-------------------")
print(f"Frames processed : {idx}")
print(f"Unique track IDs : {len(tracked_ids)}")
print("Tracking test complete.")