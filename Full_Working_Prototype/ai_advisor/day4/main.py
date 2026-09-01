from fastapi import FastAPI
from context_models import ContextRequest, ContextResponse, Event
from tavily_service import search_events_near_intersection

app = FastAPI()


@app.get("/")
def root():
    return {
        "message": "AURA Day 4 Context Service is running"
    }


@app.post("/api/search/context", response_model=ContextResponse)
def search_context(request: ContextRequest):

    tavily_results = search_events_near_intersection(request.location)

    events = []

    for result in tavily_results.get("results", []):
        score = result.get("score", 0)

        if score >= 0.75:
            relevance = "high"
        elif score >= 0.5:
            relevance = "medium"
        else:
            relevance = "low"

        events.append(
            Event(
                title=result.get("title", "Unknown event"),
                type="event",
                relevance=relevance
            )
        )

    return ContextResponse(events=events)