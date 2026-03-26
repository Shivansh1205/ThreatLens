from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.database.session import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    risk_score = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)
    explanation = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
