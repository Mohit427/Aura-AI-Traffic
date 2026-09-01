from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from advisor_service import generate_advisor_response


app = FastAPI()


class PhaseDurations(BaseModel):
    north_south_green: int
    east_west_green: int
    pedestrian_crossing_green: int


class EngineOutput(BaseModel):
    timestamp: str
    intersection_id: str
    phase_durations: PhaseDurations
    priority_mode: str
    vui_score: int


class AdvisorRequest(BaseModel):
    engine_output: EngineOutput
    context: Optional[dict] = None


@app.get("/")
def root():
    return {
        "message": "AURA Day 3 AI Advisor is running"
    }


@app.post("/api/advisor/explain")
def explain(request: AdvisorRequest):

    response = generate_advisor_response(
        engine_output=request.engine_output.model_dump(),
        context=request.context
    )

    return {
        "explanation": response,
        "priority_mode": request.engine_output.priority_mode
    }