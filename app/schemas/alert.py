from datetime import datetime

from pydantic import BaseModel


class AlertOut(BaseModel):
    id: int
    ip: str
    user_id: str
    risk_score: int
    reason: str
    timestamp: datetime

    class Config:
        orm_mode = True
        from_attributes = True
