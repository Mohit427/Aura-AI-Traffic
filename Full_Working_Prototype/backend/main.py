from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from contextlib import asynccontextmanager
import subprocess
import json

from database import engine, Base, get_db
from models import VisionLog, TomTomLog, SumoStateLog, EngineDecision, EvEvent


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="AURA Backend", lifespan=lifespan)


@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


# ── Data ingestion endpoints ────────────────────────────────

@app.post("/api/vision")
async def post_vision(payload: dict, db: AsyncSession = Depends(get_db)):
    log = VisionLog(
        timestamp=datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00")),
        intersection_id=payload["intersection_id"],
        zone=payload["zone"],
        counts=payload["counts"],
        platoon_detected=payload["platoon_detected"],
        tracked_objects=payload.get("tracked_objects", []),
    )
    db.add(log)
    await db.commit()
    return {"status": "stored"}


@app.post("/api/tomtom")
async def post_tomtom(payload: dict, db: AsyncSession = Depends(get_db)):
    log = TomTomLog(
        timestamp=datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00")),
        segment_id=payload["segment_id"],
        current_speed_kmh=payload["current_speed_kmh"],
        free_flow_speed_kmh=payload["free_flow_speed_kmh"],
        congestion_ratio=payload["congestion_ratio"],
    )
    db.add(log)
    await db.commit()
    return {"status": "stored"}


@app.post("/api/sumo-state")
async def post_sumo_state(payload: dict, db: AsyncSession = Depends(get_db)):
    log = SumoStateLog(
        timestamp=datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00")),
        intersection_id=payload["intersection_id"],
        sim_time_s=payload["sim_time_s"],
        edges=payload["edges"],
        demand_profile=payload["demand_profile"],
    )
    db.add(log)
    await db.commit()
    return {"status": "stored"}


@app.post("/api/engine-decision")
async def post_engine_decision(payload: dict, db: AsyncSession = Depends(get_db)):
    log = EngineDecision(
        timestamp=datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00")),
        intersection_id=payload["intersection_id"],
        phase_durations=payload["phase_durations"],
        priority_mode=payload["priority_mode"],
        vui_score=payload["vui_score"],
    )
    db.add(log)
    await db.commit()
    return {"status": "stored"}


@app.post("/api/ev-event")
async def post_ev_event(payload: dict, db: AsyncSession = Depends(get_db)):
    log = EvEvent(
        timestamp=datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00")),
        ev_id=payload["ev_id"],
        approach_edge=payload["approach_edge"],
        distance_to_stopline_m=payload["distance_to_stopline_m"],
        velocity_kmh=payload["velocity_kmh"],
        tti_seconds=payload["tti_seconds"],
        priority_rank=payload["priority_rank"],
    )
    db.add(log)
    await db.commit()
    return {"status": "stored"}


# ── AI Advisor endpoints ────────────────────────────────────

@app.post("/api/advisor/explain")
async def advisor_explain(payload: dict):
    engine_output = payload.get("engine_output", {})
    context = payload.get("context", {})
    priority_mode = engine_output.get("priority_mode", "normal")

    # Placeholder logic — replace with real Swytchcode agent call once wired
    if priority_mode == "vulnerable_user":
        explanation = f"Prioritizing pedestrian/cyclist crossing — VUI score is {engine_output.get('vui_score', 'N/A')}."
    elif priority_mode == "emergency_vehicle":
        explanation = "Emergency vehicle detected — signal sequence overridden for safe passage."
    else:
        explanation = "Standard vehicle-flow optimization in effect."

    return {"explanation": explanation, "priority_mode": priority_mode}


@app.post("/api/search/context")
async def search_context(payload: dict):
    location = payload.get("location", "Unknown location")
    # Placeholder — replace with real Tavily API call
    return {"events": [
        {"title": f"No live incidents found near {location}", "type": "none", "relevance": "low"}
    ]}


# ── Orchestration: calls the C++ engine ─────────────────────

@app.post("/api/orchestrate")
async def orchestrate(payload: dict, db: AsyncSession = Depends(get_db)):
    north = payload.get("north", 0)
    south = payload.get("south", 0)
    east = payload.get("east", 0)
    west = payload.get("west", 0)
    pedestrian = payload.get("pedestrian", 0)

    result = subprocess.run(
        ["../engine/engine_linux", str(north), str(south), str(east), str(west), str(pedestrian)],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        return {"error": "engine failed", "stderr": result.stderr}

    engine_output = json.loads(result.stdout)

    log = EngineDecision(
        timestamp=datetime.now(timezone.utc),
        intersection_id="vadapalani_junction",
        phase_durations=engine_output["phase_durations"],
        priority_mode=engine_output["priority_mode"],
        vui_score=engine_output["vui_score"],
    )
    db.add(log)
    await db.commit()

    return engine_output
