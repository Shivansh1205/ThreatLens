from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.log_entry import LogEntry
from app.models.user_profile import UserProfile

FAILED_WINDOW_MINUTES = 10
BRUTE_FORCE_THRESHOLD = 5
ALERT_THRESHOLD = 40

SENSITIVE_PORTS_HIGH = {22, 23, 3389}
SENSITIVE_PORTS_MED = {445, 3306, 5432}


def _count_recent_failed_logins(db: Session, user_id: str, now: datetime) -> int:
    window_start = now - timedelta(minutes=FAILED_WINDOW_MINUTES)
    return (
        db.query(LogEntry)
        .filter(
            LogEntry.user_id == user_id,
            LogEntry.action == "login",
            LogEntry.status == "failed",
            LogEntry.timestamp >= window_start,
        )
        .count()
    )


def _is_unusual_time(profile: UserProfile, log_time: datetime) -> bool:
    if profile.typical_login_start_hour is None or profile.typical_login_end_hour is None:
        return False
    start = profile.typical_login_start_hour
    end = profile.typical_login_end_hour
    hour = log_time.hour
    if start <= end:
        return not (start <= hour <= end)
    # Handles ranges that wrap past midnight, e.g., 22 -> 3.
    return not (hour >= start or hour <= end)


def analyze_log(db: Session, log: LogEntry, profile: UserProfile) -> tuple[int, list[str]]:
    reasons: list[str] = []
    risk_score = 0

    # Always use server time so the window query is consistent
    now = datetime.utcnow()

    # Brute-force: log is already committed, so count includes current log
    failed_count = 0
    if log.action == "login":
        failed_count = _count_recent_failed_logins(db, log.user_id, now)

    if failed_count >= BRUTE_FORCE_THRESHOLD:
        risk_score += 50
        reasons.append(f"brute force: {failed_count} failed logins in {FAILED_WINDOW_MINUTES}m")
    elif failed_count >= 3:
        risk_score += 30
        reasons.append(f"multiple failed logins: {failed_count} in {FAILED_WINDOW_MINUTES}m")
    elif log.action == "login" and log.status == "failed":
        risk_score += 10
        reasons.append("failed login attempt")

    # Behavior deviation: new IP compared to the user's usual IP.
    if profile.usual_ip and log.ip != profile.usual_ip:
        risk_score += 20
        reasons.append("unusual IP for user")

    # Behavior deviation: login outside the user's typical time window.
    if log.action == "login" and _is_unusual_time(profile, log.timestamp):
        risk_score += 15
        reasons.append("unusual login time")

    # Port-based risk
    if log.port in SENSITIVE_PORTS_HIGH:
        risk_score += 30
        reasons.append(f"sensitive port {log.port}")
    elif log.port in SENSITIVE_PORTS_MED:
        risk_score += 15
        reasons.append(f"risky port {log.port}")

    risk_score = min(risk_score, 100)
    return risk_score, reasons
