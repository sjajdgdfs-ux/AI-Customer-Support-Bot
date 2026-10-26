from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    reply: str
    intent: str
    thread_id: str
