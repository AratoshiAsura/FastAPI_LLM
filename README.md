# FastAPI LLM Service

HTTP-сервис на FastAPI с интеграцией LLM через OpenRouter.

## Стек
- Python 3.14
- FastAPI
- uvicorn
- OpenAI SDK (OpenAI-совместимый API OpenRouter)
- pydantic
- pytest + httpx

## Эндпоинты
- `GET /health` — проверка работоспособности
- `POST /chat` — принимает `{"message": "..."}`, возвращает `{"answer": "..."}`

## Запуск
1. Клонировать репозиторий.
2. Создать `.env` по образцу `.env.example`.
3. `python -m venv .venv && source .venv/bin/activate`
4. `pip install -r requirements.txt`
5. `uvicorn main:app --reload`
6. Открыть `http://127.0.0.1:8000/docs`

## Пример запроса
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Что такое FastAPI?"}'
```

## Тесты
```bash
pytest -v
```
## Docker

### Сборка
```bash
docker build -t fastapi-llm .
```

### Запуск
```bash
docker run -p 8000:8000 --env-file .env fastapi-llm
```

### Проверка
```bash
curl http://localhost:8000/health
```
## Хранение истории

Сервис сохраняет диалоги в SQLite через SQLAlchemy (async).

- `GET /history` — последние N сообщений из всех чатов
- `GET /history/{chat_id}` — история конкретного чата

## Обработка ошибок

При ошибке LLM клиент получает `502 Bad Gateway`, запись в БД не создаётся.
