from ultralytics import YOLO
import requests
import json
from datetime import datetime, timezone

model = YOLO("yolov8n.pt")
BACKEND_URL = "http://127.0.0.1:8000/api/vision"

CLASS_MAP = {2: "car", 5: "bus", 7: "truck", 3: "motorcycle", 1: "bicycle", 0: "person"}

def run_continuous(video_path, intersection_id="vadapalani_junction", zone="crosswalk_north", post_every_n_frames=10):
    results = model.predict(source=video_path, stream=True, conf=0.4, verbose=False)

    frame_num = 0
    for frame_result in results:
        frame_num += 1

        if frame_num % post_every_n_frames != 0:
            continue

        counts = {"car": 0, "bus": 0, "truck": 0, "motorcycle": 0, "bicycle": 0, "person": 0}
        if frame_result.boxes is not None:
            for box in frame_result.boxes:
                cls_id = int(box.cls[0])
                if cls_id in CLASS_MAP:
                    counts[CLASS_MAP[cls_id]] += 1

        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "intersection_id": intersection_id,
            "zone": zone,
            "counts": counts,
            "platoon_detected": counts["person"] + counts["bicycle"] >= 10,
            "tracked_objects": [],
            "ev_detected": []
        }

        try:
            response = requests.post(BACKEND_URL, json=payload)
            print(f"Frame {frame_num}: posted, status {response.status_code}, counts={counts}")
        except requests.exceptions.ConnectionError:
            print(f"Frame {frame_num}: backend not reachable")

if __name__ == "__main__":
    run_continuous("demo_footage.f398.mp4")
