import cv2
import json

from ultralytics import YOLO
from day3_speed import estimate_speed, SCALE_FACTOR


# ============================================================
# AURA AI - DAY 5
# EV DISTANCE / VELOCITY / TIME-TO-INTERSECTION
# ============================================================

VIDEO_PATH = "demo_footage.f398.mp4"
MODEL_PATH = "yolov8n.pt"

CONFIDENCE_THRESHOLD = 0.25

# TEMPORARY stop-line position.
# Replace when proper crossroads footage is available.
STOP_LINE_Y = 500

MAX_FRAMES = 10


# ============================================================
# VEHICLE TRACKER
# ============================================================

class EVTracker:

    def __init__(self, scale_factor, stop_line_y):

        self.scale_factor = scale_factor
        self.stop_line_y = stop_line_y

        # Store previous position for EACH vehicle separately.
        self.previous_positions = {}

    def update(self, track_id, y_current, fps):

        velocity = 0.0

        if track_id in self.previous_positions:

            y_previous = self.previous_positions[track_id]

            # Video-based time difference.
            # This is much more stable than time.time().
            dt = 1.0 / fps

            velocity = estimate_speed(
                y_previous,
                y_current,
                dt,
                self.scale_factor
            )

        # Save current position for this specific vehicle.
        self.previous_positions[track_id] = y_current

        # Distance from vehicle to temporary stop line.
        distance_m = (
            abs(y_current - self.stop_line_y)
            * self.scale_factor
        )

        # Calculate TTI.
        if velocity > 0:

            tti = distance_m / velocity

        else:

            tti = None

        return {
            "distance_m": round(distance_m, 3),
            "velocity_mps": round(velocity, 3),
            "tti_sec": round(tti, 3)
            if tti is not None
            else None
        }


# ============================================================
# LOAD MODEL + VIDEO
# ============================================================

model = YOLO(MODEL_PATH)

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():

    print("ERROR: Could not open video.")
    exit()


fps = cap.get(cv2.CAP_PROP_FPS)

if fps <= 0:
    fps = 30.0


tracker = EVTracker(
    scale_factor=SCALE_FACTOR,
    stop_line_y=STOP_LINE_Y
)


# ============================================================
# PROCESS VIDEO
# ============================================================

frame_index = 0

tti_records = []


while cap.isOpened() and frame_index < MAX_FRAMES:

    ok, frame = cap.read()

    if not ok:
        break

    # --------------------------------------------------------
    # YOLO TRACKING
    # --------------------------------------------------------

    results = model.track(
        frame,
        classes=[2, 5, 7],
        conf=CONFIDENCE_THRESHOLD,
        persist=True,
        verbose=False
    )

    result = results[0]

    if result.boxes is not None and result.boxes.id is not None:

        track_ids = result.boxes.id.int().cpu().tolist()

        boxes = result.boxes.xyxy.cpu().tolist()

        confidences = result.boxes.conf.cpu().tolist()

        classes = result.boxes.cls.int().cpu().tolist()


        # ----------------------------------------------------
        # PROCESS EACH TRACKED VEHICLE
        # ----------------------------------------------------

        for track_id, box, confidence, cls in zip(
            track_ids,
            boxes,
            confidences,
            classes
        ):

            x1, y1, x2, y2 = box

            # Bottom-center of vehicle.
            vehicle_y = float(y2)

            tti_data = tracker.update(
                track_id,
                vehicle_y,
                fps
            )

            record = {
                "frame": frame_index,
                "track_id": track_id,
                "class_id": cls,
                "confidence": round(confidence, 3),
                **tti_data
            }

            tti_records.append(record)

            print(
                f"Frame {frame_index} | "
                f"Vehicle {track_id} | "
                f"distance={tti_data['distance_m']} m | "
                f"velocity={tti_data['velocity_mps']} m/s | "
                f"TTI={tti_data['tti_sec']} sec"
            )


    frame_index += 1


# ============================================================
# CLEANUP
# ============================================================

cap.release()


# ============================================================
# SAVE RESULTS
# ============================================================

output = {

    "frames_processed": frame_index,

    "video_fps": round(fps, 3),

    "stop_line_y": STOP_LINE_Y,

    "scale_factor": SCALE_FACTOR,

    "confidence_threshold": CONFIDENCE_THRESHOLD,

    "tracking_enabled": True,

    "records": tti_records
}


with open(
    "day5_tti.json",
    "w"
) as f:

    json.dump(
        output,
        f,
        indent=2
    )


# ============================================================
# SUMMARY
# ============================================================

unique_tracks = set()

for record in tti_records:
    unique_tracks.add(record["track_id"])


print()
print("DAY 5 TTI ANALYSIS")
print("------------------")
print(f"Frames processed : {frame_index}")
print(f"Video FPS        : {fps:.2f}")
print(f"Stop line Y      : {STOP_LINE_Y}")
print(f"Scale factor     : {SCALE_FACTOR}")
print(f"Tracked vehicles : {len(unique_tracks)}")
print(f"TTI records      : {len(tti_records)}")
print()
print("Saved to day5_tti.json")