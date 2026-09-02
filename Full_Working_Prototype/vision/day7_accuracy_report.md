\# Day 7 — Vision Accuracy Report



\## Model



YOLOv8n



\## Classes



\- person

\- bicycle

\- car

\- motorcycle

\- bus

\- truck



\## Scenarios



Approximately 100 frames were considered for each test scenario.



| Scenario | Precision | Recall | Notes |

|---|---:|---:|---|

| Daylight, clear | TBD | TBD | Baseline frame detection |

| Night / low-light | TBD | TBD | CLAHE enhancement tested |

| Partial occlusion | TBD | TBD | YOLO tracking with persistent IDs tested |



\## Daylight



The existing Day 2 YOLO detection pipeline was used as the baseline.



\## Night / Low-Light



CLAHE-based low-light enhancement was implemented in

`day7\_night\_enhance.py`.



The enhanced frames can be passed into YOLO before inference.



\## Occlusion



YOLO tracking mode was tested using:



```python

model.track(

&#x20;   frame,

&#x20;   persist=True,

&#x20;   classes=\[0, 1, 2, 3, 5, 7],

&#x20;   verbose=False

)

