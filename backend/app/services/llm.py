"""
AliağaAI — LLM Servisi (Groq).

FastAPI asenkron yapısıyla uyumlu olması için AsyncGroq kullanır.
"""
import json
from loguru import logger
from groq import AsyncGroq
from app.core.config import settings

# Groq client'ını oluştur
if settings.GROQ_API_KEY:
    groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
else:
    logger.warning("GROQ_API_KEY bulunamadı! LLM çağrıları çalışmayacak.")
    groq_client = None


import asyncio

async def generate_chat_response(messages: list[dict], model: str = None, response_format: dict = None) -> str | None:
    """
    Groq API üzerinden modele istek atar ve yanıtı döner.
    Hatalara karşı 3 defa otomatik tekrar deneme (retry) yapar.
    """
    if not groq_client:
        logger.error("Groq client başlatılamadı. API anahtarı eksik.")
        return None

    retries = 3
    delay = 1.5

    for attempt in range(retries):
        try:
            kwargs = {
                "messages": messages,
                "model": model or settings.GROQ_MODEL,
                "temperature": 0.0,  # Halüsinasyonu engellemek ve kesin sonuç almak için
                "max_tokens": 1024,
            }
            
            # Eğer özel bir format (ör. JSON) isteniyorsa
            if response_format:
                kwargs["response_format"] = response_format

            completion = await groq_client.chat.completions.create(**kwargs)
            return completion.choices[0].message.content
            
        except Exception as e:
            logger.warning(f"LLM Groq API Hatası (Deneme {attempt+1}/{retries}): {e}")
            if attempt < retries - 1:
                await asyncio.sleep(delay)
            else:
                logger.error("LLM Groq API tamamen başarısız oldu!")
                return None


async def get_json_response(messages: list[dict], model: str = None) -> dict:
    """Yanıtı her zaman JSON formatında beklediğimiz çağrılar (Ör: Intent tespiti)."""
    response_text = await generate_chat_response(
        messages=messages, 
        model=model,
        response_format={"type": "json_object"}
    )
    
    if not response_text:
        return {}
        
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.error(f"LLM çıktısı JSON formatında değil: {e}\nÇıktı: {response_text}")
        return {}
