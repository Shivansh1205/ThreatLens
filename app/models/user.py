from typing import Optional

from pydantic import BaseModel


class UserProfileOut(BaseModel):
    user_id: str
    usual_ip: Optional[str]
    avg_login_attempts: float
    typical_login_start: Optional[str]
    typical_login_end: Optional[str]