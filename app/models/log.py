from datetime import datetime
from typing import Literal, List

from pydantic import BaseModel, Field


class LogIn(BaseModel):
    user_id: str = Field(..., examples=["user_123"])
    ip: str = Field(..., examples=["192.168.1.10"])
    timestamp: datetime
    action: Literal["login", "api_call", "other"]
    status: Literal["success", "failed"]
    port: int = Field(..., ge=1, le=65535)


class LogResponse(BaseModel):
    risk_score: int
    alert_created: bool
    reasons: List[str]