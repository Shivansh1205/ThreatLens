from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.database.session import Base


class LogEntry(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    ip = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), index=True, nullable=False)
    action = Column(String, index=True, nullable=False)
    status = Column(String, index=True, nullable=False)
    port = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
