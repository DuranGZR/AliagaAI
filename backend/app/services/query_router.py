"""AliagaAI - Query router with explicit response policies.

# Refactored: Pure helper functions extracted to answer_formatters.py

Flow:
- intent detection
- sql / hybrid / rag evidence collection
- policy-based response generation and validation
"""
from __future__ import annotations

import asyncio
import re
import unicodedata
from datetime import date
from typing import Any

from loguru import logger
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database import async_session as async_db_session
from app.models.cache import (
    CurrencyCache,
    EarthquakesCache,
    FuelPricesCache,
    GoldCache,
    PrayerTimesCache,
    WeatherCache,
)
from app.models.city import CityKnowledge, EmergencyContact, StreetMarket, UtilityOutage
from app.models.content import Announcement, Event, JobListing, News, Project
from app.models.places import Institution, Pharmacy, Place
from app.schemas.chat import ChatResponse, SourceReference
from app.services.llm import generate_chat_response, get_json_response
from app.services.persona import apply_persona_style, build_persona_greeting, detect_user_style
from app.services.rag import search_similar_chunks
from app.services.answer_formatters import (
    _normalize_answer_text,
    _strip_citations,
    _remove_low_data_phrase,
    _coerce_confidence,
    _coerce_bool,
    _dedupe_sources,
    _normalize_used_source_ids,
    _suggestions_for_intent,
)


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

GROUNDED_GENERATION_PROMPT = """Sen AliağaAI'sın. Gorevin once verilen BAGLAM'daki bilgilerden dogru, acik ve kullanisli bir temel cevap uretmek.

CIKTI FORMATI (zorunlu JSON):
{"answer": "...", "used_source_ids": [1, 2], "confidence": 0.0}

Kurallar:
1) Bilgiler (adres, telefon, saat, kurum vb.) dogrudan BAGLAM icinden alinmalidir. Uydurma yapma.
2) Kullanici "nerede", "iletisim", "telefon" gibi net bilgiler istediginde paragraf yerine kisa maddelerle (Adres:, Telefon:, Web:, Saatler: vb.) cevap ver.
3) BAGLAM'da net adres veya telefon yoksa, kullaniciyi bir web sitesine "ziyaret edebilirsiniz" diyerek gecistirme; "Eldeki kaynaklarda acik adres/telefon bilgisi bulunamadi" seklinde net belirt.
4) "Yaklasan etkinlikler" gibi zaman sorulan durumlarda, BAGLAM'daki eski tarihli etkinlikleri guncel veya yaklasacak gibi sunma. Sadece etkinlikleri listele.
5) Eger kullanici bugun, yarin veya belli bir konu hakkinda israrla soruyor ve BAGLAM'da hicbir kayit yoksa, "Eldeki kaynaklarda bu bilgiye ulasamadim" de. "Yoktur" gibi kesin konusma.
6) Cevap metnine [Sx] etiketleri yazma; kaynak indekslerini sadece used_source_ids icinde bildir.
7) confidence 0.0-1.0 arasinda ver (Eger sorulan ana bilgi baglamda yoksa dusuk tut).
"""

AUGMENTATION_PROMPT = """Sen AliağaAI'sın. Verilen TEMEL CEVAP'i, model bilgisini kontrollu kullanarak zenginlestir.

CIKTI FORMATI (zorunlu JSON):
{"augmentation": "...", "adds_new_information": true, "confidence": 0.0}

Kurallar:
1) TEMEL CEVAP'taki yerel olgularla celisme; celisen bir sey uretme.
2) BAGLAM'da gecmeyen yeni yerel sayi/tarih/saat/fiyat/kurum/mahalle bilgisi ekleme.
3) Zenginlestirme sadece genel arka plan, pratik oneriler, yorumlama veya planlama ipuclari olsun.
4) Eger guvenli ve faydali bir ekleme yoksa augmentation bos string, adds_new_information false olsun.
5) augmentation en fazla 3 cumle olsun ve TEMEL CEVAP'i tekrar etmesin.
6) confidence 0.0-1.0 araliginda olsun.
"""

MODEL_ONLY_FALLBACK_PROMPT = """Sen AliaÄŸaAI'sÄ±n. Veritabaninda kaynak olmasa da kullaniciya faydali bir ilk yanit ver.

Kurallar:
1) Sadece genel bilgi ve guvenli oneri ver; canli/guncel yerel veri (saat, fiyat, nobet, kesin tarih) uydurma.
2) Yerel kesinlik gerektiren kisimlarda dogrulama ihtiyaci oldugunu kibarca belirt.
3) 3-7 cumlelik akici Turkce cevap yaz.
4) Cevabi dogrudan kullaniciya ver; JSON degil, duz metin.
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
    "job",
    "outage",
})

FLEX_BLEND_INTENTS = {"city_info", "general", "place"}

# TÃ¼m bilinen source_type listesi
_ALL_SOURCE_TYPES = [
    "city_info", "city_knowledge", "place", "institution",
    "transport_route", "transport_stop", "transport_departure",
    "poi_catalog", "municipal_service", "district_stat",
    "news", "event", "announcement", "project", "job", "outage",
    "izban_schedule", "ferry_schedule",
]

INTENT_SOURCE_TYPES: dict[str, list[str] | None] = {
    "place": ["place", "institution", "city_knowledge", "poi_catalog", "city_info"],
    "news": ["news"],
    "event": ["event"],
    "announcement": ["announcement"],
    "project": ["project"],
    "job": ["job"],
    "outage": ["outage"],
    "city_info": [
        "city_info", "city_knowledge",
        "transport_route", "transport_stop", "transport_departure",
        "poi_catalog", "municipal_service", "district_stat",
        "izban_schedule", "ferry_schedule",
        "place", "institution",
    ],
    "general": _ALL_SOURCE_TYPES,  # TÃ¼m kaynaklarda ara
}

FALLBACK_NO_ANSWER = (
    "Eldeki gÃ¼ncel kaynaklarda bu bilgiye ulaÅŸamadÄ±m. "
    "Soruyu biraz daha detaylandÄ±rÄ±rsan â€” Ã¶rneÄŸin mahalle, konu veya tarih belirterek â€” "
    "daha kesin bir yanÄ±t bulabilirim."
)
LOW_EVIDENCE_ANSWER = (
    "Eldeki kaynaklarda bu sorunun net cevabÄ±na ulaÅŸamadÄ±m. "
    "Soruyu biraz daraltÄ±rsan daha kesin bir cevap Ã¼retebilirim."
)
GREETING_ANSWER = (
    "Merhaba! AliaÄŸa hakkÄ±nda kaynaklara dayalÄ± ve detaylÄ± ÅŸekilde yardÄ±mcÄ± olabilirim. "
    "UlaÅŸÄ±m, gezi, gastronomi, kurumlar veya gÃ¼ncel ÅŸehir bilgileriyle ilgili ne Ã¶ÄŸrenmek istersin?"
)

MIN_LOW_CONFIDENCE_FOR_NOTE = 0.10
RAG_CONTEXT_SNIPPET_CHARS = 1200

_QUERY_TYPE_PRIORITY = {
    "contact_location_query": {"municipal_service": 0.15, "city_knowledge": 0.10, "institution": 0.10, "place": 0.05, "city_info": -0.1},
    "transport_query": {"transport_route": 0.15, "transport_stop": 0.10, "transport_departure": 0.10, "izban_schedule": 0.10, "ferry_schedule": 0.10, "city_info": 0.0},
    "health_query": {"institution": 0.15, "place": 0.05, "city_info": -0.05, "city_knowledge": 0.0},
    "event_query": {"event": 0.15, "news": 0.10, "announcement": 0.05, "municipal_service": 0.0},
    "tourism_culture_query": {"city_info": 0.10, "place": 0.10, "poi_catalog": 0.10, "city_knowledge": 0.05, "news": -0.05},
    "general_city_info_query": {"city_info": 0.05, "city_knowledge": 0.05, "district_stat": 0.05, "municipal_service": 0.0},
}

def _detect_query_type(intent: str, question: str) -> str:
    norm = _normalize_search_text(question)
    if any(w in norm for w in ["nerede", "telefon", "iletisim", "saat", "kurum", "belediye", "adres", "mudurlugu"]):
        return "contact_location_query"
    if intent in ["pharmacy", "emergency"] or any(w in norm for w in ["hastane", "saglik", "doktor", "eczane", "tip"]):
        return "health_query"
    if any(w in norm for w in ["nasil gidilir", "ulasim", "izban", "vapur", "feribot", "otobus", "sefer", "durak"]):
        return "transport_query"
    if intent in ["event", "news", "announcement"] or any(w in norm for w in ["etkinlik", "konser", "festival", "haber", "duyuru"]):
        return "event_query"
    if any(w in norm for w in ["turizm", "gezi", "kultur", "muze", "tarihi", "tarih", "antik", "gezilecek"]):
        return "tourism_culture_query"
    return "general_city_info_query"

def _apply_source_priority(chunks: list[dict], query_type: str) -> list[dict]:
    priorities = _QUERY_TYPE_PRIORITY.get(query_type, {})
    for chunk in chunks:
        stype = chunk.get("source_type")
        boost = priorities.get(stype, -0.05)
        original_score = chunk.get("rerank_score", chunk.get("fusion_score", 0.0))
        chunk["rerank_score"] = min(1.0, max(0.0, original_score + boost))
    return sorted(chunks, key=lambda x: x.get("rerank_score", 0.0), reverse=True)

def _dedupe_chunks(chunks: list[dict], max_per_source: int = 2) -> list[dict]:
    counts: dict[str, int] = {}
    deduped: list[dict] = []
    for chunk in chunks:
        meta = chunk.get("metadata") or {}
        stype = chunk.get("source_type", "unknown")
        title = meta.get("title", "")
        sig = f"{stype}::{title}"
        counts[sig] = counts.get(sig, 0) + 1
        if counts[sig] <= max_per_source:
            deduped.append(chunk)
    return deduped

def _truncate_snippet(text: str, max_len: int = RAG_CONTEXT_SNIPPET_CHARS) -> str:
    if len(text) <= max_len:
        return text
    truncated = text[:max_len]
    last_space = truncated.rfind(" ")
    if last_space > max_len * 0.8:
        return truncated[:last_space] + "..."
    return truncated + "..."

INTENT_KEYWORD_OVERRIDES: list[tuple[str, tuple[str, ...]]] = [
    ("greeting", ("merhaba", "selam", "naber", "nasılsın", "iyi akşamlar", "günaydın", "hey", "sa")),
    (
        "place",
        (
            "gezilecek",
            "gezi",
            "turistik",
            "nereye gidilir",
            "kafe",
            "restoran",
            "mekan öner",
            "yer öner",
            "mÃ¼ze",
            "park",
            "plaj",
            "sahil",
        ),
    ),
    (
        "city_info",
        (
            "nasÄ±l gelinir", "ulaÅŸÄ±m", "izban", "otoban", "kaÃ§ km", "konum",
            "nerede", "feribot", "vapur", "tarih", "tarihi", "tarihÃ§e",
            "mahalle", "nÃ¼fus", "sanayi", "ne yapÄ±lÄ±r", "neresi",
            "hakkÄ±nda", "bilgi ver", "anlat", "Ã¶zetle",
            "nasÄ±l bir yer", "neler var", "ne var",
            "ilÃ§e", "coÄŸrafya", "iklim", "ekonomi",
        ),
    ),
]

_TOKEN_RE = re.compile(r"[a-zA-Z0-9Ã§ÄŸÄ±Ã¶ÅŸÃ¼Ã‡ÄÄ°Ã–ÅÃœ]{3,}", re.UNICODE)
_INSTITUTION_QUERY_HINTS = {
    "kurum",
    "kurulus",
    "kuruluÅŸ",
    "belediye",
    "nufus",
    "nÃ¼fus",
    "mudurluk",
    "mÃ¼dÃ¼rlÃ¼k",
    "hastane",
    "okul",
    "noter",
    "kargo",
    "devlet",
    "resmi",
    "sgk",
}
_PLACE_DISCOVERY_HINTS = {
    "gezilecek",
    "gezi",
    "turistik",
    "nerelere gidilir",
    "nerede gezilir",
    "mekan",
    "kafe",
    "restoran",
    "yer Ã¶ner",
}
_WEATHER_OUT_OF_SCOPE_HINTS = {
    "mars",
    "ay",
    "jupiter",
    "saturn",
    "venÃ¼s",
    "venus",
}
_WEATHER_FUTURE_HINTS = {
    "yarÄ±n",
    "haftaya",
    "gelecek hafta",
    "gelecek ay",
    "sonraki hafta",
    "tomorrow",
    "next week",
}
_CITY_INFO_LAYER_HINTS: dict[str, set[str]] = {
    "ulasim": {"ulasim", "ulaÅŸÄ±m", "nasil gelinir", "nasÄ±l gelinir", "izban", "otoyol", "karayolu",
              "feribot", "vapur", "tren", "otobus", "toplu tasima", "toplu taÅŸÄ±ma", "sefer"},
    "gezi": {"gezi", "gezilecek", "turistik", "rota", "antik", "sahil", "plaj",
             "tarih", "tarihi", "tarihÃ§e", "mÃ¼ze", "park", "Ã¶ren", "kale"},
    "gastronomi": {"gastronomi", "yemek", "restoran", "kafe", "tat", "lezzet", "mutfak",
                   "yeme", "iÃ§me", "balÄ±k", "deniz Ã¼rÃ¼nleri"},
    "kurumlar": {"kurum", "belediye", "mÃ¼dÃ¼rlÃ¼k", "mudurluk", "resmi", "hizmet",
                 "hastane", "okul", "sgk", "kaymakamlÄ±k", "noter"},
}
_LAYER_ALLOWED_SOURCE_TYPES: dict[str, set[str]] = {
    "ulasim": {
        "city_info",
        "city_knowledge",
        "transport_route",
        "transport_stop",
        "transport_departure",
        "izban_schedule",
        "ferry_schedule",
    },
    "gezi": {"city_info", "city_knowledge", "place", "institution", "poi_catalog"},
    "gastronomi": {"city_info", "city_knowledge", "place", "institution", "poi_catalog"},
    "kurumlar": {"city_info", "city_knowledge", "institution", "municipal_service", "poi_catalog"},
}
_INTENT_TOKEN_RE = re.compile(r"[a-z0-9]+")

def _strip_diacritics(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))

def _normalize_search_text(text: str) -> str:
    lowered = (text or "").lower().strip()
    return _strip_diacritics(lowered)

def _keywords(text: str, max_terms: int = 6) -> list[str]:
    seen: list[str] = []
    for token in _TOKEN_RE.findall((text or "").lower()):
        if token not in seen:
            seen.append(token)
        if len(seen) >= max_terms:
            break
    return seen

def _override_intent_by_keywords(question: str) -> str | None:
    raw_text = question or ""
    normalized = _normalize_search_text(raw_text)
    tokens = set(_INTENT_TOKEN_RE.findall(normalized))

    def _pattern_matches(pattern: str) -> bool:
        normalized_pattern = _normalize_search_text(pattern)
        if not normalized_pattern:
            return False
        if " " in normalized_pattern:
            return normalized_pattern in normalized
        if len(normalized_pattern) <= 2:
            return normalized == normalized_pattern or normalized_pattern in tokens
        return normalized_pattern in tokens

    for intent, patterns in INTENT_KEYWORD_OVERRIDES:
        if any(_pattern_matches(pattern) for pattern in patterns):
            if intent == "greeting" and len(tokens) > 3:
                continue
            return intent
    return None

def _is_institution_query(question: str) -> bool:
    tokens = set(_keywords(question, max_terms=12))
    return any(token in _INSTITUTION_QUERY_HINTS for token in tokens)

def _is_place_discovery_query(question: str) -> bool:
    lowered = (question or "").lower()
    return any(hint in lowered for hint in _PLACE_DISCOVERY_HINTS)

def _is_sql_scope_mismatch(intent: str, question: str) -> bool:
    normalized = _normalize_search_text(question)
    if intent != "weather":
        return False
    if any(_normalize_search_text(hint) in normalized for hint in _WEATHER_FUTURE_HINTS):
        return True
    return any(_normalize_search_text(hint) in normalized for hint in _WEATHER_OUT_OF_SCOPE_HINTS)

def _infer_city_info_layer(question: str) -> str | None:
    normalized = _normalize_search_text(question)
    scores: dict[str, int] = {}
    for layer, hints in _CITY_INFO_LAYER_HINTS.items():
        score = sum(1 for hint in hints if _normalize_search_text(hint) in normalized)
        if score > 0:
            scores[layer] = score
    if not scores:
        return None
    return max(scores.items(), key=lambda item: item[1])[0]

def _chunk_matches_city_layer(chunk: dict, target_layer: str) -> bool:
    source_type = chunk.get("source_type")
    metadata = chunk.get("metadata") or {}
    allowed_source_types = _LAYER_ALLOWED_SOURCE_TYPES.get(target_layer)
    if allowed_source_types and source_type and source_type not in allowed_source_types:
        return False

    if source_type == "city_knowledge":
        return (metadata.get("layer") or "").strip().lower() == target_layer

    if source_type != "city_info":
        return True

    haystack = " ".join(
        [
            str(metadata.get("title") or ""),
            str(metadata.get("url") or ""),
            str(chunk.get("content") or "")[:500],
        ]
    )
    normalized = _normalize_search_text(haystack)
    layer_hints = _CITY_INFO_LAYER_HINTS.get(target_layer, set())
    return any(_normalize_search_text(hint) in normalized for hint in layer_hints)

def _filter_city_info_chunks_by_layer(question: str, chunks: list[dict]) -> list[dict]:
    target_layer = _infer_city_info_layer(question)
    if not target_layer:
        return chunks
    filtered = [chunk for chunk in chunks if _chunk_matches_city_layer(chunk, target_layer)]
    return filtered or chunks

def _format_context_from_evidence(sql_context: str, rag_chunks: list[dict]) -> str:
    lines: list[str] = []
    if sql_context:
        lines.append("[SQL]")
        lines.append(sql_context)
    if rag_chunks:
        lines.append("[RAG]")
        for idx, chunk in enumerate(rag_chunks, start=1):
            chunk_content = chunk.get("content") or ""
            snippet = _truncate_snippet(chunk_content)
            is_truncated = len(chunk_content) > RAG_CONTEXT_SNIPPET_CHARS
            title = (chunk.get("metadata") or {}).get("title", "Bilinmeyen Kaynak")
            score = chunk.get("rerank_score", chunk.get("fusion_score", 0.0))
            logger.debug(f"[RAG_DEBUG] Context Chunk {idx} - type={chunk.get('source_type')}, title='{title}', score={score:.3f}, len={len(chunk_content)}, truncated={is_truncated}, preview='{snippet[:200]}'")
            lines.append(f"- ({chunk.get('source_type', 'rag')}) {title} | score={score:.3f}\n{snippet}")
    
    formatted_context = "\n".join(lines).strip()
    logger.debug(f"[RAG_DEBUG] Context Prep - Total length: {len(formatted_context)}, SQL length: {len(sql_context)}, RAG chunks: {len(rag_chunks)}")
    return formatted_context

def _build_rag_sources(rag_chunks: list[dict]) -> list[SourceReference]:
    refs: list[SourceReference] = []
    for chunk in rag_chunks:
        meta = chunk.get("metadata", {}) or {}
        refs.append(
            SourceReference(
                type=chunk.get("source_type", "rag"),
                title=meta.get("title") or "AliaÄŸa Bilgi KaynaÄŸÄ±",
                url=meta.get("url"),
                date=meta.get("date") or meta.get("last_verified_at"),
            )
        )
    return refs

def _build_source_catalog(sources: list[SourceReference]) -> str:
    if not sources:
        return ""
    lines = ["[KAYNAK DIZINI]"]
    for idx, source in enumerate(sources, start=1):
        label = source.title or source.type
        url_part = f" | {source.url}" if source.url else ""
        date_part = f" | {source.date}" if source.date else ""
        lines.append(f"[S{idx}] {source.type} | {label}{date_part}{url_part}")
        logger.debug(f"[RAG_DEBUG] Source Catalog [S{idx}]: type={source.type}, title='{source.title}', url='{source.url}'")
    
    logger.debug(f"[RAG_DEBUG] Source Catalog Prep - Total sources: {len(sources)}")
    return "\n".join(lines)

def _rag_confidence(chunks: list[dict]) -> float:
    if not chunks:
        return 0.0
    head = chunks[: min(3, len(chunks))]
    scores = [c.get("rerank_score", c.get("fusion_score", c.get("similarity", 0.0))) for c in head]
    return sum(scores) / len(scores)

def _select_sources_by_ids(sources: list[SourceReference], source_ids: list[int]) -> list[SourceReference]:
    if not sources:
        return []
    if not source_ids:
        return sources[: min(4, len(sources))]
    selected: list[SourceReference] = []
    for source_id in source_ids:
        idx = source_id - 1
        if 0 <= idx < len(sources):
            selected.append(sources[idx])
    
    final_selected = _dedupe_sources(selected)[: min(4, len(selected))]
    logger.debug(f"[RAG_DEBUG] Source Selection - Input sources: {len(sources)}, used_source_ids: {source_ids}, Output sources: {len(final_selected)}. Selected titles: {[s.title for s in final_selected]}")
    return final_selected

def _format_sql_template_answer(raw_data: str) -> str:
    lines = [line.strip() for line in (raw_data or "").splitlines() if line.strip()]
    if not lines:
        return ""
    if len(lines) <= 7:
        return "\n".join(lines)
    return "\n".join(lines[:7])

def _is_sql_no_data(raw_data: str, sources: list[SourceReference]) -> bool:
    text = (raw_data or "").lower()
    if sources:
        return False
    return (not text) or ("bulunamad" in text) or ("eÅŸleÅŸtirilemedi" in text)

def _evidence_state(
    search_method: str,
    sources: list[SourceReference],
    rag_chunks: list[dict],
    sql_rows_count: int,
    confidence: float,
) -> str:
    if not sources:
        return "none"
    if search_method == "sql":
        return "high"

    has_min_evidence = (len(rag_chunks) >= settings.RAG_MIN_EVIDENCE_CHUNKS) or (sql_rows_count > 0)
    if has_min_evidence and confidence >= settings.RAG_MIN_EVIDENCE_CONFIDENCE:
        return "high"

    if (not has_min_evidence and sql_rows_count == 0) or confidence < MIN_LOW_CONFIDENCE_FOR_NOTE:
        return "low"

    return "medium"

def _normalize_conversation_history(
    conversation_history: list[dict[str, str]] | None,
    max_items: int = 10,
) -> list[dict[str, str]]:
    if not conversation_history:
        return []

    safe_messages: list[dict[str, str]] = []
    for item in conversation_history[-max_items:]:
        role = str(item.get("role") or "").strip().lower()
        content = str(item.get("content") or "").strip()
        if role not in {"user", "assistant"} or not content:
            continue
        safe_messages.append({"role": role, "content": content[:2000]})
    return safe_messages

async def _apply_persona_if_enabled(
    *,
    answer: str,
    intent: str,
    user_message: str,
    conversation_history: list[dict[str, str]] | None,
    evidence_state: str,
    response_policy: str,
) -> tuple[str, str]:
    if not answer:
        return answer, "persona_empty"

    if not settings.PERSONA_ENABLED:
        return answer, "persona_off"

    styled, profile, _persona_conf = await apply_persona_style(
        answer=answer,
        intent=intent,
        user_message=user_message,
        conversation_history=conversation_history,
        evidence_state=evidence_state,
        response_policy=response_policy,
    )
    if not styled:
        return answer, "persona_fallback"
    return styled, profile

def _is_strict_grounding_intent(intent: str) -> bool:
    return intent in STRICT_GROUNDED_INTENTS

def _can_use_model_only_fallback(intent: str) -> bool:
    return settings.RAG_ENABLE_MODEL_ONLY_FALLBACK and intent in FLEX_BLEND_INTENTS

def _should_attempt_augmentation(
    intent: str,
    sources: list[SourceReference],
    evidence_state: str,
    evidence_confidence: float,
    query_type: str = "general_city_info_query",
) -> bool:
    if not settings.RAG_ENABLE_CONTROLLED_AUGMENTATION:
        return False
    if intent not in FLEX_BLEND_INTENTS or not sources:
        return False
    if evidence_state == "low":
        return False
    if query_type in {"contact_location_query", "transport_query", "health_query"}:
        return False
    return evidence_confidence >= settings.RAG_AUGMENTATION_MIN_EVIDENCE

def _merge_grounded_and_augmented(grounded_answer: str, augmentation: str) -> str:
    grounded = (grounded_answer or "").strip()
    extra = (augmentation or "").strip()

    if not grounded:
        return extra
    if not extra:
        return grounded

    if _normalize_search_text(extra) in _normalize_search_text(grounded):
        return grounded

    return f"{grounded}\n\n{extra}"

async def _generate_structured_grounded_answer(
    user_message: str,
    context_data: str,
    sources: list[SourceReference],
    conversation_history: list[dict[str, str]] | None = None,
) -> tuple[str, list[int], float]:
    source_count = len(sources)
    messages = [{"role": "system", "content": GROUNDED_GENERATION_PROMPT}]
    messages.extend(_normalize_conversation_history(conversation_history, max_items=10))

    messages.append(
        {
            "role": "user",
            "content": (
                f"SORU:\n{user_message}\n\n"
                f"BAGLAM:\n{context_data}\n\n"
                f"Gecerli source id araligi: 1-{source_count}."
            ),
        }
    )

    payload = await get_json_response(messages)
    answer = str(payload.get("answer") or "").strip()
    used_source_ids = _normalize_used_source_ids(payload.get("used_source_ids"), source_count)
    llm_confidence = _coerce_confidence(payload.get("confidence"), default=0.0)

    if not answer:
        fallback_messages = [
            {
                "role": "system",
                "content": (
                    "Sadece verilen baglama dayanarak Turkce ve aciklayici (5-8 cumle) cevap ver. "
                    "Baglamda olmayan ozel isim veya mekan adini ekleme. "
                    "Kaynak satirlarini kopyalama."
                ),
            },
            {"role": "user", "content": f"Soru: {user_message}\n\nBaglam:\n{context_data}"},
        ]
        fallback_messages[1:1] = _normalize_conversation_history(conversation_history, max_items=6)
        fallback_answer = await generate_chat_response(fallback_messages)
        answer = (fallback_answer or "").strip()

    answer = _normalize_answer_text(_strip_citations(answer))

    if source_count == 0:
        used_source_ids = []

    return answer, used_source_ids, llm_confidence

async def _generate_controlled_augmentation(
    user_message: str,
    context_data: str,
    grounded_answer: str,
    conversation_history: list[dict[str, str]] | None = None,
) -> tuple[str, bool, float]:
    messages = [{"role": "system", "content": AUGMENTATION_PROMPT}]
    messages.extend(_normalize_conversation_history(conversation_history, max_items=6))
    messages.append(
        {
            "role": "user",
            "content": (
                f"SORU:\n{user_message}\n\n"
                f"TEMEL CEVAP:\n{grounded_answer}\n\n"
                f"BAGLAM OZETI:\n{context_data[:3500]}"
            ),
        }
    )

    payload = await get_json_response(messages)
    augmentation = str(payload.get("augmentation") or "").strip()
    adds_new_information = _coerce_bool(payload.get("adds_new_information"))
    augmentation_confidence = _coerce_confidence(payload.get("confidence"), default=0.0)

    augmentation = _normalize_answer_text(_strip_citations(augmentation))
    if not augmentation:
        return "", False, augmentation_confidence

    if _normalize_search_text(augmentation) == _normalize_search_text(grounded_answer):
        return "", False, augmentation_confidence

    return augmentation, adds_new_information, augmentation_confidence

async def _generate_model_only_fallback_answer(
    user_message: str,
    conversation_history: list[dict[str, str]] | None = None,
) -> str:
    messages = [{"role": "system", "content": MODEL_ONLY_FALLBACK_PROMPT}]
    messages.extend(_normalize_conversation_history(conversation_history, max_items=6))
    messages.append({"role": "user", "content": user_message})
    answer = await generate_chat_response(messages)
    return _normalize_answer_text(_strip_citations((answer or "").strip()))

async def determine_intent(question: str) -> str:
    """Determine intent from user question (keyword override first, LLM second)."""
    forced_intent = _override_intent_by_keywords(question)
    if forced_intent:
        return forced_intent

    messages = [
        {"role": "system", "content": INTENT_SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    response = await get_json_response(messages)
    intent = (response.get("intent") or "general").strip().lower()

    allowed_intents = SQL_ONLY_INTENTS.union(HYBRID_INTENTS).union({"city_info", "general", "greeting"})
    if intent not in allowed_intents:
        return "general"
    return intent

async def execute_sql_query(session: AsyncSession, intent: str, query: str) -> dict:
    """SQL-only intents."""
    data_str = ""
    sources_data: list[SourceReference] = []

    if intent == "pharmacy":
        stmt = select(Pharmacy).where(Pharmacy.duty_date == date.today())
        pharmacies = (await session.execute(stmt)).scalars().all()
        if not pharmacies:
            data_str = "BugÃ¼n iÃ§in nÃ¶betÃ§i eczane verisi bulunamadÄ±."
        else:
            lines = [f"- {p.name} (Adres: {p.address}, Tel: {p.phone})" for p in pharmacies]
            data_str = "BugÃ¼nkÃ¼ NÃ¶betÃ§i Eczaneler:\n" + "\n".join(lines)
            sources_data.append(SourceReference(type="pharmacy", title="BugÃ¼nkÃ¼ NÃ¶betÃ§i Eczaneler"))

    elif intent == "weather":
        weather = (
            await session.execute(select(WeatherCache).order_by(WeatherCache.date.desc()).limit(1))
        ).scalars().first()
        if not weather:
            data_str = "GÃ¼ncel hava durumu verisi bulunamadÄ±."
        else:
            data_str = (
                f"BugÃ¼n hava {weather.temperature}Â°C, {weather.description}. "
                f"RÃ¼zgar: {weather.wind}, Nem: {weather.humidity}."
            )
            sources_data.append(SourceReference(type="weather", title="AliaÄŸa Hava Durumu"))

    elif intent == "prayer":
        prayer = (
            await session.execute(select(PrayerTimesCache).order_by(PrayerTimesCache.date.desc()).limit(1))
        ).scalars().first()
        if not prayer:
            data_str = "GÃ¼ncel namaz vakitleri bulunamadÄ±."
        else:
            data_str = (
                "Namaz Vakitleri:\n"
                f"Ä°msak: {prayer.fajr}\nGÃ¼neÅŸ: {prayer.sunrise}\nÃ–ÄŸle: {prayer.dhuhr}\n"
                f"Ä°kindi: {prayer.asr}\nAkÅŸam: {prayer.maghrib}\nYatsÄ±: {prayer.isha}"
            )
            sources_data.append(SourceReference(type="prayer", title="Namaz Vakitleri"))

    elif intent == "fuel":
        fuel = (
            await session.execute(select(FuelPricesCache).order_by(FuelPricesCache.fetched_at.desc()).limit(1))
        ).scalars().first()
        if not fuel:
            data_str = "GÃ¼ncel akaryakÄ±t verisi bulunamadÄ±."
        else:
            data_str = f"AkaryakÄ±t FiyatlarÄ±: Benzin {fuel.gasoline} TL, Motorin {fuel.diesel} TL, LPG {fuel.lpg} TL."
            sources_data.append(SourceReference(type="fuel", title="AkaryakÄ±t FiyatlarÄ±"))

    elif intent == "currency":
        currencies = (await session.execute(select(CurrencyCache))).scalars().all()
        if not currencies:
            data_str = "GÃ¼ncel dÃ¶viz kurlarÄ± bulunamadÄ±."
        else:
            lines = [f"{c.name}: AlÄ±ÅŸ {c.buying} TL, SatÄ±ÅŸ {c.selling} TL" for c in currencies]
            data_str = "GÃ¼ncel DÃ¶viz KurlarÄ±:\n" + "\n".join(lines)
            sources_data.append(SourceReference(type="currency", title="DÃ¶viz KurlarÄ±"))

    elif intent == "gold":
        golds = (await session.execute(select(GoldCache))).scalars().all()
        if not golds:
            data_str = "GÃ¼ncel altÄ±n fiyatlarÄ± bulunamadÄ±."
        else:
            lines = [f"{g.name}: AlÄ±ÅŸ {g.buying} TL, SatÄ±ÅŸ {g.selling} TL" for g in golds]
            data_str = "GÃ¼ncel AltÄ±n FiyatlarÄ±:\n" + "\n".join(lines)
            sources_data.append(SourceReference(type="gold", title="AltÄ±n FiyatlarÄ±"))

    elif intent == "earthquake":
        quakes = (
            await session.execute(select(EarthquakesCache).order_by(EarthquakesCache.event_date.desc()).limit(5))
        ).scalars().all()
        if not quakes:
            data_str = "Deprem verisi bulunamadÄ±."
        else:
            lines = [f"{q.magnitude} ÅŸiddetinde, {q.location} (Tarih: {q.event_date})" for q in quakes]
            data_str = "Son 5 Deprem:\n" + "\n".join(lines)
            sources_data.append(SourceReference(type="earthquake", title="Kandilli Son Depremler"))

    elif intent == "emergency":
        contacts = (await session.execute(select(EmergencyContact).order_by(EmergencyContact.priority.asc()))).scalars().all()
        if not contacts:
            data_str = "Acil durum numaralarÄ± bulunamadÄ±."
        else:
            lines = [f"{c.name}: {c.phone}" for c in contacts]
            data_str = "Acil ve Ã–nemli Numaralar:\n" + "\n".join(lines)
            sources_data.append(SourceReference(type="emergency", title="Acil Telefonlar"))

    elif intent == "market":
        markets = (await session.execute(select(StreetMarket))).scalars().all()
        if not markets:
            data_str = "Semt pazarÄ± bilgisi bulunamadÄ±."
        else:
            lines = [f"{m.name} - GÃ¼n: {m.day_of_week} ({m.neighborhood})" for m in markets]
            data_str = "Semt PazarlarÄ± ve GÃ¼nleri:\n" + "\n".join(lines)
            sources_data.append(SourceReference(type="market", title="Semt PazarlarÄ±"))

    else:
        data_str = "Ä°stenen veriye dair kategori eÅŸleÅŸtirilemedi."

    return {"raw_data": data_str, "sources": sources_data}

def _like_filters(keywords: list[str], columns: list[Any]) -> Any | None:
    conditions = []
    for keyword in keywords:
        pattern = f"%{keyword}%"
        for col in columns:
            conditions.append(col.ilike(pattern))
    if not conditions:
        return None
    return or_(*conditions)

async def execute_hybrid_sql_query(session: AsyncSession, intent: str, query: str, limit: int = 5) -> dict:
    """Collect fast SQL evidence for hybrid intents."""
    kws = _keywords(query)
    lines: list[str] = []
    sources: list[SourceReference] = []
    rows_count = 0

    if intent == "news":
        filt = _like_filters(kws, [News.title, News.content])
        stmt = select(News)
        if filt is not None:
            stmt = stmt.where(filt)
        rows = (await session.execute(stmt.order_by(News.published_at.desc()).limit(limit))).scalars().all()
        rows_count = len(rows)
        for row in rows:
            lines.append(f"- {row.title} ({row.published_at})")
            sources.append(
                SourceReference(
                    type="news",
                    title=row.title,
                    url=row.source_url,
                    date=str(row.published_at) if row.published_at else None,
                )
            )

    elif intent == "event":
        norm_q = _normalize_search_text(query)
        future_hints = ["yaklasan", "bugun", "yarin", "guncel", "hafta", "gelecek", "onumuzdeki"]
        is_future_query = any(h in norm_q for h in future_hints)
        
        filt = _like_filters(kws, [Event.title, Event.description, Event.location])
        stmt = select(Event)
        if filt is not None:
            stmt = stmt.where(filt)
            
        if is_future_query:
            stmt = stmt.where(Event.event_date >= date.today())
            stmt = stmt.order_by(Event.event_date.asc())
        else:
            stmt = stmt.order_by(Event.event_date.desc())
            
        rows = (await session.execute(stmt.limit(limit))).scalars().all()
        rows_count = len(rows)
        for row in rows:
            lines.append(f"- {row.title} ({row.event_date}) @ {row.location or 'BelirtilmemiÅŸ'}")
            sources.append(
                SourceReference(
                    type="event",
                    title=row.title,
                    url=row.source_url,
                    date=str(row.event_date) if row.event_date else None,
                )
            )

    elif intent == "announcement":
        filt = _like_filters(kws, [Announcement.title, Announcement.content])
        stmt = select(Announcement)
        if filt is not None:
            stmt = stmt.where(filt)
        rows = (await session.execute(stmt.order_by(Announcement.published_at.desc()).limit(limit))).scalars().all()
        rows_count = len(rows)
        for row in rows:
            lines.append(f"- {row.title} ({row.type})")
            sources.append(
                SourceReference(
                    type="announcement",
                    title=row.title,
                    url=row.source_url,
                    date=str(row.published_at) if row.published_at else None,
                )
            )

    elif intent == "project":
        filt = _like_filters(kws, [Project.title, Project.description, Project.status, Project.category])
        stmt = select(Project)
        if filt is not None:
            stmt = stmt.where(filt)
        rows = (await session.execute(stmt.order_by(Project.created_at.desc()).limit(limit))).scalars().all()
        rows_count = len(rows)
        for row in rows:
            lines.append(f"- {row.title} (Durum: {row.status})")
            sources.append(SourceReference(type="project", title=row.title, url=row.source_url))

    elif intent == "job":
        filt = _like_filters(kws, [JobListing.title, JobListing.description, JobListing.company, JobListing.location])
        stmt = select(JobListing).where(JobListing.is_active.is_(True))
        if filt is not None:
            stmt = stmt.where(filt)
        rows = (await session.execute(stmt.order_by(JobListing.published_at.desc()).limit(limit))).scalars().all()
        rows_count = len(rows)
        for row in rows:
            lines.append(f"- {row.title} ({row.company or 'Firma belirtilmemiÅŸ'})")
            sources.append(
                SourceReference(
                    type="job",
                    title=row.title,
                    url=row.source_url,
                    date=str(row.published_at) if row.published_at else None,
                )
            )

    elif intent == "outage":
        filt = _like_filters(kws, [UtilityOutage.description, UtilityOutage.neighborhood, UtilityOutage.district, UtilityOutage.type])
        stmt = select(UtilityOutage)
        if filt is not None:
            stmt = stmt.where(filt)
        rows = (await session.execute(stmt.order_by(UtilityOutage.start_date.desc()).limit(limit))).scalars().all()
        rows_count = len(rows)
        for row in rows:
            lines.append(f"- {row.type.upper()} kesintisi | {row.neighborhood or row.district or 'Konum yok'}")
            sources.append(SourceReference(type="outage", title=f"{row.type.upper()} Kesintisi", url=row.source))

    elif intent == "place":
        include_institutions = _is_institution_query(query)

        place_filter = _like_filters(kws, [Place.name, Place.description, Place.category, Place.subcategory, Place.address])
        place_stmt = select(Place).where(Place.is_active.is_(True))
        if place_filter is not None:
            place_stmt = place_stmt.where(place_filter)
        places = (await session.execute(place_stmt.order_by(Place.rating.desc()).limit(limit))).scalars().all()

        institutions = []
        if include_institutions:
            institution_filter = _like_filters(
                kws,
                [Institution.name, Institution.description, Institution.category, Institution.subcategory, Institution.address],
            )
            inst_stmt = select(Institution).where(Institution.is_active.is_(True))
            if institution_filter is not None:
                inst_stmt = inst_stmt.where(institution_filter)
            institutions = (await session.execute(inst_stmt.order_by(Institution.updated_at.desc()).limit(limit))).scalars().all()

        if not places and not institutions and _is_place_discovery_query(query):
            places = (
                await session.execute(
                    select(Place).where(Place.is_active.is_(True)).order_by(Place.rating.desc()).limit(limit)
                )
            ).scalars().all()
            if include_institutions:
                institutions = (
                    await session.execute(
                        select(Institution)
                        .where(Institution.is_active.is_(True))
                        .order_by(Institution.updated_at.desc())
                        .limit(limit)
                    )
                ).scalars().all()

        rows_count = len(places) + len(institutions)
        for row in places:
            lines.append(f"- {row.name} ({row.category})")
            sources.append(SourceReference(type="place", title=row.name, url=row.website))
        for row in institutions:
            lines.append(f"- {row.name} ({row.category})")
            sources.append(SourceReference(type="institution", title=row.name, url=row.website))

    return {
        "raw_data": "\n".join(lines).strip(),
        "sources": sources,
        "row_count": rows_count,
    }

async def execute_city_info_sql_query(session: AsyncSession, query: str, limit: int = 5) -> dict:
    """city_info iÃ§in hÄ±zlÄ± SQL fallback (embedding gecikmelerinde devreye girer)."""
    keywords = _keywords(query, max_terms=8)
    inferred_layer = _infer_city_info_layer(query)

    stmt = select(CityKnowledge)
    if inferred_layer:
        stmt = stmt.where(CityKnowledge.layer == inferred_layer)

    filter_conditions = _like_filters(keywords, [CityKnowledge.title, CityKnowledge.summary, CityKnowledge.neighborhood])
    if filter_conditions is not None:
        stmt = stmt.where(filter_conditions)

    rows = (await session.execute(stmt.order_by(CityKnowledge.last_verified_at.desc()).limit(limit))).scalars().all()
    if not rows and inferred_layer:
        rows = (
            await session.execute(
                select(CityKnowledge)
                .where(CityKnowledge.layer == inferred_layer)
                .order_by(CityKnowledge.last_verified_at.desc())
                .limit(limit)
            )
        ).scalars().all()

    lines: list[str] = []
    sources: list[SourceReference] = []
    for row in rows:
        neighborhood = f" ({row.neighborhood})" if row.neighborhood else ""
        lines.append(f"- [{row.layer}] {row.title}{neighborhood}: {row.summary}")
        sources.append(
            SourceReference(
                type="city_knowledge",
                title=row.title,
                url=row.source_url,
                date=str(row.last_verified_at) if row.last_verified_at else None,
            )
        )

    return {
        "raw_data": "\n".join(lines).strip(),
        "sources": sources,
        "row_count": len(rows),
    }

async def _fetch_rag_chunks(
    query: str,
    source_types: list[str] | None,
    session: AsyncSession | None = None,
    is_factual: bool = False,
) -> list[dict]:
    if session is not None:
        return await search_similar_chunks(
            session=session,
            query=query,
            limit=settings.RAG_TOP_K,
            min_similarity=settings.RAG_MIN_SIMILARITY,
            source_types=source_types,
            is_factual=is_factual,
        )

    async with async_db_session() as isolated_session:
        return await search_similar_chunks(
            session=isolated_session,
            query=query,
            limit=settings.RAG_TOP_K,
            min_similarity=settings.RAG_MIN_SIMILARITY,
            source_types=source_types,
            is_factual=is_factual,
        )

async def process_chat_query(
    session: AsyncSession, 
    user_message: str,
    conversation_history: list[dict[str, str]] | None = None
) -> ChatResponse:
    """End-to-end chat processing with explicit response policy layer."""
    logger.info(f"YENI SORGU: {user_message}")
    logger.debug(f"[RAG_DEBUG] Request start - query: '{user_message}', history_len: {len(conversation_history) if conversation_history else 0}")
    intent = await determine_intent(user_message)
    query_type = _detect_query_type(intent, user_message)
    is_factual = query_type in {"contact_location_query", "health_query", "transport_query"}
    logger.info(f"Tespit edilen intent: {intent}, query_type: {query_type}")
    logger.debug(f"[RAG_DEBUG] Intent detected: '{intent}', query_type: '{query_type}', strict_grounding: {_is_strict_grounding_intent(intent)}")

    if intent == "greeting":
        user_style = detect_user_style(user_message=user_message, conversation_history=conversation_history)
        greeting_answer = GREETING_ANSWER
        persona_profile = "persona_off"
        if settings.PERSONA_ENABLED:
            greeting_answer = build_persona_greeting(user_style=user_style)
            persona_profile = f"greeting:{user_style}"
        return ChatResponse(
            answer=greeting_answer,
            intent=intent,
            sources=[],
            search_method="none",
            response_policy="greeting",
            confidence=1.0,
            persona_profile=persona_profile,
            follow_up_suggestions=_suggestions_for_intent(intent),
        )

    if intent in SQL_ONLY_INTENTS:
        if _is_sql_scope_mismatch(intent, user_message):
            raw_answer = (
                "Bu soru mevcut veri kapsamimin disinda kaliyor. "
                "Su an Aliaga ve yakin cevre icin guncel verilerle yanit verebiliyorum; "
                "istersen Aliaga icin guncel hava durumunu paylasabilirim."
            )
            styled_answer, persona_profile = await _apply_persona_if_enabled(
                answer=raw_answer,
                intent=intent,
                user_message=user_message,
                conversation_history=conversation_history,
                evidence_state="none",
                response_policy="no_answer",
            )
            return ChatResponse(
                answer=styled_answer,
                intent=intent,
                sources=[],
                search_method="sql",
                response_policy="no_answer",
                confidence=0.0,
                persona_profile=persona_profile,
                follow_up_suggestions=_suggestions_for_intent(intent),
            )
        sql_result = await execute_sql_query(session, intent, user_message)
        sources = _dedupe_sources(sql_result["sources"])
        raw_data = sql_result["raw_data"]
        logger.debug(f"[RAG_DEBUG] SQL retrieval executed (SQL_ONLY). Intent: {intent}. Results count: {len(sources)}, raw_data len: {len(raw_data)}, is_empty: {not bool(raw_data.strip())}")

        if _is_sql_no_data(raw_data, sources):
            styled_answer, persona_profile = await _apply_persona_if_enabled(
                answer=FALLBACK_NO_ANSWER,
                intent=intent,
                user_message=user_message,
                conversation_history=conversation_history,
                evidence_state="none",
                response_policy="no_answer",
            )
            return ChatResponse(
                answer=styled_answer,
                intent=intent,
                sources=[],
                search_method="sql",
                response_policy="no_answer",
                confidence=0.0,
                persona_profile=persona_profile,
                follow_up_suggestions=_suggestions_for_intent(intent),
            )

        sql_answer = _format_sql_template_answer(raw_data)
        styled_answer, persona_profile = await _apply_persona_if_enabled(
            answer=sql_answer,
            intent=intent,
            user_message=user_message,
            conversation_history=conversation_history,
            evidence_state="high",
            response_policy="sql_only",
        )

        return ChatResponse(
            answer=styled_answer,
            intent=intent,
            sources=sources,
            search_method="sql",
            response_policy="sql_only",
            confidence=1.0 if sources else 0.7,
            persona_profile=persona_profile,
            follow_up_suggestions=_suggestions_for_intent(intent),
        )

    search_method = "hybrid" if intent in HYBRID_INTENTS else "rag"
    sources: list[SourceReference] = []
    rag_chunks: list[dict] = []
    sql_rows_count = 0
    sql_context = ""
    source_types = INTENT_SOURCE_TYPES.get(intent)

    if intent in HYBRID_INTENTS and settings.RAG_SKIP_VECTOR_WHEN_SQL_HIT and intent in STRICT_GROUNDED_INTENTS:
        hybrid_sql = await execute_hybrid_sql_query(session, intent, user_message, limit=settings.RAG_TOP_K)
        sql_context = hybrid_sql["raw_data"]
        sql_rows_count = hybrid_sql["row_count"]
        sources.extend(hybrid_sql["sources"])

        if sql_rows_count == 0:
            rag_chunks = await _fetch_rag_chunks(
                query=user_message,
                source_types=source_types,
                session=session,
            )
    elif intent in HYBRID_INTENTS:
        if settings.RAG_PARALLEL_RETRIEVAL_ENABLED:
            hybrid_sql_task = asyncio.create_task(
                execute_hybrid_sql_query(session, intent, user_message, limit=settings.RAG_TOP_K)
            )
            rag_task = asyncio.create_task(
                _fetch_rag_chunks(
                    query=user_message,
                    source_types=source_types,
                    session=None,
                )
            )
            hybrid_sql, rag_chunks = await asyncio.gather(hybrid_sql_task, rag_task)
        else:
            hybrid_sql = await execute_hybrid_sql_query(session, intent, user_message, limit=settings.RAG_TOP_K)
            rag_chunks = await _fetch_rag_chunks(
                query=user_message,
                source_types=source_types,
                is_factual=is_factual,
                session=session,
            )

        sql_context = hybrid_sql["raw_data"]
        sql_rows_count = hybrid_sql["row_count"]
        sources.extend(hybrid_sql["sources"])
    elif intent == "city_info":
        if settings.RAG_PARALLEL_RETRIEVAL_ENABLED:
            city_sql_task = asyncio.create_task(
                execute_city_info_sql_query(session, user_message, limit=settings.RAG_TOP_K)
            )
            rag_task = asyncio.create_task(
                _fetch_rag_chunks(
                    query=user_message,
                    source_types=source_types,
                    session=None,
                )
            )
            city_sql, rag_chunks = await asyncio.gather(city_sql_task, rag_task)
        else:
            city_sql = await execute_city_info_sql_query(session, user_message, limit=settings.RAG_TOP_K)
            rag_chunks = await _fetch_rag_chunks(
                query=user_message,
                source_types=source_types,
                is_factual=is_factual,
                session=session,
            )

        sql_context = city_sql["raw_data"]
        sql_rows_count = city_sql["row_count"]
        sources.extend(city_sql["sources"])
        if sql_rows_count > 0:
            search_method = "hybrid"
    else:
        rag_chunks = await _fetch_rag_chunks(
            query=user_message,
            source_types=source_types,
            session=session,
        )

    logger.debug(f"[RAG_DEBUG] Retrieval phase finished. SQL rows count: {sql_rows_count}, RAG chunks fetched: {len(rag_chunks)}")
    if intent in {"city_info", "place"}:
        rag_chunks = _filter_city_info_chunks_by_layer(user_message, rag_chunks)
    
    rag_chunks = _apply_source_priority(rag_chunks, query_type)
    rag_chunks = _dedupe_chunks(rag_chunks)
    
    sources = _dedupe_sources(_build_rag_sources(rag_chunks) + sources)

    if not sources:
        if _can_use_model_only_fallback(intent):
            model_only_answer = await _generate_model_only_fallback_answer(
                user_message=user_message,
                conversation_history=conversation_history,
            )
            if model_only_answer:
                styled_answer, persona_profile = await _apply_persona_if_enabled(
                    answer=model_only_answer,
                    intent=intent,
                    user_message=user_message,
                    conversation_history=conversation_history,
                    evidence_state="none",
                    response_policy="model_only_fallback",
                )
                return ChatResponse(
                    answer=styled_answer,
                    intent=intent,
                    sources=[],
                    search_method="llm_only",
                    response_policy="model_only_fallback",
                    confidence=_coerce_confidence(settings.RAG_MODEL_ONLY_BASE_CONFIDENCE, default=0.35),
                    persona_profile=persona_profile,
                    follow_up_suggestions=_suggestions_for_intent(intent),
                )
        styled_answer, persona_profile = await _apply_persona_if_enabled(
            answer=FALLBACK_NO_ANSWER,
            intent=intent,
            user_message=user_message,
            conversation_history=conversation_history,
            evidence_state="none",
            response_policy="no_answer",
        )
        return ChatResponse(
            answer=styled_answer,
            intent=intent,
            sources=[],
            search_method=search_method,
            response_policy="no_answer",
            confidence=0.0,
            persona_profile=persona_profile,
            follow_up_suggestions=_suggestions_for_intent(intent),
        )

    rag_score = _rag_confidence(rag_chunks)
    sql_score = 0.85 if sql_rows_count > 0 else 0.0
    evidence_confidence = max(rag_score, sql_score)
    evidence_state = _evidence_state(
        search_method=search_method,
        sources=sources,
        rag_chunks=rag_chunks,
        sql_rows_count=sql_rows_count,
        confidence=evidence_confidence,
    )

    if evidence_state == "low" and (not rag_chunks or evidence_confidence < 0.15) and sql_rows_count == 0:
        # Sadece hiÃ§ veri yoksa reddet; kÄ±smi veri varsa cevap Ã¼retmeye devam et
        styled_answer, persona_profile = await _apply_persona_if_enabled(
            answer=LOW_EVIDENCE_ANSWER,
            intent=intent,
            user_message=user_message,
            conversation_history=conversation_history,
            evidence_state="low",
            response_policy="no_answer",
        )
        return ChatResponse(
            answer=styled_answer,
            intent=intent,
            sources=[],
            search_method=search_method,
            response_policy="no_answer",
            confidence=evidence_confidence,
            persona_profile=persona_profile,
            follow_up_suggestions=_suggestions_for_intent(intent),
        )

    context_data = _format_context_from_evidence(sql_context, rag_chunks)
    source_catalog = _build_source_catalog(sources)
    if source_catalog:
        context_data = f"{source_catalog}\n\n{context_data}".strip()

    logger.debug(f"[RAG_DEBUG] Calling LLM Generation: _generate_structured_grounded_answer")
    grounded_answer, used_source_ids, llm_confidence = await _generate_structured_grounded_answer(
        user_message=user_message,
        context_data=context_data,
        sources=sources,
        conversation_history=conversation_history,
    )
    logger.debug(f"[RAG_DEBUG] LLM Response - Output length: {len(grounded_answer)}, used_source_ids: {used_source_ids}, llm_confidence: {llm_confidence}")
    selected_sources = _select_sources_by_ids(sources, used_source_ids)

    final_answer = grounded_answer
    if evidence_confidence >= settings.RAG_MIN_EVIDENCE_CONFIDENCE:
        final_answer = _remove_low_data_phrase(final_answer)

    if not final_answer:
        final_answer = "Bu konuda doğrulayabildiğim kaynakları temel alarak kısa bir özet sunabilirim."

    augmentation_text = ""
    augmentation_confidence = 0.0
    used_augmentation = False

    if _should_attempt_augmentation(
        intent=intent,
        sources=selected_sources,
        evidence_state=evidence_state,
        evidence_confidence=evidence_confidence,
        query_type=query_type,
    ) and not _is_strict_grounding_intent(intent):
        (
            augmentation_text,
            _adds_new_information,
            augmentation_confidence,
        ) = await _generate_controlled_augmentation(
            user_message=user_message,
            context_data=context_data,
            grounded_answer=final_answer,
            conversation_history=conversation_history,
        )
        used_augmentation = bool(augmentation_text)
        logger.debug(f"[RAG_DEBUG] Augmentation executed. Used: {used_augmentation}, Adds new info: {_adds_new_information}, confidence: {augmentation_confidence}")
        if used_augmentation:
            final_answer = _merge_grounded_and_augmented(final_answer, augmentation_text)

    final_answer = _normalize_answer_text(final_answer)
    final_answer = _strip_citations(final_answer)

    blended_confidence = (0.90 * evidence_confidence) + (0.10 * llm_confidence)
    if used_augmentation:
        blended_confidence += 0.05 * augmentation_confidence
    if evidence_state != "high":
        blended_confidence = min(blended_confidence, 0.74)
    blended_confidence = _coerce_confidence(blended_confidence, default=0.0)

    response_policy = "grounded_plus_model" if used_augmentation else "grounded_rag"
    if _is_strict_grounding_intent(intent):
        response_policy = "grounded_rag_strict"

    styled_answer, persona_profile = await _apply_persona_if_enabled(
        answer=final_answer,
        intent=intent,
        user_message=user_message,
        conversation_history=conversation_history,
        evidence_state=evidence_state,
        response_policy=response_policy,
    )

    logger.debug(f"[RAG_DEBUG] Final Response - search_method: '{search_method}', response_policy: '{response_policy}', answer length: {len(styled_answer)}, confidence: {blended_confidence:.3f}, fallback used: {used_augmentation or response_policy=='no_answer'}")
    return ChatResponse(
        answer=styled_answer,
        intent=intent,
        sources=selected_sources,
        search_method=search_method,
        response_policy=response_policy,
        confidence=blended_confidence,
        persona_profile=persona_profile,
        follow_up_suggestions=_suggestions_for_intent(intent),
    )

