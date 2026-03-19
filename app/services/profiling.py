from collections import Counter
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.models.log_entry import LogEntry
from app.models.user_profile import UserProfile

MAX_LOGS = 200
AVG_WINDOW_DAYS = 7
TIME_WINDOW_DAYS = 30


def get_or_create_profile(
    db: Session,
    user_id: str,
    default_ip: Optional[str] = None,
) -> UserProfile:
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if profile:
        return profile
    profile = UserProfile(
        user_id=user_id,
        usual_ip=default_ip,
        avg_login_attempts=0.0,
        typical_login_start_hour=None,
        typical_login_end_hour=None,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_user_profile(db: Session, user_id: str) -> UserProfile:
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)
        db.flush()

    now = datetime.utcnow()

    recent_logs = (
        db.query(LogEntry)
        .filter(LogEntry.user_id == user_id)
        .order_by(LogEntry.timestamp.desc())
        .limit(MAX_LOGS)
        .all()
    )
    if recent_logs:
        ip_counts = Counter(log.ip for log in recent_logs if log.ip)
        if ip_counts:
            profile.usual_ip = ip_counts.most_common(1)[0][0]

    avg_window_start = now - timedelta(days=AVG_WINDOW_DAYS)
    login_logs = (
        db.query(LogEntry)
        .filter(
            LogEntry.user_id == user_id,
            LogEntry.action == "login",
            LogEntry.timestamp >= avg_window_start,
        )
        .all()
    )
    if login_logs:
        days = {log.timestamp.date() for log in login_logs if log.timestamp}
        profile.avg_login_attempts = len(login_logs) / max(len(days), 1)
    else:
        profile.avg_login_attempts = 0.0

    time_window_start = now - timedelta(days=TIME_WINDOW_DAYS)
    success_logs = (
        db.query(LogEntry)
        .filter(
            LogEntry.user_id == user_id,
            LogEntry.action == "login",
            LogEntry.status == "success",
            LogEntry.timestamp >= time_window_start,
        )
        .all()
    )
    base_logs = success_logs
    if not base_logs:
        base_logs = (
            db.query(LogEntry)
            .filter(
                LogEntry.user_id == user_id,
                LogEntry.action == "login",
                LogEntry.timestamp >= time_window_start,
            )
            .all()
        )

    if base_logs:
        hours = [log.timestamp.hour for log in base_logs if log.timestamp]
        profile.typical_login_start_hour = min(hours)
        profile.typical_login_end_hour = max(hours)
    else:
        profile.typical_login_start_hour = None
        profile.typical_login_end_hour = None

    profile.last_updated = now
    db.add(profile)
    return profile
