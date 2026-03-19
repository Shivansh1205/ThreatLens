from fastapi import FastAPI

from app.database.init_db import init_db
from app.routes.alerts import router as alerts_router
from app.routes.logs import router as logs_router

app = FastAPI(
    title="ThreatLens",
    description="Adaptive Behavior-Based Intrusion Detection and Threat Analysis System",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok"}


app.include_router(logs_router)
app.include_router(alerts_router)
