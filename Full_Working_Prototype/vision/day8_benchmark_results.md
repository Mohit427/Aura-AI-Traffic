\# Day 8 — Vision Latency / FPS Benchmark



\## Baseline



Model: YOLOv8n  

Video: `demo\_footage.f398.mp4`  

Video FPS: 25.0  

Frames benchmarked: 500



| Metric | Result |

|---|---:|

| Average inference | 83.3 ms |

| Effective inference FPS | 12.0 FPS |

| P95 inference | 126.2 ms |



\## Observations



The YOLOv8n vision pipeline processes approximately 12 inference frames per second on the current development machine.



The benchmark was limited to 500 frames to provide a representative latency measurement without processing the entire 51,201-frame video.



No frame-skipping optimization was applied for this baseline.



\## Optimization decision



Frame skipping was not applied at this stage because the required end-to-end AURA decision-loop target has not yet been specified by the backend/engine team.



A frame-skip comparison can be performed later if the end-to-end latency target requires it.

