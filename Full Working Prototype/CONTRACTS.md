# AURA — Data Contracts

Shared JSON schemas between layers. Do not change field names without notifying the whole team.

**Roles (as of Day 1 revision):**
- Mohit — Backend, Orchestration, Automation & Integration
- Shruti — Vision & Live Data (YOLOv8 + TomTom)
- Tharanesh — Digital Twin (Eclipse SUMO + TraCI)
- Yashvant ATK — Optimization Engine (C++ Edmonds-Karp + EV Scheduler)
- Mithunn — Frontend & AI Advisor (React + Swytchcode + Tavily)

**Database:** PostgreSQL (via SQLAlchemy/asyncpg) — each JSON payload below maps to a table: `vision_logs`, `tomtom_logs`, `sumo_state_logs`, `engine_decisions`, `ev_events`.

---

## 1. Vision Output (Shruti → Backend)

```json
{
  "timestamp": "2026-08-26T10:15:30Z",
  "intersection_id": "vadapalani_junction",
  "zone": "north_approach",
  "counts": {
    "car": 12,
    "bus": 2,
    "truck": 1,
    "motorcycle": 8,
    "bicycle": 3,
    "person": 15
  },
  "platoon_detected": false,
  "tracked_objects": [
    {
      "object_id": "veh_042",
      "class": "car",
      "distance_to_stopline_m": 45.2,
      "speed_kmh": 22.5
    }
  ],
  "ev_detected": []
}
```
- `tracked_objects` holds per-object distance/speed for anything worth tracking individually (not just aggregate counts) — this is where Shruti's Day 3 pixel-distance speed estimation lands:
  `speed = (Δy_pixels × scale_factor) / Δt`
- Populate `tracked_objects` at minimum for any detected emergency vehicle (feeds directly into the EV Conflict Event below); populate it more broadly if useful once speed estimation is stable.

## 2. TomTom Output (Shruti → Backend)

```json
{
  "timestamp": "2026-08-26T10:15:30Z",
  "segment_id": "arcot_road_north",
  "current_speed_kmh": 18,
  "free_flow_speed_kmh": 45,
  "congestion_ratio": 0.6
}
```

## 3. Digital Twin State (Tharanesh → Backend / Engine)

```json
{
  "timestamp": "2026-08-26T10:15:30Z",
  "intersection_id": "vadapalani_junction",
  "sim_time_s": 145.2,
  "edges": [
    {
      "edge_id": "north_approach",
      "queue_length": 14,
      "occupancy_ratio": 0.62,
      "avg_wait_time_s": 22.5
    },
    {
      "edge_id": "crosswalk_north",
      "queue_length": 9,
      "occupancy_ratio": 0.4,
      "avg_wait_time_s": 30.0
    }
  ],
  "demand_profile": "medium"
}
```
- `demand_profile` is one of: `light | medium | heavy` — used for both live calibration and the synthetic historical seed data Tharanesh generates on Day 4.
- This is the graph-state snapshot Yashvant's engine consumes as its live input, calibrated from Shruti's real detection + TomTom data via TraCI.

## 4. Engine Output (Yashvant ATK → Backend)

```json
{
  "timestamp": "2026-08-26T10:15:30Z",
  "intersection_id": "vadapalani_junction",
  "phase_durations": {
    "north_south_green": 32,
    "east_west_green": 28,
    "pedestrian_crossing_green": 15
  },
  "priority_mode": "normal",
  "vui_score": 42
}
```
`priority_mode` is one of: `normal | vulnerable_user | emergency_vehicle`

## 5. EV Conflict Event (Shruti / Yashvant ATK → Backend)

```json
{
  "timestamp": "2026-08-26T10:15:30Z",
  "ev_id": "ev_1",
  "distance_to_stopline_m": 120,
  "velocity_kmh": 40,
  "tti_seconds": 10.8,
  "priority_rank": "EV-1"
}
```
- `distance_to_stopline_m` and `velocity_kmh` come straight from Shruti's `tracked_objects` entry for that vehicle; Yashvant's engine computes `tti_seconds` and `priority_rank` from there.

## 6. Advisor Agent Endpoints (Mithunn ↔ Backend)

**`POST /api/advisor/explain`**

Request:
```json
{
  "engine_output": { "...": "matches Engine Output contract above" },
  "context": { "...": "optional, matches /api/search/context response below" }
}
```
Response:
```json
{
  "explanation": "Extending North-South green by 12 seconds — a cyclist platoon of 14 is waiting.",
  "priority_mode": "vulnerable_user"
}
```

**`POST /api/search/context`**

Request:
```json
{
  "location": "Vadapalani Junction, Chennai",
  "radius_km": 2
}
```
Response:
```json
{
  "events": [
    {
      "title": "Road closure near Vadapalani for maintenance",
      "type": "road_closure",
      "relevance": "high"
    }
  ]
}
```

---

## Demo Intersection
- Name: Vadapalani Junction, Chennai
- Coordinates: 13.0505, 80.2121
