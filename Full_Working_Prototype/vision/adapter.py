import json
import requests
from datetime import datetime, timezone

BACKEND_URL = "http://127.0.0.1:8000/api/vision"
SOURCE_FILE = "day4_traffic_analysis.json"

def adapt_and_post():
    with open(SOURCE_FILE, "r") as f:
        raw = json.load(f)

    # Map her aggregate totals into contract's per-class counts.
    # She doesn't break vehicles into car/bus/truck/motorcycle/bicycle,
    # so everything vehicle-side lands under "car" as a placeholder
    # until her script reports classes separately.
    counts = {
        "car": raw.get("total_vehicle_detections", 0),
        "bus": 0, "truck": 0, "motorcycle": 0, "bicycle": 0,
        "person": raw.get("total_people_detections", 0)
    }

    # Contract only allows normal/vulnerable_user/emergency_vehicle.
    # Her "vehicle_congestion" isn't a legal value yet, so it maps to
    # "normal" here until the team decides whether to add a 4th mode.
    raw_mode = raw.get("priority_mode", "normal")
    priority_mode = raw_mode if raw_mode in ("normal", "vulnerable_user", "emergency_vehicle") else "normal"

    # Using the documented >=10 threshold here rather than her
    # people_in_zone > 0 check, pending her fixing it upstream.
    platoon_detected = raw.get("people_zone_detections", 0) >= 10

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "intersection_id": "vadapalani_junction",
        "zone": "crosswalk_north",
        "counts": counts,
        "platoon_detected": platoon_detected,
        "tracked_objects": [],
        "ev_detected": []
    }

    response = requests.post(BACKEND_URL, json=payload)
    print(f"Status: {response.status_code}")
    print(response.json())

if __name__ == "__main__":
    adapt_and_post()
