from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from app.database.models import Alert
from app.models.log import LogIn


def create_alert(
    db: Session, log: LogIn, risk_score: int, reasons: List[str]
) -> Alert:
    alert = Alert(
        user_id=log.user_id,
        ip=log.ip,
        risk_score=risk_score,
        reason="; ".join(reasons),
        timestamp=log.timestamp or datetime.utcnow(),
    )
    db.add(alert)
    return alert