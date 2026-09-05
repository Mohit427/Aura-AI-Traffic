import time
from ultralytics import YOLO
import cv2


print("Starting Day 8...")
print("Loading YOLO model...")

model = YOLO("yolov8n.pt")

print("Opening video...")

cap = cv2.VideoCapture("demo_footage.f398.mp4")

if not cap.isOpened():
    print("ERROR: Could not open video.")
    exit()

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
video_fps = cap.get(cv2.CAP_PROP_FPS)

print("Video opened successfully!")
print("Total frames:", total_frames)
print("Video FPS:", video_fps)

times = []

idx = 0

MAX_FRAMES = 500

print(f"Starting inference benchmark on {MAX_FRAMES} frames...")

while cap.isOpened() and idx < MAX_FRAMES:

    ok, frame = cap.read()

    if not ok:
        break

    t0 = time.time()

    model(
        frame,
        classes=[0, 1, 2, 3, 5, 7],
        verbose=False
    )

    inference_time = time.time() - t0
    times.append(inference_time)

    idx += 1

    if idx % 50 == 0:
        print(f"Processed {idx} frames...")


cap.release()


if not times:
    print("ERROR: No frames were processed.")
    exit()


avg = sum(times) / len(times)

sorted_times = sorted(times)

p95_index = int(len(sorted_times) * 0.95)

if p95_index >= len(sorted_times):
    p95_index = len(sorted_times) - 1

p95 = sorted_times[p95_index]

effective_fps = 1 / avg


print()
print("DAY 8 VISION BENCHMARK")
print("-----------------------")
print(f"Frames benchmarked : {len(times)}")
print(f"Average inference  : {avg * 1000:.1f} ms")
print(f"Effective FPS      : {effective_fps:.1f}")
print(f"P95 inference      : {p95 * 1000:.1f} ms")
print()
print("Benchmark complete.")