from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ChatRequest(BaseModel):
    message: str
    chat_id: str = "default"
class ChatResponse(BaseModel):
    answer: str
class HistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    chat_id: str
    user_message: str
    llm_answer: str
    created_at: datetime

#    class Config:
#        from_attributes = True
