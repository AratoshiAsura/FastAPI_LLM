from datetime import datetime
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    chat_id: str = "default"
class ChatResponse(BaseModel):
    answer: str
class HistoryItem(BaseModel):
    id: int
    chat_id: str
    user_message: str
    llm_answer: str
    created_at: datetime

    class Config:
        from_attributes = True
