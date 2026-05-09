"""
AliağaAI - Ortak chunking yardımcıları.

Farklı kaynaklardan gelen metinleri tutarlı bir şekilde parçalamak için
tek bir merkezden yönetilir.
"""
from __future__ import annotations

import hashlib
import re
from typing import Iterable

from app.core.config import settings


_SENTENCE_SPLIT_RE = re.compile(r"(?<=[\.\?\!])\s+")
_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(text: str | None) -> str:
    """Metni tek satırlı ve tutarlı boşluk yapısına indirger."""
    if not text:
        return ""
    return _WHITESPACE_RE.sub(" ", text).strip()


def build_text(parts: Iterable[str | None]) -> str:
    """Parça metinleri birleştirir ve normalize eder."""
    return normalize_text(" ".join(p for p in parts if p))


def content_hash(text: str) -> str:
    """Metin içeriğinin stable hash değerini üretir."""
    normalized = normalize_text(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _split_sentences(text: str) -> list[str]:
    if not text:
        return []
    raw = _SENTENCE_SPLIT_RE.split(text)
    return [normalize_text(s) for s in raw if normalize_text(s)]


def chunk_text(
    text: str,
    chunk_size: int | None = None,
    overlap: int | None = None,
    min_length: int | None = None,
) -> list[str]:
    """
    Metni cümle bazlı toplar, hedef uzunluğu aşınca yeni chunk açar.
    """
    chunk_size = chunk_size or settings.CHUNK_SIZE
    overlap = overlap if overlap is not None else settings.CHUNK_OVERLAP
    min_length = min_length or settings.CHUNK_MIN_LENGTH

    normalized = normalize_text(text)
    if not normalized:
        return []
    if len(normalized) <= chunk_size:
        return [normalized] if len(normalized) >= min_length else []

    sentences = _split_sentences(normalized)
    if not sentences:
        return [normalized[i : i + chunk_size] for i in range(0, len(normalized), chunk_size)]

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for sentence in sentences:
        sentence_len = len(sentence)
        separator_len = 1 if current else 0
        if current and current_len + separator_len + sentence_len > chunk_size:
            chunk = normalize_text(" ".join(current))
            if len(chunk) >= min_length:
                chunks.append(chunk)

            if overlap > 0:
                overlap_text = chunk[-overlap:]
                current = [normalize_text(overlap_text)] if overlap_text else []
                current_len = len(current[0]) if current else 0
            else:
                current = []
                current_len = 0

        current.append(sentence)
        current_len += sentence_len + (1 if len(current) > 1 else 0)

    tail = normalize_text(" ".join(current))
    if len(tail) >= min_length:
        chunks.append(tail)

    return chunks
