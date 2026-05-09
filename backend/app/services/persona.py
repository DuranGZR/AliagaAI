"""Persona layer for AliağaAI responses.

This module rewrites already-grounded answers into a friendly local voice
without introducing new factual claims.
"""
from __future__ import annotations

import re
from typing import Any

from app.core.config import settings
from app.services.llm import get_json_response

PERSONA_REWRITE_PROMPT = """Sen Aliağa'da yasayan samimi bir yerel asistansin.

Gorevin:
- VERILEN CEVAP'i daha arkadasca ve sicak bir dille yeniden yaz.
- Yanitin dogrulugunu %100 KORU.

JSON cikti zorunlu:
{"answer":"...", "style_label":"...", "confidence":0.0}

Kesin kurallar:
1) Yeni olgusal bilgi ASLA EKLEME. Kaynaklarda yoksa, "Sistemimde buna dair bilgi bulunmuyor" de.
2) Yeni sayi, tarih, saat, fiyat, kurum, telefon, mahalle veya iddia ASLA EKLEME. Tahmin yürütme.
3) Sadece eldeki metni ifade ve ton duzeyinde donustur.
4) Resmi degil, guven veren ve samimi ol; asiri laubali olma.
5) Kisa ve akici tut: 2-9 cumle.
6) Emoji kullanma.
"""

_FRIENDLY_MARKERS = {
    "kanka",
    "knk",
    "abi",
    "bro",
    "reis",
    "hocam",
    "dostum",
}
_RESPECT_MARKERS = {
    "lutfen",
    "lütfen",
    "rica",
    "tesekkur",
    "teşekkür",
    "siz",
}
_NUMERIC_RE = re.compile(r"\d+(?:[.,]\d+)?")
_CITATION_RE = re.compile(r"\s*\[S\d+\]")

_INTENT_TONE: dict[str, str] = {
    "pharmacy": "pratik_ve_samimi",
    "weather": "pratik_ve_samimi",
    "prayer": "sakin_ve_samimi",
    "fuel": "pratik_ve_samimi",
    "currency": "pratik_ve_samimi",
    "gold": "pratik_ve_samimi",
    "earthquake": "sakin_ve_net",
    "emergency": "sakin_ve_net",
    "market": "pratik_ve_samimi",
    "news": "ozetleyici_ve_samimi",
    "event": "onerici_ve_samimi",
    "announcement": "net_ve_samimi",
    "project": "aciklayici_ve_samimi",
    "job": "yonlendirici_ve_samimi",
    "outage": "sakin_ve_net",
    "place": "yerel_rehber_gibi",
    "city_info": "yerel_rehber_gibi",
    "general": "yerel_rehber_gibi",
    "greeting": "mahalle_arkadasi",
}


def _normalize_answer_text(text: str) -> str:
    cleaned = _CITATION_RE.sub("", text or "")
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    return cleaned


def _coerce_confidence(value: Any, default: float = 0.0) -> float:
    try:
        conf = float(value)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, conf))


def _extract_user_text(conversation_history: list[dict[str, str]] | None) -> str:
    if not conversation_history:
        return ""
    parts: list[str] = []
    for row in conversation_history[-10:]:
        if str(row.get("role") or "").strip().lower() == "user":
            content = str(row.get("content") or "").strip()
            if content:
                parts.append(content.lower())
    return " ".join(parts)


def detect_user_style(
    user_message: str,
    conversation_history: list[dict[str, str]] | None = None,
) -> str:
    text = f"{_extract_user_text(conversation_history)} {user_message or ''}".lower()
    if any(marker in text for marker in _FRIENDLY_MARKERS):
        return "buddy"
    if any(marker in text for marker in _RESPECT_MARKERS):
        return "respectful"
    return "neutral"


def _numeric_tokens(text: str) -> set[str]:
    return set(_NUMERIC_RE.findall(text or ""))


def _has_new_numeric_facts(original: str, rewritten: str) -> bool:
    if not rewritten:
        return False
    old_tokens = _numeric_tokens(original)
    new_tokens = _numeric_tokens(rewritten)
    return len(new_tokens - old_tokens) > 0


def _persona_tone(intent: str, evidence_state: str) -> str:
    base = _INTENT_TONE.get(intent, "samimi_ve_net")
    if evidence_state == "low":
        return "temkinli_ve_samimi"
    return base


def build_persona_greeting(user_style: str = "neutral") -> str:
    if user_style == "buddy":
        return (
            "Selam, ben Aliağa tarafindan bir dost gibi yardimci olayim. "
            "Ulasim, gezi, yeme-icme ya da guncel sehir bilgisi sor, birlikte bakalim."
        )
    if user_style == "respectful":
        return (
            "Merhaba, Aliağa ile ilgili konularda samimi ve net sekilde yardimci olabilirim. "
            "Ulasim, gezi, kurumlar veya guncel bilgilerden hangisiyle baslayalim?"
        )
    return (
        "Merhaba, ben Aliağa tarafini iyi bilen bir asistanim. "
        "Ulasimdan geziye, guncel konulardan kurum bilgilerine kadar ne istersen birlikte bakalim."
    )


async def apply_persona_style(
    *,
    answer: str,
    intent: str,
    user_message: str,
    conversation_history: list[dict[str, str]] | None,
    evidence_state: str,
    response_policy: str,
) -> tuple[str, str, float]:
    """Return (styled_answer, persona_label, persona_confidence)."""
    base_answer = _normalize_answer_text(answer)
    if not settings.PERSONA_ENABLED or not base_answer:
        return base_answer, "persona_off", 0.0

    user_style = detect_user_style(user_message=user_message, conversation_history=conversation_history)
    tone_target = _persona_tone(intent=intent, evidence_state=evidence_state)

    messages = [
        {"role": "system", "content": PERSONA_REWRITE_PROMPT},
        {
            "role": "user",
            "content": (
                f"KULLANICI_STILI: {user_style}\n"
                f"INTENT: {intent}\n"
                f"TONE_TARGET: {tone_target}\n"
                f"RESPONSE_POLICY: {response_policy}\n"
                f"EVIDENCE_STATE: {evidence_state}\n"
                f"SORU: {user_message}\n\n"
                f"YENIDEN_YAZILACAK_CEVAP:\n{base_answer}"
            ),
        },
    ]

    payload = await get_json_response(messages, temperature=settings.PERSONA_TEMPERATURE)
    rewritten = _normalize_answer_text(str(payload.get("answer") or ""))
    style_label = str(payload.get("style_label") or f"local_friend:{tone_target}")
    persona_confidence = _coerce_confidence(payload.get("confidence"), default=0.0)

    if not rewritten:
        return base_answer, "persona_fallback_empty", persona_confidence

    if _has_new_numeric_facts(base_answer, rewritten):
        return base_answer, "persona_guard_numeric", persona_confidence

    return rewritten, style_label, persona_confidence
