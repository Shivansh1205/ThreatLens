from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.alert import Alert
from app.models.log_entry import LogEntry
from app.schemas.log import LogCreate, LogIngestResponse
from app.services.detection import ALERT_THRESHOLD, analyze_log
from app.services.profiling import get_or_create_profile, update_user_profile
from app.services.ws_manager import manager

router = APIRouter(prefix="/log", tags=["logs"])


@router.post("", response_model=LogIngestResponse)
def ingest_log(payload: LogCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    profile = get_or_create_profile(db, payload.user_id, payload.ip)

    # Save log FIRST so the failed-login count query in analyze_log finds it
    log_entry = LogEntry(
        user_id=payload.user_id,
        ip=payload.ip,
        timestamp=datetime.utcnow(),  # always use server time
        action=payload.action,
        status=payload.status,
        port=payload.port,
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)

    risk_score, reasons = analyze_log(db, log_entry, profile)

    alert = None
    if risk_score >= ALERT_THRESHOLD:
        alert = Alert(
            ip=payload.ip,
            user_id=payload.user_id,
            risk_score=risk_score,
            reason="; ".join(reasons) if reasons else "risk threshold exceeded",
            timestamp=datetime.utcnow(),
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)

    update_user_profile(db, payload.user_id)
    db.commit()

    if alert:
        alert_payload = {
            "id": alert.id,
            "user_id": alert.user_id,
            "ip": alert.ip,
            "risk_score": alert.risk_score,
            "reasons": [r.strip() for r in (alert.reason or "").split(";") if r.strip()],
            "timestamp": alert.timestamp.isoformat(),
        }
        background_tasks.add_task(manager.broadcast, alert_payload)

    return LogIngestResponse(
        log_id=log_entry.id,
        risk_score=risk_score,
        alerted=alert is not None,
        alert_id=alert.id if alert else None,
    )
