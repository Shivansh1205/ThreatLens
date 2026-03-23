from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.init_db import init_db
from app.routes.alerts import router as alerts_router
from app.routes.logs import router as logs_router
from app.routes.chat import router as chat_router
from app.routes.dashboard import router as dashboard_router

app = FastAPI(
    title="ThreatLens",
    description="Adaptive Behavior-Based Intrusion Detection and Threat Analysis System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok"}


app.include_router(logs_router)
app.include_router(alerts_router)
app.include_router(chat_router)
app.include_router(dashboard_router)
