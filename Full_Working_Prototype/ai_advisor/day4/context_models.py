from pydantic import BaseModel


class ContextRequest(BaseModel):
    location: str
    radius_km: float


class Event(BaseModel):
    title: str
    type: str
    relevance: str


class ContextResponse(BaseModel):
    events: list[Event]