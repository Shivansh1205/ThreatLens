from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class LogCreate(BaseModel):
    user_id: str = Field(..., min_length=1)
    ip: str = Field(..., min_length=1)
    timestamp: datetime
    action: Literal["login", "api_call", "other"]
    status: Literal["success", "failed"]
    port: int = Field(..., ge=1, le=65535)


class LogIngestResponse(BaseModel):
    log_id: int
    risk_score: int
    alerted: bool
    alert_id: Optional[int] = None
