import cv2
import json
from ultralytics import YOLO

VIDEO_PATH = "demo_footage.f398.mp4"
MODEL_PATH = "yolov8n.pt"

CONFIDENCE_THRESHOLD = 0.25

# Crosswalk / VUI zone from Day 3
CROSSWALK_ZONE = [
    [333, 382],
    [881, 330],
    [1125, 623],
    [225, 619]
]


def point_in_zone(cx, cy, zone):
    import cv2
    import numpy as np

    polygon = np.array(zone, dtype=np.int32)

    return cv2.pointPolygonTest(
        polygon,
        (float(cx), float(cy)),
        False
    ) >= 0


model = YOLO(MODEL_PATH)

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print("ERROR: Could not open video.")
    exit()

frame_count = 0
MAX_FRAMES = 100

total_vehicles = 0
total_people = 0
vehicles_in_zone = 0
people_in_zone = 0

while frame_count < MAX_FRAMES:

    ret, frame = cap.read()

    if not ret:
        break

    frame_count += 1

    results = model(
        frame,
        classes=[0, 1, 2, 3, 5, 7],
        conf=CONFIDENCE_THRESHOLD,
        verbose=False
    )

    for result in results:

        if result.boxes is None:
            continue

        for box in result.boxes:

            cls = int(box.cls[0])
            confidence = float(box.conf[0])

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0]
            )

            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            # COCO classes:
            # 0 = person
            # 1 = bicycle
            # 2 = car
            # 3 = motorcycle
            # 5 = bus
            # 7 = truck

            if cls == 0:

                total_people += 1

                if point_in_zone(cx, cy, CROSSWALK_ZONE):
                    people_in_zone += 1

            else:

                total_vehicles += 1

                if point_in_zone(cx, cy, CROSSWALK_ZONE):
                    vehicles_in_zone += 1


cap.release()

if people_in_zone > 0:
    priority_mode = "vulnerable_user"
    traffic_level = "high"
elif vehicles_in_zone >= 500:
    priority_mode = "vehicle_congestion"
    traffic_level = "high"
elif vehicles_in_zone >= 200:
    priority_mode = "vehicle_congestion"
    traffic_level = "medium"
else:
    priority_mode = "normal"
    traffic_level = "low"

traffic_data = {
    "frames_processed": frame_count,
    "confidence_threshold": CONFIDENCE_THRESHOLD,
    "total_vehicle_detections": total_vehicles,
    "total_people_detections": total_people,
    "vehicle_zone_detections": vehicles_in_zone,
    "people_zone_detections": people_in_zone,
    "priority_mode": priority_mode,
    "traffic_level": traffic_level,
}


with open(
    "day4_traffic_analysis.json",
    "w"
) as f:

    json.dump(
        traffic_data,
        f,
        indent=2
    )


print()
print("AURA TRAFFIC STATE")
print("------------------")
print(f"Frames processed: {frame_count}")
print(f"Vehicle detections: {total_vehicles}")
print(f"People detections: {total_people}")
print(f"Vehicles in zone: {vehicles_in_zone}")
print(f"People in zone: {people_in_zone}")
print(f"Traffic level : {traffic_level}")
print(f"Priority mode : {priority_mode}")
print()
print("Saved to day4_traffic_analysis.json")