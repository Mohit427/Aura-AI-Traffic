# AURA — AI Traffic Digital Twin for Smart Traffic Optimization

**A human-centric, predictive, self-optimizing traffic signal system for Vadapalani Junction, Chennai.**

🔗 **Live Demo:** [aura-ai-traffic.onrender.com](https://aura-ai-traffic.onrender.com)
🔗 **Backend API:** [aura-backend-v27b.onrender.com](https://aura-backend-v27b.onrender.com)

Built in 10 days for Decode SIH 2026.

---

## The Problem

India recorded **1.83 lakh road accident deaths in 2025** — 21 every hour. Pedestrians now account for **1 in 7 of those deaths**, nearly triple their 2015 share. Meanwhile, India's biggest cities lose an estimated **₹1.47 lakh crore annually** to traffic congestion alone, with 10 Indian cities ranking among the world's 100 most congested.

Every adaptive traffic system deployed today optimizes for one thing: moving vehicles faster. None of them ask whether a pedestrian is standing at the crosswalk while the light stays green for cars.

**AURA is a traffic control system that treats human safety as a higher-priority signal than vehicle throughput — not as an afterthought, but as a first-class variable inside the same optimization engine that manages traffic flow.**

---

## What It Does

1. **Sees** the intersection via real-time computer vision (YOLOv8) and predicts incoming congestion via live traffic data (TomTom API) before it's visible on camera.
2. **Simulates** the intersection as a live digital twin (Eclipse SUMO), calibrated continuously with real detection and traffic data via TraCI.
3. **Decides** optimal signal timing using a C++ Edmonds-Karp max-flow engine — the same algorithm that computes normal traffic flow also dynamically reweights the graph to prioritize pedestrian/cyclist crossings (**Vulnerable User Index**) and to resolve dual-emergency-vehicle conflicts via Time-to-Intersection scheduling.
4. **Explains** every decision in plain language via a Gemini-powered AI advisor, with live contextual awareness (road closures, nearby events) via Tavily search.
5. **Acts** — automation via n8n handles scheduled data polling and downstream green-wave coordination for emergency vehicles.

---

## Core Differentiator: Multi-Modal Platoon Prioritization

When YOLOv8 detects a cluster of pedestrians/cyclists at a crossing, the engine doesn't apply a hard-coded override — it dynamically reweights the crosswalk edge's capacity and priority *within the same max-flow computation* used for ordinary vehicle optimization. This is visualized live on the dashboard as the **Vulnerable User Index (VUI)** — a real-time gauge, not a cosmetic metric.

For the hardest safety case — two emergency vehicles approaching from conflicting axes — the engine computes Time-to-Intersection for both, sequences them with a proper all-red clearance phase, and hands the secondary vehicle an immediate green corridor the moment it's safe. Same algorithm, same engine, temporarily overridden edges — not a separate hard-coded subsystem.

---

## Architecture

```
TomTom API ──┐
             ├──► SUMO Digital Twin ──► C++ Max-Flow Engine ──► FastAPI Backend ──► React Dashboard
YOLOv8 ──────┘      (calibrated live)      (Edmonds-Karp)        (orchestrator)      (live control room)
                                                                        │
                                                                  PostgreSQL
                                                              (5 tables: vision,
                                                            tomtom, sumo, decisions,
                                                                 ev events)
                                                                        │
                                                    n8n automation + Gemini advisor + Tavily context
```

Each layer is independently built and posts to a shared PostgreSQL database. The backend aggregates the most recent readings across a rolling time window, feeds them to the C++ engine, and serves the decision to the dashboard — no direct coupling between Vision, SUMO, or the Engine.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Vision | Python, OpenCV, YOLOv8 |
| Upstream traffic prediction | TomTom Traffic API |
| Real-world context | Tavily Search API |
| Digital Twin | Eclipse SUMO, TraCI |
| Optimization Engine | C++ (Edmonds-Karp max-flow) |
| Backend | FastAPI, SQLAlchemy (async), PostgreSQL |
| AI Advisor | Google Gemini (`gemini-flash-latest`) |
| Automation | n8n |
| Frontend | React (Vite) |
| Deployment | Render (Web Service + Static Site + PostgreSQL) |

---

## API Endpoints

**Ingestion**
- `POST /api/vision` — vehicle/pedestrian/cyclist detection counts
- `POST /api/tomtom` — live upstream traffic flow
- `POST /api/sumo-state` — digital twin edge state
- `POST /api/engine-decision`, `POST /api/ev-event` — direct logging

**Orchestration**
- `POST /api/orchestrate` — manual counts → engine decision
- `POST /api/decision-cycle` — fully automatic: aggregates live vision + SUMO data, computes decision, no manual input
- `POST /api/simulate-ev` — dual-emergency-vehicle conflict scenario

**Serving**
- `GET /api/latest-decision` — most recent engine decision (polled by dashboard every 2s)

**Intelligence**
- `POST /api/advisor/explain` — Gemini-generated plain-language explanation of a decision, with deterministic fallback
- `POST /api/search/context` — live Tavily search for real-world context near the intersection

Full data contracts are documented in `CONTRACTS.md`.

---

## Team

| Member | Role |
|---|---|
| **Mohit** | Backend, Orchestration, Automation & Integration Lead |
| **Shruti** | Vision & Live Data (YOLOv8 + TomTom) |
| **Tharanesh** | Digital Twin (Eclipse SUMO + TraCI) |
| **Yashvant ATK** | Optimization Engine (C++ Edmonds-Karp + EV Scheduler) |
| **Mithunn** | Frontend & AI Advisor (React + Gemini + Tavily) |

---

## Running Locally

### Backend
```bash
cd Full_Working_Prototype/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Create a `.env` file:
```
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/aura_db
GEMINI_API_KEY=your_key
TAVILY_API_KEY=your_key
```
Compile the engine and run:
```bash
cd ../engine && g++ -o engine_linux main.cpp && cd ../backend
uvicorn main:app --reload
```

### Frontend
```bash
cd Full_Working_Prototype/frontend
npm install
npm run dev
```

### Digital Twin
```bash
cd Full_Working_Prototype/sumo_simulation
python3 -m venv venv && source venv/bin/activate
pip install traci requests psycopg2-binary
python traci_inject.py
```

### Vision Pipeline
```bash
cd Full_Working_Prototype/vision
python3 -m venv venv && source venv/bin/activate
pip install ultralytics opencv-python requests
python continuous_pipeline.py
```

---

## Known Limitations

- The n8n downstream green-wave webhook currently runs locally and is not cloud-hosted — Render's production backend cannot reach a laptop's localhost. The automation logic is fully implemented and tested; cloud-to-cloud n8n hosting was out of scope for this sprint.
- Emergency vehicle distance/speed values are not echoed back by the engine (only TTI and computed flush duration are) — the dashboard shows these fields honestly as unavailable rather than fabricating them.
- Gemini's free-tier API quota (20 requests/day) is easily exhausted during active testing; the advisor endpoint gracefully falls back to deterministic explanations when unavailable.

---

## Demo Intersection

**Vadapalani Junction, Chennai** — 13.0505°N, 80.2121°E
