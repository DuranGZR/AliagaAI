from __future__ import annotations

import re
from typing import Literal

from loguru import logger

from app.services.llm import get_json_response

INTENT_SYSTEM_PROMPT = """Sen Aliağa şehir asistanısın. Kullanıcı sorusunu intent olarak sınıflandır.

Intent seçenekleri:
- pharmacy (eczane, nöbetçi eczane)
- weather (hava durumu, sıcaklık)
- prayer (namaz vakitleri, ezan)
- fuel (benzin, motorin, akaryakıt fiyatları)
- currency (dolar, euro, döviz)
- gold (altın fiyatları)
- earthquake (deprem)
- emergency (acil telefon, itfaiye, ambulans)
- market (semt pazarı, pazar günleri)
- place (gezilecek yer, mekan, kafe, restoran, turistik yer, müze, park)
- news (haber, son gelişmeler)
- event (etkinlik, konser, festival)
- announcement (duyuru, ilan)
- project (belediye projesi, yatırım)
- job (iş ilanı, kariyer)
- outage (su kesintisi, elektrik kesintisi)
- city_info (ulaşım, izban, tarih, mahalleler, nüfus, sanayi, coğrafya, nasıl gelinir, genel şehir bilgisi, ne yapılır, neresi, kurumlar)
- general (yukarıdakilere uymayan genel Aliağa soruları)
- greeting (merhaba, selam, nasılsın)

Kurallar:
- Selamlaşma -> greeting
- Gezilecek yer, mekan, kafe, restoran -> place
- Ulaşım, İZBAN, otoban, nasıl gelinir, feribot -> city_info
- Tarih, mahalle, nüfus, sanayi, coğrafya, genel bilgi -> city_info
- "ne yapılır", "neresi", "hakkında bilgi" -> city_info
- Haber/duyuru/etkinlik/proje/iş ilanı -> ilgili intent
- Aliağa hakkında genel soru -> city_info (general yerine city_info tercih et)
- Emin değilsen city_info kullan

Sadece JSON döndür:
{"intent": "<intent>"}
"""

SQL_ONLY_INTENTS = {
    "pharmacy",
    "weather",
    "prayer",
    "fuel",
    "currency",
    "gold",
    "earthquake",
    "emergency",
    "market",
}

HYBRID_INTENTS = {
    "place",
    "news",
    "event",
    "announcement",
    "project",
    "job",
    "outage",
}

STRICT_GROUNDED_INTENTS = SQL_ONLY_INTENTS.union({
    "news",
    "event",
    "announcement",
    "project",
    "outage",
})

VALID_INTENTS = SQL_ONLY_INTENTS.union(HYBRID_INTENTS).union({
    "city_info",
    "general",
    "greeting",
})


class IntentAnalyzerService:
    @staticmethod
    async def determine_intent(user_message: str) -> str:
        """Kullanıcının sorusunun niyetini belirler."""
        if not user_message or not user_message.strip():
            return "general"

        msg_lower = user_message.lower()
        if "eczane" in msg_lower:
            return "pharmacy"
        elif "hava" in msg_lower and "durum" in msg_lower:
            return "weather"
        elif "namaz" in msg_lower or "ezan" in msg_lower:
            return "prayer"
        elif "altın" in msg_lower or "gram" in msg_lower or "çeyrek" in msg_lower:
            return "gold"

        messages = [
            {"role": "system", "content": INTENT_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]
        
        try:
            payload = await get_json_response(messages, temperature=0.0)
            intent = payload.get("intent", "general").strip().lower()
            if intent not in VALID_INTENTS:
                logger.warning(f"Geçersiz intent döndü: {intent}, fallback -> general")
                return "general"
            return intent
        except Exception as e:
            logger.error(f"Intent analizi hatası: {e}")
            return "general"

    @staticmethod
    def detect_query_type(intent: str, user_message: str) -> str:
        """Intent ve mesaja göre query_type belirler."""
        if intent == "pharmacy":
            return "health_query"
        if intent == "emergency":
            return "contact_location_query"
        if intent == "weather":
            return "environmental_query"

        msg_lower = user_message.lower()
        if any(w in msg_lower for w in ["nerede", "nasıl gidilir", "yol tarifi", "konum", "adres"]):
            return "contact_location_query"
        if any(w in msg_lower for w in ["telefon", "iletişim", "numarası", "ara"]):
            return "contact_location_query"
        if any(w in msg_lower for w in ["saat", "açık mı", "kapanış", "çalışma"]):
            return "time_query"

        return "general_query"

    @staticmethod
    def is_strict_grounding_intent(intent: str) -> bool:
        return intent in STRICT_GROUNDED_INTENTS
