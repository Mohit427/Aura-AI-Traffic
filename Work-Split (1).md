# AURA — 10-Day Sprint Plan (Person-by-Person, Day-by-Day)

**Team:** Mohit, Shruti, Yashvant ATK, Tharanesh, Mithunn

| Person | Owns |
|---|---|
| **Mohit** | Backend, Orchestration, Automation & Integration Lead |
| **Shruti** | Vision & Live Data Lead (YOLOv8 + TomTom) |
| **Tharanesh** | Digital Twin Lead (Eclipse SUMO + TraCI) |
| **Yashvant ATK** | Optimization Engine Lead (C++ Edmonds-Karp + EV Scheduler) |
| **Mithunn** | Frontend & AI Advisor Lead (React + Swytchcode + Tavily) |

**Golden rule:** every day below ends in something you can literally point at and say "this works" — a screenshot, a running process, a JSON output, a rendered UI. Nothing is "I read about X today." If a day's deliverable can't be shown, that's the flag to raise at standup, not something to quietly carry forward.

---

## 📌 Day 1 (Today) — Show This at Tomorrow's Meeting

| Person | Task | Tomorrow's Deliverable |
|---|---|---|
| **Mohit** | Lock the demo intersection; set up shared GitHub repo & branch structure; write the JSON data-contract doc (vehicle counts, pedestrian/cyclist counts, TomTom output, engine output, EV event payload); FastAPI skeleton | Repo live, contract doc shared with team, a running `/health` FastAPI endpoint |
| **Shruti** | Source demo footage (must have visible pedestrians/cyclists); run baseline pretrained YOLOv8 on it | A video clip with bounding boxes drawn live on cars, pedestrians, and cyclists |
| **Tharanesh** | Export OSM data for the chosen intersection; build the first SUMO network file; render it in SUMO-GUI | Screenshot/recording of the actual intersection rendered as a SUMO network |
| **Yashvant ATK** | Set up C++ project skeleton; implement basic Edmonds-Karp on a toy graph; verify correctness with Codemate.ai | Console output proving max-flow computes correctly on a test graph |
| **Mithunn** | Set up React (Vite) project; build the dashboard shell (dark mode, placeholder panels for live view / VUI gauge / signal timeline) | A running localhost dashboard shell in the browser |

**Meeting goal:** everyone shows their piece exists and runs. This isn't the finished feature — it's proof the foundation is real, one day in.

---

## Phase 1: Days 2–3 — Standalone Components, Real Data

### Mohit
- **Day 2:** Build PostgreSQL schema (historical logs, VUI history, EV event log) using SQLAlchemy/asyncpg; wire FastAPI endpoints to accept mock data from each layer. → *Deliverable: FastAPI accepts POST from mock vision/engine data, stores in PostgreSQL.*
- **Day 3:** Orchestration logic — FastAPI calls the C++ engine (subprocess/pybind11) with mock counts, returns signal timing. → *Deliverable: end-to-end mock call (POST counts → engine → JSON timing back).*

### Shruti
- **Day 2:** Build structured JSON output pipeline (counts per class, per lane/crosswalk region) matching Mohit's contract; get TomTom API key and confirm a working call. → *Deliverable: continuous JSON detection stream + a real TomTom API response.*
- **Day 3:** Refine detection zones (lane vs. crosswalk regions), tune confidence thresholds, implement relative pixel-distance shortcut ($\text{Speed} = \frac{\Delta y_{\text{pixels}} \times \text{Scale Factor}}{\Delta t}$) for distance/speed estimation. → *Deliverable: clean, contract-matching JSON stream with speed estimation running continuously on the demo video.*

### Tharanesh
- **Day 2:** Define lane/edge structure matching the intersection's real approach roads; set up basic demand generation for a standalone run. → *Deliverable: SUMO simulation running standalone with basic traffic flow.*
- **Day 3:** Build the TraCI interface skeleton to allow external data injection; verify scripts run with headless `sumo` binary. → *Deliverable: a headless TraCI script that pushes a mock vehicle count into SUMO.*

### Yashvant ATK
- **Day 2:** Model the actual intersection as a graph (nodes/edges matching Tharanesh's SUMO network); basic signal-timing output from the max-flow result. → *Deliverable: engine takes manual lane counts, outputs green-phase durations for the real intersection.*
- **Day 3:** Expose the engine as a callable service (pybind11 binding or subprocess/socket) for FastAPI; optimize bindings with Codemate.ai. → *Deliverable: Mohit can call the engine from Python and get JSON timing back.*

### Mithunn
- **Day 2:** Build the static VUI gauge and signal-phase timeline components with dummy data. → *Deliverable: gauge and timeline rendering with mock values.*
- **Day 3:** Set up Swytchcode CLI; scaffold backend AI Advisor agent service/endpoints (`/api/advisor/explain` and `/api/search/context`); configure TomTom + Tavily API keys. → *Deliverable: Swytchcode "hello world" agent responding via backend route.*

---

## Phase 2: Days 4–6 — Human-Priority & Emergency-Vehicle Logic + Pairwise Integration

### Mohit
- **Day 4:** Integrate Shruti's real vision output into the backend ingestion endpoint. → *Deliverable: real detected counts landing live in PostgreSQL.*
- **Day 5:** Integrate Tharanesh's SUMO/TraCI output into the backend; add the EV-priority event schema. → *Deliverable: SUMO-calibrated data flowing into the backend.*
- **Day 6:** Full pairwise integration test — Vision → SUMO → Engine → Backend running with real data end to end (no dashboard yet). → *Deliverable: a logged full pipeline decision cycle, visible in console/logs.*

### Shruti
- **Day 4:** Implement pedestrian/cyclist clustering logic for platoon detection (10+ threshold); begin dual-EV visual detection. → *Deliverable: platoon flag correctly triggers on a test clip with a crowd.*
- **Day 5:** Implement EV distance/velocity tracking using the pixel-to-meter scale factor for TTI — hand off numbers to Yashvant ATK. → *Deliverable: live distance/velocity overlay on ambulance test footage.*
- **Day 6:** Push the live detection feed continuously into the backend; validate against Mohit's endpoint. → *Deliverable: real-time counts visibly landing in PostgreSQL.*

### Tharanesh
- **Day 4:** Generate synthetic historical demand profiles (light/medium/heavy) for PostgreSQL seeding; begin human-priority edge markup (crosswalk edges). → *Deliverable: 3 synthetic demand datasets ready for PostgreSQL.*
- **Day 5:** Add EV-specific route/lane markup; build a synthetic dual-EV conflict scenario in SUMO. → *Deliverable: SUMO scenario showing two ambulances approaching from conflicting directions.*
- **Day 6:** Wire TraCI to accept real YOLOv8 + TomTom data to calibrate the live simulation in headless mode. → *Deliverable: SUMO reflecting real detected counts in near-real-time.*

### Yashvant ATK
- **Day 4:** Implement dynamic edge-reweighting for human-priority (VUI) — crosswalk edge gets boosted capacity/priority when a platoon is detected. → *Deliverable: engine correctly reprioritizes the crosswalk edge on a mock platoon signal.*
- **Day 5:** Implement the TTI-based dual-EV priority scheduler (EV-1/EV-2 designation, infinite-capacity/zero-weight edge override, time-staged scheduling). → *Deliverable: engine correctly sequences two mock ambulance events with different TTIs.*
- **Day 6:** Implement edge-case tie-breakers (equal TTI, standstill ambulance); integrate with Tharanesh's live SUMO data. → *Deliverable: engine consuming live SUMO data, producing correct decisions across all three scenario types (normal, platoon, dual-EV).*

### Mithunn
- **Day 4:** Build the backend Tavily integration service — query real-world events/incidents near the demo intersection. → *Deliverable: Tavily returning real results for the chosen location via backend endpoint.*
- **Day 5:** Build the Swytchcode advisor's core logic: engine decision + Tavily context → plain-language explanation endpoint. → *Deliverable: agent produces a sample explanation from mock engine output.*
- **Day 6:** Wire the dashboard to backend endpoints for live data display (replacing dummy data). → *Deliverable: dashboard showing live vehicle/pedestrian/cyclist counts.*

---

## Phase 3: Days 7–8 — Automation, Context, Advisor Agent

### Mohit
- **Day 7:** Set up n8n workflows — scheduled TomTom polling, PostgreSQL logging, threshold alerting. → *Deliverable: n8n workflow actively polling TomTom and logging.*
- **Day 8:** Add the n8n downstream green-wave webhook for EV scheduling; connect FastAPI to trigger it. → *Deliverable: webhook fires correctly on a simulated EV event.*

### Shruti
- **Day 7:** Support Tavily integration with location/time metadata tagging; polish detection accuracy for edge cases (night footage, occlusion). → *Deliverable: documented accuracy report + edge-case fixes.*
- **Day 8:** Support full integration testing; benchmark detection latency/FPS to confirm it isn't a pipeline bottleneck. → *Deliverable: measured latency/FPS benchmark.*

### Tharanesh
- **Day 7:** Validate calibration accuracy against real detected counts; tune SUMO parameters (driver behavior, lane capacity) for realism. → *Deliverable: calibration accuracy report.*
- **Day 8:** Support Yashvant's engine integration — confirm SUMO outputs the exact graph structure/edge data the engine expects. → *Deliverable: verified SUMO → Engine handoff.*

### Yashvant ATK
- **Day 7:** Benchmark and optimize decision latency for near-instant response using Codemate.ai. → *Deliverable: measured latency benchmark.*
- **Day 8:** Support backend integration testing with Mohit; fix bugs surfaced by real-data edge cases. → *Deliverable: stable engine responses under real pipeline load.*

### Mithunn
- **Day 7:** Wire the VUI gauge and signal timeline to live engine output; wire advisor agent backend endpoints to live engine decisions. → *Deliverable: VUI gauge reacting live to real platoon detection.*
- **Day 8:** Build the EV-conflict UI (TTI display, conflict visualization, downstream green-wave indicator). → *Deliverable: dashboard visually shows the dual-EV conflict resolving in real time.*

---

## Phase 4: Days 9–10 — Full Integration, Deployment, Demo Prep

### Mohit
- **Day 9:** Deploy the full stack to Render (Web Service + Managed PostgreSQL + Background Worker); verify from a public URL. → *Deliverable: publicly accessible deployed app.*
- **Day 10:** End-to-end stress test with the whole team; fix orchestration bugs; support rehearsal. → *Deliverable: stable, rehearsed live pipeline.*

### Shruti
- **Day 9:** Final tuning for the three demo scenarios (normal, platoon, dual-EV). → *Deliverable: three reliable, demo-ready video clips.*
- **Day 10:** Standby during full rehearsal for live troubleshooting. → *Deliverable: vision layer confirmed demo-ready.*

### Tharanesh
- **Day 9:** Support full pipeline integration on Render; confirm synthetic historical data is logged to PostgreSQL in production. → *Deliverable: historical logs populated in the deployed DB.*
- **Day 10:** Support stress-testing with heavy-traffic and platoon/EV scenarios; final polish. → *Deliverable: all 3 demo scenarios validated in SUMO.*

### Yashvant ATK
- **Day 9:** Support full end-to-end integration and Render deployment; validate engine behavior in the deployed environment. → *Deliverable: engine confirmed working in production.*
- **Day 10:** Stress-test with all demo scenarios; support rehearsal. → *Deliverable: engine confirmed demo-ready.*

### Mithunn
- **Day 9:** Deploy frontend on Render; final UI polish (transitions, alert states, color coding). → *Deliverable: publicly accessible, fully wired dashboard.*
- **Day 10:** Support full rehearsal; fix UI bugs found during stress testing. → *Deliverable: dashboard confirmed demo-ready.*

---

## Daily Standup Checklist (use every day, not just Day 1)

Each person answers three questions in under a minute:
1. What did I finish yesterday (show it, don't describe it)?
2. What am I finishing today?
3. What's blocking me — whose output am I waiting on?

Question 3 matters most from Day 4 onward, since that's when the layers start depending on each other directly.