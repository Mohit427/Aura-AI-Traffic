from pydantic import BaseModel
from typing import Optional, Literal


class PhaseDurations(BaseModel):
    north_south_green: int
    east_west_green: int
    pedestrian_crossing_green: int


class EngineOutput(BaseModel):
    timestamp: str
    intersection_id: str
    phase_durations: PhaseDurations
    priority_mode: Literal[
        "normal",
        "vulnerable_user",
        "emergency_vehicle"
    ]
    vui_score: int


class AdvisorRequest(BaseModel):
    engine_output: EngineOutput
    context: Optional[dict] = None