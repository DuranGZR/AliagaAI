"""
AliağaAI — Metin işleme ve genel yardımcı fonksiyonlar.

Tüm servisler tarafından kullanılan, bağımsız ve saf (pure) yardımcılar.
"""
from __future__ import annotations

import re
from typing import Any

from app.schemas.chat import SourceReference


# ── Metin normalizasyon ──────────────────────────────────────────────

_CITATION_RE = re.compile(r"\s*\[S\d+\]")
_WHITESPACE_RE = re.compile(r"[ \t]{2,}")
_MULTI_NEWLINE_RE = re.compile(r"\n{3,}")

# Groq bazen Indonezce/İngilizce kelime sızdırır; sessizce Türkçeye çeviriyoruz.
_LANGUAGE_LEAK_MAP = {
    "beberapa": "birkaç",
    "Beberapa": "Birkaç",
}


def normalize_answer(text: str) -> str:
    """Yanıt metnini temizle: gereksiz boşluklar, satır karmaşası ve dil sızıntıları."""
    result = text or ""
    for src, dst in _LANGUAGE_LEAK_MAP.items():
        result = result.replace(src, dst)
    result = result.replace("\r\n", "\n").replace("\r", "\n")
    result = _WHITESPACE_RE.sub(" ", result)
    result = re.sub(r"[ \t]*\n[ \t]*", "\n", result)
    result = _MULTI_NEWLINE_RE.sub("\n\n", result).strip()
    return result


def strip_citations(text: str) -> str:
    """Yanıt metninden [S1], [S2] gibi kaynak etiketlerini sil."""
    return _CITATION_RE.sub("", text or "").strip()


# ── Tip dönüşümleri ─────────────────────────────────────────────────

def coerce_confidence(value: Any, default: float = 0.0) -> float:
    """Herhangi bir değeri 0.0-1.0 arasında float'a dönüştür."""
    try:
        conf = float(value)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, conf))


# ── Kaynak yardımcıları ─────────────────────────────────────────────

def dedupe_sources(sources: list[SourceReference]) -> list[SourceReference]:
    """Tekrarlayan kaynak referanslarını kaldır."""
    seen: set[tuple] = set()
    unique: list[SourceReference] = []
    for source in sources:
        key = (source.type, source.title, source.url, source.date)
        if key not in seen:
            seen.add(key)
            unique.append(source)
    return unique


# ── Takip önerileri ──────────────────────────────────────────────────

_SUGGESTION_CATALOG: dict[str, list[str]] = {
    "greeting": [
        "Aliağa'da gezilecek yerler neler?",
        "Aliağa'ya nasıl gelinir?",
        "Aliağa mahalleleri hakkında kısa bilgi ver",
    ],
    "place": [
        "Aile için uygun gezi rotası öner",
        "Deniz kenarı mekan öner",
        "Tarihi yerleri sıralar mısın?",
    ],
    "city_info": [
        "İZBAN ile Aliağa'ya ulaşımı anlat",
        "Karayolu ile geliş seçenekleri neler?",
        "Aliağa'nın mahallelerini özetle",
    ],
    "news": [
        "Son belediye haberlerini özetle",
        "Bu haftaki önemli gelişmeler neler?",
        "Kaynağıyla birlikte kısa haber özeti ver",
    ],
    "event": [
        "Bu ayki etkinlikleri listele",
        "Aile etkinlikleri var mı?",
        "Etkinlik yer ve tarihlerini yaz",
    ],
    "transport": [
        "İzmir yönüne ilk ve son İZBAN saatleri neler?",
        "Aliağa-Midilli feribot sefer saatlerini listele",
        "İZBAN Aliağa istasyonundan hangi yöne gidilir?",
    ],
    "taxi": [
        "Tüm taksi duraklarının telefon numaralarını listele",
        "Hangi taksi durakları 24 saat hizmet veriyor?",
        "Merkez taksi durağı nerede?",
    ],
    "postal_code": [
        "Kültür Mahallesi posta kodu nedir?",
        "Yenişakran posta kodunu yazar mısın?",
        "Aliağa mahallelerinin posta kodları listesi var mı?",
    ],
}

_DEFAULT_SUGGESTIONS = [
    "Bunu biraz daha detaylandırır mısın?",
    "Mahalle bazında anlatır mısın?",
    "Kaynaklarıyla kısa özet geçer misin?",
]


def suggestions_for_intent(intent: str) -> list[str]:
    """Intent'e göre takip sorusu önerileri döner."""
    return _SUGGESTION_CATALOG.get(intent, _DEFAULT_SUGGESTIONS)
