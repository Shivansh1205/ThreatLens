import asyncio
import json
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.alert import Alert
from app.models.user_profile import UserProfile

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    profiles = db.query(UserProfile).all()
    total_users = len(profiles)

    high_risk = [p for p in profiles if getattr(p, "behavior_label", "normal") == "high-risk"]
    suspicious = [p for p in profiles if getattr(p, "behavior_label", "normal") == "suspicious"]
    active_threats = len(high_risk) + len(suspicious)

    recent_cutoff = datetime.utcnow() - timedelta(hours=24)
    recent_alerts = (
        db.query(Alert)
        .filter(Alert.timestamp >= recent_cutoff)
        .order_by(Alert.timestamp.desc())
        .limit(10)
        .all()
    )

    return {
        "total_users": total_users,
        "active_threats": active_threats,
        "high_risk_users": [
            {
                "user_id": p.user_id,
                "behavior_label": getattr(p, "behavior_label", "normal"),
                "risk_score": getattr(p, "risk_score", 0),
                "usual_ip": p.usual_ip,
            }
            for p in sorted(high_risk + suspicious, key=lambda x: getattr(x, "risk_score", 0), reverse=True)[:5]
        ],
        "recent_alerts": [
            {
                "id": a.id,
                "user_id": a.user_id,
                "ip": a.ip,
                "risk_score": a.risk_score,
                "reasons": [r.strip() for r in (a.reason or "").split(";") if r.strip()],
                "timestamp": a.timestamp.isoformat() if a.timestamp else None,
            }
            for a in recent_alerts
        ],
    }
