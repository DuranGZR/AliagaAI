"""
AliağaAI — Agentic RAG Servisi.

Tüm chat akışını yöneten ana servis. Groq Tool Calling API'sini
kullanarak LLM'in hangi veri kaynağına erişeceğine kendisinin
karar vermesini sağlar.

Akış:
    1. Kullanıcı mesajı + geçmiş → mesaj dizisi oluştur
    2. Groq'a tool tanımlarıyla gönder
    3. LLM tool_call döndürürse → aracı çalıştır → sonuçla tekrar gönder
    4. LLM direkt yanıt döndürürse → al
    5. ChatResponse formatına dönüştür
"""
from __future__ import annotations

import json
from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.schemas.chat import ChatResponse, SourceReference
from app.services.agent.definitions import TOOL_DEFINITIONS
from app.services.agent.prompt import build_messages
from app.services.agent.tools import TOOL_FUNCTIONS
from app.services.llm import create_tool_completion, generate_chat_response
from app.utils.text import (
    coerce_confidence,
    dedupe_sources,
    normalize_answer,
    strip_citations,
    suggestions_for_intent,
)


# ── Araç adından intent eşlemesi ────────────────────────────────────
_TOOL_INTENT_MAP: dict[str, str] = {
    "search_knowledge": "city_info",
    "get_duty_pharmacies": "pharmacy",
    "get_weather": "weather",
    "get_prayer_times": "prayer",
    "get_fuel_prices": "fuel",
    "get_currency_rates": "currency",
    "get_gold_prices": "gold",
    "get_recent_earthquakes": "earthquake",
    "get_emergency_contacts": "emergency",
    "search_news_events": "news",
    "get_transport_schedules": "transport",
    "get_taxi_stands": "taxi",
    "get_postal_codes": "postal_code",
}


def _infer_intent(tool_calls: list[Any] | None) -> str:
    """Çağrılan araçlardan intent çıkar. Birden fazla araç varsa
    ilkine göre karar verir."""
    if not tool_calls:
        return "general"
    first_tool = tool_calls[0].function.name
    return _TOOL_INTENT_MAP.get(first_tool, "general")


def _infer_search_method(tool_calls: list[Any] | None) -> str:
    """Çağrılan araçlardan arama yöntemini belirle."""
    if not tool_calls:
        return "llm_only"

    tool_names = {tc.function.name for tc in tool_calls}

    has_rag = "search_knowledge" in tool_names or "search_news_events" in tool_names
    has_sql = bool(tool_names - {"search_knowledge", "search_news_events"})

    if has_rag and has_sql:
        return "hybrid"
    if has_rag:
        return "rag"
    return "sql"


def _build_sources_from_tool_results(
    tool_calls: list[Any] | None,
) -> list[SourceReference]:
    """Çağrılan araçlara göre kaynak referansları oluştur."""
    if not tool_calls:
        return []

    source_map: dict[str, tuple[str, str]] = {
        "get_duty_pharmacies": ("pharmacy", "Nöbetçi Eczaneler"),
        "get_weather": ("weather", "Hava Durumu"),
        "get_prayer_times": ("prayer", "Namaz Vakitleri"),
        "get_fuel_prices": ("fuel", "Akaryakıt Fiyatları"),
        "get_currency_rates": ("currency", "Döviz Kurları"),
        "get_gold_prices": ("gold", "Altın Fiyatları"),
        "get_recent_earthquakes": ("earthquake", "Son Depremler"),
        "get_emergency_contacts": ("emergency", "Acil Numaralar"),
        "search_knowledge": ("city_info", "Aliağa Bilgi Kaynağı"),
        "search_news_events": ("news", "Haber ve Etkinlikler"),
        "get_transport_schedules": ("transport", "Ulaşım Sefer Saatleri"),
        "get_taxi_stands": ("taxi", "Taksi Durakları"),
        "get_postal_codes": ("postal_code", "Posta Kodları"),
    }

    sources: list[SourceReference] = []
    for tc in tool_calls:
        name = tc.function.name
        if name in source_map:
            stype, title = source_map[name]
            sources.append(SourceReference(type=stype, title=title))

    return dedupe_sources(sources)


async def _execute_tool_call(
    tool_call: Any,
    session: AsyncSession,
) -> str:
    """Tek bir tool_call'ı çalıştırır ve string sonuç döner."""
    func_name = tool_call.function.name
    func = TOOL_FUNCTIONS.get(func_name)

    if not func:
        logger.warning(f"Bilinmeyen araç çağrısı: {func_name}")
        return f"Hata: '{func_name}' aracı bulunamadı."

    # Argümanları parse et
    try:
        args = json.loads(tool_call.function.arguments or "{}")
    except json.JSONDecodeError:
        args = {}

    # Aracı çalıştır
    try:
        result = await func(**args, session=session)
        logger.info(
            f"Araç çalıştırıldı: {func_name}({args}) → {len(result)} karakter"
        )
        return result
    except Exception as exc:
        logger.error(f"Araç çalıştırma hatası ({func_name}): {exc}")
        return f"Araç hatası: {func_name} çalıştırılırken sorun oluştu."


def preprocess_user_query(query: str) -> str:
    """Kullanıcının sorgusundaki yaygın yazım ve klavye hatalarını düzeltir."""
    if not query:
        return query
    
    cleaned = query.strip()
    
    # Sık karşılaşılan klavye hataları ve düzeltmeleri (regex -> replacement)
    typo_map = {
        r"\balaşı(m|mı|ma|mdan|lar|ları|nız|nıza)\b": r"ulaşı\1",
        r"\bnöbetci\b": "nöbetçi",
        r"\bnobetci\b": "nöbetçi",
        r"\bezcane\b": "eczane",
        r"\bezcaneler\b": "eczaneler",
        r"\bezcanesi\b": "eczanesi",
        r"\btaksisi\b": "taksisi",
        r"\btaksiler\b": "taksiler",
        r"\bpostakodu\b": "posta kodu",
        r"\bpostakodları\b": "posta kodları",
        r"\bpostakodunu\b": "posta kodunu",
    }
    
    import re
    for pattern, replacement in typo_map.items():
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        
    return cleaned


class AgenticRAGService:
    """Groq Tool Calling tabanlı Agentic RAG servisi.

    process_chat_query yerine geçer. Tüm intent tespiti, veri çekme,
    bilgi harmanlama ve persona uygulaması tek bir akışta gerçekleşir.
    """

    async def run(
        self,
        session: AsyncSession,
        user_message: str,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> ChatResponse:
        """Ana ajan döngüsü."""
        # Sorguyu ön işlemeden geçir ve yaygın hataları düzelt
        corrected_message = preprocess_user_query(user_message)
        if corrected_message != user_message:
            logger.info(f"[AGENT] Sorgu düzeltildi: '{user_message}' -> '{corrected_message}'")
            
        logger.info(f"[AGENT] Yeni sorgu: {corrected_message}")

        # ── 1. Mesaj dizisini oluştur ──
        messages = build_messages(
            user_message=corrected_message,
            conversation_history=conversation_history,
        )

        # ── 2. İlk Groq çağrısı (tool tanımlarıyla) ──
        completion = await create_tool_completion(
            messages=messages,
            tools=TOOL_DEFINITIONS,
            temperature=settings.AGENT_TEMPERATURE,
            max_tokens=settings.AGENT_MAX_TOKENS,
        )

        if not completion:
            logger.error("[AGENT] Groq API yanıt vermedi, fallback dönülüyor.")
            return self._fallback_response(user_message)

        response_message = completion.choices[0].message
        tool_calls = response_message.tool_calls
        all_tool_calls: list[Any] = []

        # ── 3. Tool calling döngüsü ──
        round_count = 0
        while tool_calls and round_count < settings.AGENT_MAX_TOOL_ROUNDS:
            round_count += 1
            all_tool_calls.extend(tool_calls)

            logger.info(
                f"[AGENT] Döngü {round_count}: {len(tool_calls)} araç çağrısı"
            )

            # Asistan mesajını ekle (tool_calls içeriyor)
            messages.append({
                "role": "assistant",
                "content": response_message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in tool_calls
                ],
            })

            # Her tool call için sonucu çalıştır ve mesaj olarak ekle
            for tc in tool_calls:
                result = await _execute_tool_call(tc, session)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

            # ── 4. Araç sonuçlarıyla ikinci Groq çağrısı ──
            completion = await create_tool_completion(
                messages=messages,
                tools=TOOL_DEFINITIONS,
                temperature=settings.AGENT_TEMPERATURE,
                max_tokens=settings.AGENT_MAX_TOKENS,
            )

            if not completion:
                logger.error("[AGENT] İkinci Groq çağrısı başarısız.")
                return self._fallback_response(user_message)

            response_message = completion.choices[0].message
            tool_calls = response_message.tool_calls

        # ── 5. Nihai yanıtı al ──
        raw_answer = response_message.content or ""
        final_answer = strip_citations(normalize_answer(raw_answer))

        if not final_answer:
            logger.warning("[AGENT] LLM boş yanıt döndü, fallback kullanılıyor.")
            return self._fallback_response(user_message)

        # ── 6. Metadata'yı oluştur ──
        intent = _infer_intent(all_tool_calls)
        search_method = _infer_search_method(all_tool_calls)
        sources = _build_sources_from_tool_results(all_tool_calls)

        # Confidence: araç kullanıldıysa yüksek, kullanılmadıysa düşük
        if all_tool_calls:
            confidence = 0.85
        else:
            confidence = 0.50

        # Response policy
        if all_tool_calls:
            response_policy = "agentic_grounded"
        else:
            response_policy = "agentic_general"

        logger.info(
            f"[AGENT] Yanıt hazır — intent={intent}, method={search_method}, "
            f"tools={len(all_tool_calls)}, rounds={round_count}, "
            f"answer_len={len(final_answer)}"
        )

        return ChatResponse(
            answer=final_answer,
            intent=intent,
            sources=sources,
            search_method=search_method,
            response_policy=response_policy,
            confidence=coerce_confidence(confidence),
            persona_profile="agentic_assistant",
            follow_up_suggestions=suggestions_for_intent(intent),
        )

    def _fallback_response(self, user_message: str) -> ChatResponse:
        """API hatası durumunda güvenli fallback yanıtı."""
        return ChatResponse(
            answer=(
                "Şu an sistemde geçici bir sorun yaşanıyor. "
                "Lütfen birkaç saniye sonra tekrar dener misin?"
            ),
            intent="general",
            sources=[],
            search_method="none",
            response_policy="error_fallback",
            confidence=0.0,
            persona_profile="fallback",
            follow_up_suggestions=[
                "Aliağa hakkında genel bilgi ver",
                "Bugünkü hava durumu nasıl?",
                "Nöbetçi eczane var mı?",
            ],
        )
