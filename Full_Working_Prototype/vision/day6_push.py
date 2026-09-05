from ultralytics import YOLO
import cv2
import time
import requests
from datetime import datetime, timezone


# ============================================================
# AURA AI - DAY 6
# PUSH VISION DETECTIONS INTO BACKEND
# ============================================================

ENDPOINT = "http://127.0.0.1:8000/api/vision"

VIDEO_PATH = "demo_footage.f398.mp4"
MODEL_PATH = "yolov8n.pt"

MAX_FRAMES = 10


# ============================================================
# YOLO COCO CLASS IDs
# ============================================================

CLASS_MAP = {
    0: "person",
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck"
}


# ============================================================
# BUILD VISION RECORD
# ============================================================

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
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "intersection_id": "vadapalani_junction",
        "zone": "north_approach",
        "counts": counts,
        "platoon_detected": False,
        "tracked_objects": [],
        "ev_detected": []
    }


# ============================================================
# PUSH RECORD TO BACKEND
# ============================================================

def push_record(record, retries=3):

    for attempt in range(1, retries + 1):

        try:

            response = requests.post(
                ENDPOINT,
                json=record,
                timeout=2
            )

            if response.status_code == 200:

                return True

            print(
                f"Backend returned HTTP "
                f"{response.status_code}"
            )

        except requests.RequestException as error:

            print(
                f"Push attempt {attempt} failed: "
                f"{error}"
            )

        if attempt < retries:

            time.sleep(0.5 * attempt)

    return False


# ============================================================
# LOAD MODEL
# ============================================================

print("Starting Day 6...")
print("Loading YOLO model...")

model = YOLO(MODEL_PATH)

print("Opening video...")

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():

    print("ERROR: Could not open video.")

    exit()


print("Video opened successfully!")
print("Backend endpoint:", ENDPOINT)
print("Starting detection + backend push...")


# ============================================================
# PROCESS VIDEO
# ============================================================

idx = 0

successful_pushes = 0
failed_pushes = 0


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


    # --------------------------------------------------------
    # PUSH RECORD
    # --------------------------------------------------------

    success = push_record(record)


    if success:

        successful_pushes += 1

        print(
            f"Frame {idx}: "
            f"PUSHED successfully | "
            f"counts={record['counts']}"
        )

    else:

        failed_pushes += 1

        print(
            f"Frame {idx}: "
            f"PUSH FAILED"
        )


    idx += 1


# ============================================================
# CLEANUP
# ============================================================

cap.release()


# ============================================================
# SUMMARY
# ============================================================

print()
print("DAY 6 VISION → BACKEND")
print("----------------------")
print(f"Frames processed : {idx}")
print(f"Successful pushes: {successful_pushes}")
print(f"Failed pushes    : {failed_pushes}")
print()
print("Day 6 push test complete.")