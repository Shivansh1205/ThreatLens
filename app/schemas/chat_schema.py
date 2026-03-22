from typing import Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    context: Optional[str] = None  # selected option category


class ChatResponse(BaseModel):
    answer: str
    options: Optional[list[str]] = None
    session_id: Optional[str] = None
