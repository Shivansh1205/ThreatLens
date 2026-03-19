from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from .session import Base


class UserProfile(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    usual_ip = Column(String, nullable=True)
    avg_login_attempts = Column(Float, default=0.0)
    typical_login_start = Column(String, nullable=True)
    typical_login_end = Column(String, nullable=True)

    # Lightweight stats to keep the baseline dynamic
    first_seen_date = Column(String, nullable=True)  # YYYY-MM-DD
    last_seen_date = Column(String, nullable=True)
    total_login_attempts = Column(Integer, default=0)
    total_logs = Column(Integer, default=0)

    # Heuristic fields for adapting usual IP over time
    usual_ip_hits = Column(Integer, default=0)
    candidate_ip = Column(String, nullable=True)
    candidate_ip_hits = Column(Integer, default=0)

    last_updated = Column(DateTime, default=datetime.utcnow)


class LogEntry(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    ip = Column(String, index=True)
    timestamp = Column(DateTime, index=True)
    action = Column(String)
    status = Column(String)
    port = Column(Integer)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    ip = Column(String, index=True)
    risk_score = Column(Integer)
    reason = Column(String)
    timestamp = Column(DateTime, index=True, default=datetime.utcnow)