
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = "default"


class ChatResponse(BaseModel):
    reply: str
    intent: str
    thread_id: str
