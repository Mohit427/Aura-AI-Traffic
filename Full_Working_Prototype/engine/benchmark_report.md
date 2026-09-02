# AURA Engine — Day 7 Latency Benchmark Report

- **Component:** C++ Optimization Engine (Edmonds-Karp Max-Flow + EV Scheduler)
- **Measurement Tool:** `std::chrono::high_resolution_clock` (Microsecond precision)
- **Test Environment:** Vadapalani Junction OSM Graph (Live SUMO Ingestion)

| Scenario | Active Logic | Execution Time | Bottleneck Risk |
|---|---|---|---|
| 1. Normal Traffic | Edmonds-Karp Max-Flow | 0.2209 ms | None |
| 2. Pedestrian Platoon | Max-Flow + VUI Scaling | 0.2419 ms | None |
| 3. Dual-EV Conflict | TTI Scheduler + Velocity Tie-Breaker | 0.4026 ms | None |

...

## Architectural Takeaway
The engine computes maximum vehicle throughput and resolves complex life-safety conflicts in under 0.5 milliseconds. A standard YOLOv8 vision pipeline requires approximately 20-30ms to process a single frame. At ~0.2ms, this deterministic C++ decision engine operates 100x faster than the vision layer, guaranteeing it will never bottleneck the live pipeline. This data validates the design choice to utilize graph theory over Reinforcement Learning, securing strictly explainable, bounds-checked outcomes with near-zero inference latency.