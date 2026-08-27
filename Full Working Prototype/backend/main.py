from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from contextlib import asynccontextmanager

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
