"""AliagaAI LLM service (Groq)."""
from __future__ import annotations

import asyncio
import json

from groq import AsyncGroq
from loguru import logger

from app.core.config import settings


if settings.GROQ_API_KEY:
    groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
else:
    logger.warning("GROQ_API_KEY bulunamadi. LLM cagrilari calismayacak.")
    groq_client = None


async def generate_chat_response(
    messages: list[dict],
    model: str | None = None,
    response_format: dict | None = None,
    temperature: float = 0.0,
    max_tokens: int = 1024,
) -> str | None:
    """Call Groq chat completion with retry."""
    if not groq_client:
        logger.error("Groq client baslatilamadi. API anahtari eksik.")
        return None

    retries = 3
    delay = 1.5

    for attempt in range(retries):
        try:
            kwargs = {
                "messages": messages,
                "model": model or settings.GROQ_MODEL,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if response_format:
                kwargs["response_format"] = response_format

            completion = await groq_client.chat.completions.create(**kwargs)
            return completion.choices[0].message.content
        except Exception as exc:  # pragma: no cover - network path
            logger.warning(f"LLM Groq API hatasi (deneme {attempt + 1}/{retries}): {exc}")
            if attempt < retries - 1:
                await asyncio.sleep(delay)
                delay *= 2
            else:
                logger.error("LLM Groq API tamamen basarisiz oldu.")
                return None


async def get_json_response(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.0,
) -> dict:
    """Call model and parse JSON object response."""
    response_text = await generate_chat_response(
        messages=messages,
        model=model,
        response_format={"type": "json_object"},
        temperature=temperature,
    )
    if not response_text:
        return {}

    try:
        return json.loads(response_text)
    except json.JSONDecodeError as exc:
        logger.error(f"LLM cikti JSON formatinda degil: {exc}\nCikti: {response_text}")
        return {}
