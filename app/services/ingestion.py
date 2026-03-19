from sqlalchemy.orm import Session

from app.database.models import LogEntry
from app.models.log import LogIn, LogResponse
from app.services.alert_service import create_alert
from app.services.detection import ALERT_THRESHOLD, compute_risk
from app.services.profiler import get_or_create_user_profile, update_user_profile


def process_log(db: Session, log: LogIn) -> LogResponse:
    user = get_or_create_user_profile(db, log.user_id)

    # Compute risk using the current baseline before updating it
    risk_score, reasons = compute_risk(db, log, user)

    # Store the raw log entry
    log_entry = LogEntry(
        user_id=log.user_id,
        ip=log.ip,
        timestamp=log.timestamp,
        action=log.action,
        status=log.status,
        port=log.port,
    )
    db.add(log_entry)

    # Update baseline behavior after storing the log
    update_user_profile(db, user, log)

    alert_created = False
    if risk_score >= ALERT_THRESHOLD:
        create_alert(db, log, risk_score, reasons)
        alert_created = True

    db.commit()

    return LogResponse(
        risk_score=risk_score,
        alert_created=alert_created,
        reasons=reasons,
    )