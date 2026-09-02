import cv2
from day7_night_enhance import enhance_low_light


INPUT_VIDEO = "demo_footage.f398.mp4"
OUTPUT_VIDEO = "day7_enhanced_preview.mp4"

cap = cv2.VideoCapture(INPUT_VIDEO)

if not cap.isOpened():
    print("ERROR: Could not open video.")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*"mp4v")

out = cv2.VideoWriter(
    OUTPUT_VIDEO,
    fourcc,
    fps,
    (width, height)
)

MAX_FRAMES = 100
idx = 0

while cap.isOpened() and idx < MAX_FRAMES:

    ok, frame = cap.read()

    if not ok:
        break

    enhanced = enhance_low_light(frame)

    out.write(enhanced)

    idx += 1

cap.release()
out.release()

print("Day 7 enhancement test complete.")
print(f"Frames processed: {idx}")
print(f"Saved: {OUTPUT_VIDEO}")