from datetime import datetime
from typing import List

from pydantic import BaseModel, model_validator


class AlertOut(BaseModel):
    id: int
    ip: str
    user_id: str
    risk_score: int
    reason: str
    reasons: List[str] = []
    explanation: str = ""
    timestamp: datetime

    @model_validator(mode="after")
    def populate_reasons(self):
        if not self.reasons and self.reason:
            self.reasons = [r.strip() for r in self.reason.split(";") if r.strip()]
        return self

    class Config:
        orm_mode = True
        from_attributes = True
