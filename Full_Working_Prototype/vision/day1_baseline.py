from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")

cap = cv2.VideoCapture("demo_footage.f398.mp4")

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

if fps == 0:
    fps = 30

out = cv2.VideoWriter(
    "day1_output.mp4",
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps,
    (width, height)
)

while cap.isOpened():
    ok, frame = cap.read()

    if not ok:
        break

    results = model(
        frame,
        classes=[0, 1, 2, 3, 5, 7],
        verbose=False
    )

    annotated = results[0].plot()

    out.write(annotated)

cap.release()
out.release()

print("Detection complete!")
print("Output saved as day1_output.mp4")