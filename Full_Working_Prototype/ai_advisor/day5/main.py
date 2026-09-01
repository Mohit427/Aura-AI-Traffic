from fastapi import FastAPI
from models import AdvisorRequest
from advisor_service import explain_decision

app = FastAPI()


@app.get("/")
def root():
    return {
        "message": "AURA Day 5 Advisor is running"
    }


@app.post("/api/advisor/explain")
def explain(request: AdvisorRequest):

    return explain_decision(
        engine_output=request.engine_output.model_dump(),
        context=request.context
    )