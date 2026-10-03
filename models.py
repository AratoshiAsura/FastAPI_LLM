from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from database import Base

class ChatMessage(Base):
    __tablename__ = "chat_message"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, index=True, nullable=False)
    user_message = Column(Text, nullable=False)
    llm_answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
