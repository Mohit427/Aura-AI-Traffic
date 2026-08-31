from ultralytics import YOLO
import cv2
import json
import time
from datetime import datetime, timezone


print("Starting Day 2...")
print("Loading YOLO model...")

model = YOLO("yolov8n.pt")

print("Opening video...")

cap = cv2.VideoCapture("demo_footage.f398.mp4")

if not cap.isOpened():
    print("ERROR: Could not open video.")
    exit()

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)

print("Video opened successfully!")
print("Total frames:", total_frames)
print("FPS:", fps)


# YOLO COCO class IDs
CLASS_MAP = {
    0: "person",
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck"
}


def frame_to_record(results):
    counts = {
        "car": 0,
        "bus": 0,
        "truck": 0,
        "motorcycle": 0,
        "bicycle": 0,
        "person": 0
    }

    for box in results[0].boxes:

        cls_id = int(box.cls[0])

        if cls_id in CLASS_MAP:
            class_name = CLASS_MAP[cls_id]
            counts[class_name] += 1

    return {
        "timestamp": time.time(),
        "timestamp_iso": datetime.now(timezone.utc).isoformat(),
        "intersection_id": "vadapalani_junction",
        "zone": "north_approach",
        "location": {
            "lat": 13.0505,
            "lon": 80.2121
        },
        "camera_id": "511ga-11899",
        "counts": counts,
        "platoon_detected": False,
        "tracked_objects": [],
        "ev_detected": []
    }


records = []
idx = 0

print("Starting detection...")


# Safety limit for Day 2 testing
MAX_FRAMES = 500


while cap.isOpened() and idx < MAX_FRAMES:

    ok, frame = cap.read()

    if not ok:
        break

    results = model(
        frame,
        classes=list(CLASS_MAP.keys()),
        verbose=False
    )

    record = frame_to_record(results)

    records.append(record)

    idx += 1

    if idx % 100 == 0:
        print(f"Processed {idx}/{total_frames} frames")


cap.release()


with open("day2_detections.json", "w") as f:
    json.dump(records, f, indent=2)


print("Detection complete!")
print(f"Saved {len(records)} records to day2_detections.json")