import json

from llm import client
import pytest
from unittest.mock import AsyncMock, patch
from httpx import ASGITransport, AsyncClient
from main import app

#часть старого кода для памяти)
#@pytest.mark.asyncio
#async def test_health():
#    transport = ASGITransport(app=app)
#    async with AsyncClient(transport=transport, base_url="http://test") as ac:
#        response = await ac.get("/health")
#    assert response.status_code == 200
#    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_chat_returns_answer(client):
    with patch("main.ask_llm", new=AsyncMock(return_value="mock-answer")):
        #transport = ASGITransport(app=app)
        #async with AsyncClient(transport=transport, base_url="http://test") as ac:
            #response = await ac.post("/chat", json={"message": "hello"})
        response = await client.post("/chat", json={"message": "hello"})
    assert response.status_code == 200
    assert response.json() == {"answer": "mock-answer"}


@pytest.mark.asyncio
async def test_chat_validation_error(client):
    #transport = ASGITransport(app=app)
    #async with AsyncClient(transport=transport, base_url="http://test") as ac:
        #response = await ac.post("/chat", json={})
    response = await client.post("/chat", json={})

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_chat_saves_to_history(client):
    with patch("main.ask_llm", new=AsyncMock(return_value="mock-answer")):
        await client.post("/chat", json={"message": "test", "chat_id": "user1"})

    response = await client.get("/history/user1")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["user_message"] == "test"
    assert items[0]["llm_answer"] == "mock-answer"

@pytest.mark.asyncio
async def test_history_empty(client):
    response = await client.get("/history/nonexistent")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_history_filters_by_chat(client):
    with patch("main.ask_llm", new=AsyncMock(return_value="answe")):
        await client.post("/chat", json={"message": "msg1", "chat_id": "user1"})
        await client.post("/chat", json={"message": "msg2", "chat_id": "user2"})

    r1 = await client.get("/history/user1")
    r2 = await client.get("/history/user2")

    assert len(r1.json()) == 1
    assert len(r2.json()) == 1
    assert r1.json()[0]["chat_id"] == "user1"
    assert r2.json()[0]["chat_id"] == "user2"

@pytest.mark.asyncio
async def test_chat_llm_error_return_502(client):
    with patch("main.ask_llm", new=AsyncMock(side_effect=Exception("LLM down"))):
        response = await client.post("/chat", json={"message": "test"})
    assert response.status_code == 502

    history = await client.get("/history")
    assert history.json() == []
