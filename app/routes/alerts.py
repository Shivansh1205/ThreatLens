from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertOut

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertOut])
def list_alerts(db: Session = Depends(get_db)):
    return db.query(Alert).order_by(Alert.timestamp.desc()).all()


@router.get("/recent", response_model=list[AlertOut])
def recent_alerts(
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
):
    since = datetime.utcnow() - timedelta(hours=hours)
    return (
        db.query(Alert)
        .filter(Alert.timestamp >= since)
        .order_by(Alert.timestamp.desc())
        .all()
    )
