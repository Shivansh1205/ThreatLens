from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user_profile import UserProfile

router = APIRouter(prefix="/users", tags=["users"])

@router.get("")
def list_users(db: Session = Depends(get_db)):
    profiles = db.query(UserProfile).order_by(UserProfile.risk_score.desc()).all()
    return [
        {
            "user_id": p.user_id,
            "behavior_label": getattr(p, "behavior_label", "normal"),
            "risk_score": getattr(p, "risk_score", 0),
            "usual_ip": p.usual_ip,
        }
        for p in profiles
    ]
