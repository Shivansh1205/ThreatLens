from __future__ import annotations

from datetime import date, datetime

from sqlalchemy.orm import Session

from app.database.models import UserProfile
from app.models.log import LogIn


def get_or_create_user_profile(db: Session, user_id: str) -> UserProfile:
    user = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not user:
        user = UserProfile(user_id=user_id)
        db.add(user)
        db.flush()
    return user


def update_user_profile(db: Session, user: UserProfile, log: LogIn) -> None:
    """Update baseline behavior stats based on the incoming log."""

    user.total_logs = (user.total_logs or 0) + 1

    log_date = log.timestamp.date().isoformat()
    if not user.first_seen_date:
        user.first_seen_date = log_date
    if not user.last_seen_date or log_date > user.last_seen_date:
        user.last_seen_date = log_date

    if log.action == "login":
        user.total_login_attempts = (user.total_login_attempts or 0) + 1

    if user.first_seen_date and user.last_seen_date:
        days_observed = (
            date.fromisoformat(user.last_seen_date)
            - date.fromisoformat(user.first_seen_date)
        ).days + 1
        user.avg_login_attempts = round(
            user.total_login_attempts / max(days_observed, 1), 2
        )

    # Update usual IP heuristics on successful logins
    if log.action == "login" and log.status == "success":
        _update_usual_ip(user, log.ip)

    # Update the typical login time range on successful logins
    if log.action == "login" and log.status == "success":
        time_str = log.timestamp.strftime("%H:%M")
        if not user.typical_login_start or not user.typical_login_end:
            user.typical_login_start = time_str
            user.typical_login_end = time_str
        else:
            user.typical_login_start = min(user.typical_login_start, time_str)
            user.typical_login_end = max(user.typical_login_end, time_str)

    user.last_updated = datetime.utcnow()


def _update_usual_ip(user: UserProfile, ip: str) -> None:
    """Heuristic: promote a new IP to usual if it repeats often enough."""

    if not user.usual_ip:
        user.usual_ip = ip
        user.usual_ip_hits = 1
        user.candidate_ip = None
        user.candidate_ip_hits = 0
        return

    if ip == user.usual_ip:
        user.usual_ip_hits = (user.usual_ip_hits or 0) + 1
        user.candidate_ip = None
        user.candidate_ip_hits = 0
        return

    if user.candidate_ip == ip:
        user.candidate_ip_hits = (user.candidate_ip_hits or 0) + 1
    else:
        user.candidate_ip = ip
        user.candidate_ip_hits = 1

    # After 3 successful logins from the new IP, treat it as usual
    if (user.candidate_ip_hits or 0) >= 3:
        user.usual_ip = user.candidate_ip
        user.usual_ip_hits = user.candidate_ip_hits
        user.candidate_ip = None
        user.candidate_ip_hits = 0