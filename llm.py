import os
import logging

from pyexpat import model
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
MODEL = os.getenv("MODEL","apodex/apodex-1.1-mini:free")

SYSTEM_PROMPT = (
    "Ты — опытный IT-гик. Отвечай кратко, по делу, без воды. "
    "Если не уверен — скажи прямо."
)

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_KEY,
)

async def ask_llm(user_text: str) -> str:
    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.exception("LLM Error")
        #return f"Error LLM: {e}"
        async def ask_llm(user_text: str) -> str:
            response = await client.chat.completions.create(...)
            return response.choices[0].message.content
