from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.log_entry import LogEntry
from app.models.user_profile import UserProfile

FAILED_WINDOW_MINUTES = 10
BRUTE_FORCE_THRESHOLD = 5
ALERT_THRESHOLD = 50

# Increased weights for sensitive ports
SENSITIVE_PORTS_HIGH = {22, 23, 3389}  # SSH, Telnet, RDP
SENSITIVE_PORTS_MED = {445, 3306, 5432} # SMB, MySQL, Postgres

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

def _count_recent_distinct_ports(db: Session, ip: str, current_port: int, now: datetime) -> int:
    window_start = now - timedelta(minutes=5)
    records = (
        db.query(LogEntry.port)
        .filter(
            LogEntry.ip == ip,
            LogEntry.timestamp >= window_start,
        )
        .all()
    )
    ports = {r[0] for r in records}
    ports.add(current_port)
    return len(ports)

def _is_unusual_time(profile: UserProfile, log_time: datetime) -> bool:
    if profile.typical_login_start_hour is None or profile.typical_login_end_hour is None:
        return False
    start = profile.typical_login_start_hour
    end = profile.typical_login_end_hour
    hour = log_time.hour
    if start <= end:
        return not (start <= hour <= end)
    return not (hour >= start or hour <= end)

def analyze_log(db: Session, log: LogEntry, profile: UserProfile) -> tuple[int, list[str]]:
    reasons: list[str] = []
    risk_score = 0
    now = datetime.utcnow()

    # --- 1. BRUTE FORCE LOGIC (Exponential Scaling) ---
    failed_count = 0
    if log.action == "login":
        failed_count = _count_recent_failed_logins(db, log.user_id, now)
        if log.status == "failed":
            failed_count += 1

    if failed_count >= 10:  # CRITICAL level brute force
        risk_score += 80
        reasons.append(f"CRITICAL: Massive brute force detected ({failed_count} failures)")
    elif failed_count >= BRUTE_FORCE_THRESHOLD:
        risk_score += 50 # Increased from 40
        reasons.append(f"High risk: {failed_count} failed logins in {FAILED_WINDOW_MINUTES}m")
    elif failed_count >= 3:
        risk_score += 30
        reasons.append(f"Multiple failed logins: {failed_count}")
    elif log.action == "login" and log.status == "failed":
        risk_score += 15
        reasons.append("Failed login attempt")

    # --- 2. BEHAVIOR DEVIATION ---
    is_unusual_ip = False
    if profile.usual_ip and log.ip != profile.usual_ip:
        risk_score += 25  # Increased from 20
        reasons.append("Unusual IP for user")
        is_unusual_ip = True

    if log.action == "login" and _is_unusual_time(profile, log.timestamp):
        risk_score += 15
        reasons.append("Unusual login time")

    # --- 3. PORT SCANNING ---
    scan_count = _count_recent_distinct_ports(db, log.ip, log.port, now)
    if scan_count >= 5:
        risk_score += 45 # Increased from 35
        reasons.append(f"Port scan pattern: {scan_count} distinct ports")

    # --- 4. SENSITIVE PORTS ---
    is_sensitive = False
    if log.port in SENSITIVE_PORTS_HIGH:
        risk_score += 30 # Increased from 20
        reasons.append(f"Sensitive port {log.port} (High Risk)")
        is_sensitive = True
    elif log.port in SENSITIVE_PORTS_MED:
        risk_score += 15
        reasons.append(f"Risky port {log.port}")

    # --- 5. THE "CRITICAL" MULTIPLIER (Compound Risk) ---
    # If it's a new IP AND they are failing logins AND hitting sensitive ports
    if is_unusual_ip and log.status == "failed" and is_sensitive:
        risk_score += 20 # Bonus points for the "Perfect Storm" of bad behavior
        reasons.append("COMPOUND THREAT: Multiple high-risk indicators matching attack patterns")

    # Ensure max is 100
    risk_score = min(risk_score, 100)
    
    return int(risk_score), reasons