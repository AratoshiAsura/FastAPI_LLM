from fastapi import FastAPI
from pydantic import BaseModel

from llm import ask_llm

app =FastAPI(title="LLM API", version="0.1.0")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str


@app.get("/health")
async def health():
    return {"status": "OK"}

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    answer = await ask_llm(req.message)
    return ChatResponse(answer=answer)
