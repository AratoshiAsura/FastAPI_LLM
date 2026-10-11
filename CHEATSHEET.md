# Cheatsheet: FastAPI_LLM

Конспект по функциям и приёмам, использованным в проекте.

## 1. FastAPI

### `FastAPI(title=..., lifespan=...)`
**Что:** создаёт приложение.
**Аргументы:**
- `title` — заголовок в Swagger.
- `lifespan` — async-контекст для startup/shutdown.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="LLM API", version="0.2.0", lifespan=lifespan)
```

### `@app.get("/path")`
**Что:** регистрирует GET-эндпоинт.

```python
@app.get("/health")
async def health():
    return {"status": "ok"}
```

### `@app.post("/path", response_model=...)`
**Что:** регистрирует POST-эндпоинт с валидацией ответа.

```python
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    ...
```

### `Depends(get_db)`
**Что:** внедряет зависимость (сессию БД) в эндпоинт. FastAPI вызовет `get_db` и передаст результат.

```python
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
```

### `HTTPException`
**Что:** возвращает HTTP-ошибку с кодом и сообщением.

```python
from fastapi import HTTPException

raise HTTPException(status_code=502, detail=f"LLM error: {e}")
```

---

## 2. Pydantic

### `BaseModel`
**Что:** базовая схема для валидации входных/выходных данных.

```python
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    chat_id: str = "default"

class ChatResponse(BaseModel):
    answer: str
```

### `ConfigDict(from_attributes=True)`
**Что:** позволяет Pydantic читать данные из ORM-объектов (SQLAlchemy). Без этого `response_model` не сможет сериализовать модель БД.

```python
from pydantic import BaseModel, ConfigDict

class HistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chat_id: str
    user_message: str
    llm_answer: str
    created_at: datetime
```

---

## 3. SQLAlchemy

### `create_async_engine(url)`
**Что:** создаёт асинхронный движок БД.

```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine("sqlite+aiosqlite:///./chat_history.db", echo=False)
```

### `async_sessionmaker(engine)`
**Что:** фабрика сессий. Каждый запрос получает свою сессию.

```python
from sqlalchemy.ext.asyncio import async_sessionmaker

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
```

### `DeclarativeBase`
**Что:** базовый класс для моделей (SQLAlchemy 2.0).

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

### `Mapped[...]` + `mapped_column(...)`
**Что:** описание колонок с типизацией.

```python
from datetime import datetime, UTC
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chat_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    user_message: Mapped[str] = mapped_column(Text, nullable=False)
    llm_answer: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
```

### `select(Model).where(...).order_by(...).limit(...)`
**Что:** асинхронный SELECT-запрос.

```python
from sqlalchemy import select

result = await db.execute(
    select(ChatMessage)
    .where(ChatMessage.chat_id == chat_id)
    .order_by(ChatMessage.id.desc())
    .limit(limit)
)
items = result.scalars().all()
```

### `db.add(...)` + `await db.commit()`
**Что:** добавление записи и сохранение в БД.

```python
msg = ChatMessage(chat_id="user1", user_message="привет", llm_answer="ответ")
db.add(msg)
await db.commit()
```

---

## 4. Работа с БД в приложении

### `get_db()`
**Что:** зависимость FastAPI. Выдаёт сессию и закрывает после запроса.

```python
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
```

### `init_db()`
**Что:** создаёт таблицы при старте приложения.

```python
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

---

## 5. LLM (OpenRouter)

### `AsyncOpenAI(base_url=..., api_key=...)`
**Что:** асинхронный клиент OpenAI-совместимого API.

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_KEY"),
)
```

### `ask_llm(text)`
**Что:** отправляет сообщение в LLM и возвращает ответ.

```python
async def ask_llm(user_text: str) -> str:
    response = await client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
    )
    return response.choices[0].message.content
```

---

## 6. Тесты (pytest + httpx)

### `AsyncClient` + `ASGITransport`
**Что:** HTTP-клиент для тестов без запуска uvicorn.

```python
from httpx import ASGITransport, AsyncClient

transport = ASGITransport(app=app)
async with AsyncClient(transport=transport, base_url="http://test") as ac:
    response = await ac.get("/health")
```

### `app.dependency_overrides[get_db]`
**Что:** подменяет зависимость `get_db` на тестовую БД.

```python
app.dependency_overrides[get_db] = override_get_db
yield
app.dependency_overrides.clear()
```

### `AsyncMock(return_value=...)`
**Что:** мок для async-функции (подменяет `ask_llm` без вызова API).

```python
from unittest.mock import AsyncMock, patch

with patch("main.ask_llm", new=AsyncMock(return_value="мок-ответ")):
    response = await client.post("/chat", json={"message": "тест"})
```

### `side_effect=Exception(...)`
**Что:** заставляет мок поднять исключение (для проверки обработки ошибок).

```python
with patch("main.ask_llm", new=AsyncMock(side_effect=Exception("LLM down"))):
    response = await client.post("/chat", json={"message": "тест"})
assert response.status_code == 502
```

---

## 7. Docker

### `Dockerfile`
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `.dockerignore`
```
.env
.venv/
__pycache__/
.pytest_cache/
*.pyc
.git/
*.db
```

### Команды
```bash
docker build -t fastapi-llm .                          # собрать
docker run -p 8000:8000 --env-file .env fastapi-llm    # запустить
docker ps                                              # запущенные
docker logs <id>                                       # логи
docker stop <id>                                       # остановить
```

---

## 8. Env-переменные

```python
from dotenv import load_dotenv
import os

load_dotenv()
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
MODEL = os.getenv("MODEL", "default-model")
```

`.env`:
```
OPENROUTER_KEY=sk-or-v1-...
MODEL=nex-agi/nex-n2.5-mini:free
```

**Правило:** `.env` в `.gitignore`, `.env.example` — в репозитории (без ключей).
