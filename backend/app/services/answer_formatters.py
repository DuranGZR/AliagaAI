import re
from typing import Any
from app.schemas.chat import SourceReference


def _normalize_answer_text(answer: str) -> str:
    text = answer or ""
    replacements = {
        "beberapa": "birkaÃ§",
        "Beberapa": "BirkaÃ§",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    text = re.sub(r"\s{2,}", " ", text).strip()
    return text



def _strip_citations(text: str) -> str:
    return re.sub(r"\s*\[S\d+\]", "", text or "").strip()



def _remove_low_data_phrase(answer: str) -> str:
    if not answer:
        return answer
    cleaned = re.sub(r"(?i)^\s*not:\s*bu konuda elimde sÄ±nÄ±rlÄ± veri var\.?\s*", "", answer).strip()
    cleaned = re.sub(r"(?i)[^.\n]*sÄ±nÄ±rlÄ± veri[^.\n]*[.\n]?", "", cleaned).strip()
    return cleaned



def _coerce_confidence(value: Any, default: float = 0.0) -> float:
    try:
        conf = float(value)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, conf))




def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "evet"}
    if isinstance(value, (int, float)):
        return value != 0
    return False



def _dedupe_sources(sources: list[SourceReference]) -> list[SourceReference]:
    seen = set()
    unique = []
    for source in sources:
        key = (source.type, source.title, source.url, source.date)
        if key in seen:
            continue
        seen.add(key)
        unique.append(source)
    return unique



def _normalize_used_source_ids(raw_ids: Any, source_count: int) -> list[int]:
    if source_count <= 0:
        return []
    if not isinstance(raw_ids, list):
        return []

    clean: list[int] = []
    for value in raw_ids:
        try:
            idx = int(value)
        except (TypeError, ValueError):
            continue
        if 1 <= idx <= source_count and idx not in clean:
            clean.append(idx)
    return clean



def _suggestions_for_intent(intent: str) -> list[str]:
    catalog = {
        "greeting": [
            "AliaÄŸa'da gezilecek yerler neler?",
            "AliaÄŸa'ya nasÄ±l gelinir?",
            "AliaÄŸa mahalleleri hakkÄ±nda kÄ±sa bilgi ver",
        ],
        "place": [
            "Aile iÃ§in uygun gezi rotasÄ± Ã¶ner",
            "Deniz kenarÄ± mekan Ã¶ner",
            "Tarihi yerleri sÄ±ralar mÄ±sÄ±n?",
        ],
        "city_info": [
            "Ä°ZBAN ile AliaÄŸa'ya ulaÅŸÄ±mÄ± anlat",
            "Karayolu ile geliÅŸ seÃ§enekleri neler?",
            "AliaÄŸa'nÄ±n mahallelerini Ã¶zetle",
        ],
        "news": [
            "Son belediye haberlerini Ã¶zetle",
            "Bu haftaki Ã¶nemli geliÅŸmeler neler?",
            "KaynaÄŸÄ±yla birlikte kÄ±sa haber Ã¶zeti ver",
        ],
        "event": [
            "Bu ayki etkinlikleri listele",
            "Aile etkinlikleri var mÄ±?",
            "Etkinlik yer ve tarihlerini yaz",
        ],
    }
    return catalog.get(
        intent,
        [
            "Bunu biraz daha detaylandÄ±rÄ±r mÄ±sÄ±n?",
            "Mahalle bazÄ±nda anlatÄ±r mÄ±sÄ±n?",
            "KaynaklarÄ±yla kÄ±sa Ã¶zet geÃ§er misin?",
        ],
    )


