from datetime import datetime, UTC
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from database import Base

class ChatMessage(Base):
    __tablename__ = "chat_message"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, index=True, nullable=False)
    user_message = Column(Text, nullable=False)
    llm_answer = Column(Text, nullable=False)
#    created_at = Column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
