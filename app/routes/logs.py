from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.alert import Alert
from app.models.log_entry import LogEntry
from app.schemas.log import LogCreate, LogIngestResponse
from app.services.detection import ALERT_THRESHOLD, analyze_log
from app.services.profiling import get_or_create_profile, update_user_profile

router = APIRouter(prefix="/log", tags=["logs"])


@router.post("", response_model=LogIngestResponse)
def ingest_log(payload: LogCreate, db: Session = Depends(get_db)):
    profile = get_or_create_profile(db, payload.user_id, payload.ip)

    log_entry = LogEntry(
        user_id=payload.user_id,
        ip=payload.ip,
        timestamp=payload.timestamp,
        action=payload.action,
        status=payload.status,
        port=payload.port,
    )

    risk_score, reasons = analyze_log(db, log_entry, profile)

    alert = None
    if risk_score >= ALERT_THRESHOLD:
        reasons_str = "; ".join(reasons) if reasons else "risk threshold exceeded"
        alert = Alert(
            ip=payload.ip,
            user_id=payload.user_id,
            risk_score=risk_score,
            reason=reasons_str,
            explanation=f"Alert generated for {payload.user_id} on {payload.ip} due to risk score {risk_score}.",
            timestamp=datetime.utcnow(),
        )
        db.add(alert)

    db.add(log_entry)
    db.commit()

    db.refresh(log_entry)
    if alert:
        db.refresh(alert)

    update_user_profile(db, payload.user_id)
    db.commit()

    return LogIngestResponse(
        log_id=log_entry.id,
        risk_score=risk_score,
        alert_generated=alert is not None,
        alert_id=alert.id if alert else None,
        reasons=reasons,
    )
