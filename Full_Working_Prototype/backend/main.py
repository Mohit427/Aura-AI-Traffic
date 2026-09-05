from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone, timedelta
from contextlib import asynccontextmanager
import subprocess
import json
import requests
import os
import asyncio
from dotenv import load_dotenv
from database import engine, Base, get_db
from models import VisionLog, TomTomLog, SumoStateLog, EngineDecision, EvEvent
from tavily import TavilyClient
import google.generativeai as genai


load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-flash-latest")
tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

ENGINE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "engine", "engine_linux")

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="AURA Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

    prompt = f"""You are AURA, an AI traffic control advisor for Vadapalani Junction, Chennai.
Explain this signal decision in one plain-language sentence for a city planner.
Engine output: {json.dumps(engine_output)}
Context: {json.dumps(context)}"""

    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(gemini_model.generate_content, prompt),
            timeout=15.0
        )
        explanation = response.text.strip()
    except (Exception, asyncio.TimeoutError) as e:
        print(f"GEMINI ERROR: {e}")
        if priority_mode == "vulnerable_user":
            explanation = f"Prioritizing pedestrian/cyclist crossing — VUI score is {engine_output.get('vui_score', 'N/A')}."
        elif priority_mode == "emergency_vehicle":
            explanation = "Emergency vehicle detected — signal sequence overridden for safe passage."
        else:
            explanation = "Standard vehicle-flow optimization in effect."

    return {"explanation": explanation, "priority_mode": priority_mode}


@app.post("/api/search/context")
async def search_context(payload: dict):
    location = payload.get("location", "Vadapalani Junction, Chennai")

    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(
                tavily_client.search,
                query=f"traffic incidents road closures events near {location} today",
                max_results=3
            ),
            timeout=10.0
        )
        events = [
            {"title": r.get("title", "Untitled"), "type": "web_result", "relevance": "high"}
            for r in result.get("results", [])
        ]
        if not events:
            events = [{"title": f"No live incidents found near {location}", "type": "none", "relevance": "low"}]
    except (Exception, asyncio.TimeoutError) as e:
        print(f"TAVILY ERROR: {e}")
        events = [{"title": f"No live incidents found near {location}", "type": "none", "relevance": "low"}]

    return {"events": events}


# ── Orchestration: calls the C++ engine ─────────────────────

@app.post("/api/orchestrate")
async def orchestrate(payload: dict, db: AsyncSession = Depends(get_db)):
    north = payload.get("north", 0)
    south = payload.get("south", 0)
    east = payload.get("east", 0)
    west = payload.get("west", 0)
    pedestrian = payload.get("pedestrian", 0)

    result = subprocess.run(
        [ENGINE_PATH, str(north), str(south), str(east), str(west), str(pedestrian)],
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


# Maps Tharanesh's raw SUMO edge IDs to the friendly names decision-cycle
# aggregates on. If your own sumo_state_bridge.py (which already posts
# friendly names) is used instead, these keys simply won't match anything
# in EDGE_ID_MAP and the raw value passes through unchanged via .get() fallback.
EDGE_ID_MAP = {
    "1313198082.274": "north_approach",
    "1313198080.250": "south_approach",
    "1110246916": "east_approach",
    "588357066": "west_approach",
}


@app.post("/api/decision-cycle")
async def decision_cycle(db: AsyncSession = Depends(get_db)):
    sumo_result = await db.execute(
        select(SumoStateLog).order_by(SumoStateLog.timestamp.desc()).limit(10)
    )
    recent_sumo = sumo_result.scalars().all()

    cutoff = datetime.now(timezone.utc) - timedelta(minutes=10)
    vision_result = await db.execute(
        select(VisionLog).where(VisionLog.timestamp >= cutoff).order_by(VisionLog.timestamp.desc())
    )
    recent_vision = vision_result.scalars().all()

    if not recent_sumo or not recent_vision:
        return {"error": "Need at least one vision reading and one SUMO reading before running a decision cycle"}

    pedestrian = max((v.counts.get("person", 0) for v in recent_vision), default=0)
    latest_vision = recent_vision[0]

    edge_counts = {"north_approach": 0, "south_approach": 0, "east_approach": 0, "west_approach": 0}
    for state in recent_sumo:
        for e in state.edges:
            edge_id = e["edge_id"]
            friendly_name = EDGE_ID_MAP.get(edge_id, edge_id)
            if friendly_name in edge_counts:
                edge_counts[friendly_name] = max(edge_counts[friendly_name], e["queue_length"])

    north = edge_counts["north_approach"]
    south = edge_counts["south_approach"]
    east = edge_counts["east_approach"]
    west = edge_counts["west_approach"]

    latest_sumo = recent_sumo[0]

    result = subprocess.run(
        [ENGINE_PATH, str(north), str(south), str(east), str(west), str(pedestrian)],
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

    return {
        "inputs_used": {"north": north, "south": south, "east": east, "west": west, "pedestrian": pedestrian},
        "sumo_reading_timestamp": latest_sumo.timestamp.isoformat(),
        "sumo_readings_considered": len(recent_sumo),
        "vision_reading_timestamp": latest_vision.timestamp.isoformat(),
        "engine_output": engine_output
    }


@app.get("/api/latest-decision")
async def latest_decision(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(EngineDecision).order_by(EngineDecision.timestamp.desc()).limit(1)
    )
    latest = result.scalar_one_or_none()

    if not latest:
        return {"error": "No engine decisions recorded yet"}

    return {
        "timestamp": latest.timestamp.isoformat(),
        "intersection_id": latest.intersection_id,
        "phase_durations": latest.phase_durations,
        "priority_mode": latest.priority_mode,
        "vui_score": latest.vui_score,
        "ev_schedule": latest.ev_schedule
    }


N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/downstream-green-wave")

@app.post("/api/simulate-ev")
async def simulate_ev(payload: dict, db: AsyncSession = Depends(get_db)):
    north = payload.get("north", 12)
    south = payload.get("south", 10)
    east = payload.get("east", 8)
    west = payload.get("west", 14)
    vui_score = payload.get("vui_score", 0)
    ev_north_tti = payload.get("ev_north_tti", 0)
    ev_east_tti = payload.get("ev_east_tti", 0)
    ev_north_velocity = payload.get("ev_north_velocity", 0.0)
    ev_east_velocity = payload.get("ev_east_velocity", 0.0)

    result = subprocess.run(
        [ENGINE_PATH, str(north), str(south), str(east), str(west),
         str(vui_score), str(ev_north_tti), str(ev_east_tti),
         str(ev_north_velocity), str(ev_east_velocity)],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        return {"error": "engine failed", "stderr": result.stderr}

    engine_output = json.loads(result.stdout)

    log = EngineDecision(
        timestamp=datetime.now(timezone.utc),
        intersection_id="vadapalani_junction",
        phase_durations=engine_output.get("phase_durations", {}),
        priority_mode=engine_output["priority_mode"],
        vui_score=engine_output["vui_score"],
        ev_schedule=engine_output.get("ev_schedule"),
    )
    db.add(log)
    await db.commit()

    webhook_result = None
    if engine_output.get("priority_mode") == "emergency_vehicle":
        try:
            resp = requests.post(N8N_WEBHOOK_URL, json=engine_output.get("ev_schedule", {}), timeout=3)
            webhook_result = {"status_code": resp.status_code, "response": resp.json()}
        except requests.exceptions.RequestException as e:
            webhook_result = {"error": str(e)}

    return {
        "engine_output": engine_output,
        "webhook_triggered": engine_output.get("priority_mode") == "emergency_vehicle",
        "webhook_result": webhook_result
    }
