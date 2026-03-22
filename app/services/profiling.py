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
        behavior_label="normal",
        risk_score=0,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def _classify_behavior(profile: UserProfile, recent_failed: int, ip_changed: bool) -> tuple[str, int]:
    """Adaptive classification based on user history and current activity."""
    score = 0

    avg = profile.avg_login_attempts or 0
    brute_threshold = min(5, max(3, int(avg * 1.5)))

    if recent_failed >= brute_threshold + 2:
        score += 60
    elif recent_failed >= brute_threshold:
        score += 35
    elif recent_failed >= 2:
        score += 15

    if ip_changed:
        score += 20

    start = profile.typical_login_start_hour
    end = profile.typical_login_end_hour
    if start is not None and end is not None:
        window_size = (end - start) % 24
        if window_size > 12:
            score = max(0, score - 10)

    if score >= 60:
        return "high-risk", min(score, 100)
    elif score >= 30:
        return "suspicious", score
    return "normal", score


def update_user_profile(db: Session, user_id: str) -> UserProfile:
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id, behavior_label="normal", risk_score=0)
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
    base_logs = success_logs or (
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

    # Adaptive behavior classification
    latest_log = recent_logs[0] if recent_logs else None
    if latest_log and latest_log.timestamp:
        window_start = latest_log.timestamp - timedelta(minutes=10)
    else:
        window_start = now - timedelta(minutes=10)

    recent_failed = (
        db.query(LogEntry)
        .filter(
            LogEntry.user_id == user_id,
            LogEntry.action == "login",
            LogEntry.status == "failed",
            LogEntry.timestamp >= window_start,
        )
        .count()
    )
    ip_changed = bool(latest_log and profile.usual_ip and latest_log.ip != profile.usual_ip)

    profile.behavior_label, profile.risk_score = _classify_behavior(profile, recent_failed, ip_changed)
    profile.last_updated = now
    db.add(profile)
    return profile
