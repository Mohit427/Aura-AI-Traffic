import cv2
import json
import time
import numpy as np

from ultralytics import YOLO
from scipy.spatial.distance import pdist, squareform


# ============================================================
# AURA AI - DAY 4 TRAFFIC ANALYSIS
# ============================================================

VIDEO_PATH = "demo_footage.f398.mp4"
MODEL_PATH = "yolov8n.pt"

CONFIDENCE_THRESHOLD = 0.25

# Day 3 zone coordinates
PRIORITY_ZONE = np.array([
    [333, 382],
    [881, 330],
    [1125, 623],
    [225, 619]
], dtype=np.int32)


# Day 4 platoon parameters
PLATOON_THRESHOLD = 10
CLUSTER_RADIUS_PX = 80

MAX_FRAMES = 100

INTERSECTION_ID = "trafficvision_511ga_11899"
ZONE_NAME = "priority_zone"


# COCO classes used by our vision pipeline
CLASS_MAP = {
    0: "person",
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck"
}


def in_zone(cx, cy, zone=PRIORITY_ZONE):
    return cv2.pointPolygonTest(
        zone,
        (float(cx), float(cy)),
        False
    ) >= 0


def detect_platoon(centroids):
    """
    Detect a cluster of at least PLATOON_THRESHOLD
    vulnerable road users within CLUSTER_RADIUS_PX.
    """

    if len(centroids) < PLATOON_THRESHOLD:
        return False, 0

    points = np.array(centroids, dtype=np.float32)

    distance_matrix = squareform(
        pdist(points)
    )

    neighbor_counts = (
        distance_matrix < CLUSTER_RADIUS_PX
    ).sum(axis=1)

    max_cluster = int(
        neighbor_counts.max()
    )

    return (
        max_cluster >= PLATOON_THRESHOLD,
        max_cluster
    )


# ============================================================
# MODEL + VIDEO
# ============================================================

model = YOLO(MODEL_PATH)

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print("ERROR: Could not open video.")
    exit()


# ============================================================
# ANALYSIS STATE
# ============================================================

frame_count = 0

total_counts = {
    "car": 0,
    "bus": 0,
    "truck": 0,
    "motorcycle": 0,
    "bicycle": 0,
    "person": 0
}

zone_counts = {
    "car": 0,
    "bus": 0,
    "truck": 0,
    "motorcycle": 0,
    "bicycle": 0,
    "person": 0
}

platoon_detected = False
largest_platoon = 0


# ============================================================
# FRAME LOOP
# ============================================================

while frame_count < MAX_FRAMES:

    ret, frame = cap.read()

    if not ret:
        break

    frame_count += 1

    results = model(
        frame,
        classes=list(CLASS_MAP.keys()),
        conf=CONFIDENCE_THRESHOLD,
        verbose=False
    )

    vulnerable_centroids = []

    for result in results:

        if result.boxes is None:
            continue

        for box in result.boxes:

            cls_id = int(box.cls[0])

            if cls_id not in CLASS_MAP:
                continue

            class_name = CLASS_MAP[cls_id]

            total_counts[class_name] += 1

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0]
            )

            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2

            if in_zone(cx, cy):

                zone_counts[class_name] += 1

                # Day 4 platoon detection
                # person + bicycle are treated as vulnerable users
                if cls_id in (0, 1):
                    vulnerable_centroids.append(
                        (cx, cy)
                    )

    # Check platoon for this frame
    is_platoon, cluster_size = detect_platoon(
        vulnerable_centroids
    )

    if is_platoon:

        platoon_detected = True

        if cluster_size > largest_platoon:
            largest_platoon = cluster_size

        print(
            f"Frame {frame_count}: "
            f"PLATOON DETECTED - size={cluster_size}"
        )


cap.release()


# ============================================================
# PRIORITY DECISION
# ============================================================

if platoon_detected:

    priority_mode = "vulnerable_user"

elif False:

    # Reserved for Day 5/EV integration
    priority_mode = "emergency_vehicle"

else:

    priority_mode = "normal"


# ============================================================
# CONTRACT-COMPATIBLE OUTPUT
# ============================================================

traffic_data = {
    "timestamp": time.time(),
    "intersection_id": INTERSECTION_ID,
    "zone": ZONE_NAME,

    "counts": zone_counts,

    "platoon_detected": platoon_detected,

    "tracked_objects": {
        "total_detections": sum(total_counts.values()),
        "zone_detections": sum(zone_counts.values())
    },

    "ev_detected": False,

    "priority_mode": priority_mode,

    # Useful internal diagnostic information
    "analysis": {
        "frames_processed": frame_count,
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "platoon_threshold": PLATOON_THRESHOLD,
        "cluster_radius_px": CLUSTER_RADIUS_PX,
        "largest_platoon": largest_platoon,
        "total_counts": total_counts
    }
}


# ============================================================
# SAVE
# ============================================================

with open(
    "day4_traffic_analysis.json",
    "w"
) as f:

    json.dump(
        traffic_data,
        f,
        indent=2
    )


# ============================================================
# TERMINAL OUTPUT
# ============================================================

print()
print("AURA TRAFFIC STATE")
print("------------------")
print(f"Frames processed : {frame_count}")
print(f"Zone counts      : {zone_counts}")
print(f"Platoon detected : {platoon_detected}")
print(f"Largest platoon  : {largest_platoon}")
print(f"Priority mode    : {priority_mode}")
print()
print("Saved to day4_traffic_analysis.json")