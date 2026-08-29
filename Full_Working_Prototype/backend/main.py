from fastapi import FastAPI
from datetime import datetime, timezone

app = FastAPI(title="AURA Backend")

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}