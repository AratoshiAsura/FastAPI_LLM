from fastapi import Depends, FastAPI, HTTPException
from llm import ask_llm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db, init_db, Base
from models import ChatMessage
from schemas import ChatRequest, ChatResponse, HistoryItem

app =FastAPI(title="LLM API", version="0.2.0")

@app.on_event("startup")
async def startup():
    await init_db()

#class ChatRequest(BaseModel):
    #message: str

#class ChatResponse(BaseModel):
    #answer: str


@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    try:
        answer = await ask_llm(req.message)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {e}")

    msg = ChatMessage(
        chat_id=req.chat_id,
        user_message=req.message,
        llm_answer=answer,
    )
    db.add(msg)
    await db.commit()

    return ChatResponse(answer=answer)

@app.get("/history/{chat_id}", response_model=list[HistoryItem])
async def history_by_chat(chat_id: str, limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.id.desc())
        .limit(limit)
    )
    return result.scalars().all()
@app.get("/history", response_model=list[HistoryItem])
async def history(limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChatMessage).order_by(ChatMessage.id.desc()).limit(limit)
    )
    return result.scalars().all()
