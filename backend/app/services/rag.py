"""
AliagaAI - RAG Retrieval service.

Multi-stage retrieval:
1) Vector similarity (pgvector)
2) Lexical retrieval (PostgreSQL full-text)
3) Fusion + rerank
"""
from __future__ import annotations

import asyncio
import re
import time
import unicodedata
from collections import defaultdict

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.embedding import generate_query_embedding

try:
    from app.models.city import DocumentChunk

    HAS_VECTOR = True
except ImportError:
    HAS_VECTOR = False


_TOKEN_RE = re.compile(r"[a-zA-Z0-9çğıöşüÇĞİÖŞÜ]{2,}", re.UNICODE)
_LAST_ERROR_SIGNATURE = ""
_LAST_ERROR_AT = 0.0
_STOPWORDS = {
    "ve", "ile", "icin", "için", "bu", "su", "şu", "bir", "mi", "mu", "mı", "mü",
    "hakkinda", "hakkında", "bilir", "misin", "nedir", "nerede", "bana", "beni",
    "nasil", "nasıl", "anlat", "soyle", "söyle", "ver", "eder", "olan", "olan",
    "gibi", "daha", "cok", "çok", "var", "yok", "kadar", "sonra", "once", "önce",
    "ama", "fakat", "veya", "ya", "da", "de", "den", "dan", "dir", "dır",
    "lar", "ler", "nin", "nın", "nun", "nün", "mısın", "musun",
    "hangi", "kac", "kaç", "lütfen", "lutfen",
}
_SYNONYM_MAP = {
    "kamu": ["devlet", "resmi", "belediye"],
    "resmi": ["kamu", "devlet"],
    "egitim": ["okul", "egitim", "lise", "universite"],
    "eğitim": ["okul", "egitim", "lise", "universite"],
    "saglik": ["hastane", "saglik", "doktor", "eczane"],
    "sağlık": ["hastane", "saglik", "doktor", "eczane"],
    "kultur": ["sanat", "kultur", "muze", "tiyatro"],
    "kültür": ["sanat", "kultur", "muze", "tiyatro"],
    "kutuphane": ["kutuphane", "kitaplik", "kitap"],
    "kütüphane": ["kutuphane", "kitaplik", "kitap"],
    "ulasim": ["izban", "otobus", "vapur", "feribot", "toplu tasima"],
    "ulaşım": ["izban", "otobus", "vapur", "feribot", "toplu tasima"],
    "izban": ["tren", "banliyo", "istasyon", "ulasim", "metro"],
    "tarih": ["antik", "kent", "arkeoloji", "gecmis", "eski", "tarihi"],
    "gezi": ["tur", "turistik", "gezilecek", "mekan", "yer"],
    "yemek": ["restoran", "lokanta", "kafe", "gastronomi", "mutfak"],
    "spor": ["havuz", "fitness", "stadyum", "salon"],
    "kargo": ["ptt", "mng", "yurtici", "aras", "surat"],
    "sahil": ["plaj", "deniz", "kumsal", "yuzme"],
    "mahalle": ["semt", "bolge", "ilce", "mevki"],
    "nufus": ["kisi", "insan", "demografi", "nüfus"],
}
_TAXONOMY_HINTS = {
    "kategori", "tur", "turu", "türü", "öner", "oner",
    "listele", "sirala", "sırala", "hangileri", "neler",
}


def _tokenize(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN_RE.findall(text or "")}


def _strip_diacritics(text: str) -> str:
    norm = unicodedata.normalize("NFKD", text or "")
    return "".join(ch for ch in norm if not unicodedata.combining(ch))


def _looks_taxonomy_query(query: str) -> bool:
    tokens = _tokenize(query)
    return any(token in _TAXONOMY_HINTS for token in tokens)


def _build_query_variants(query: str, is_factual: bool = False) -> list[str]:
    base = (query or "").strip()
    if not base:
        return []

    if not settings.RAG_QUERY_EXPANSION_ENABLED:
        return [base]

    variants: list[str] = [base]
    tokens = [t for t in _TOKEN_RE.findall(base.lower()) if t]
    if tokens:
        compact = " ".join(tokens)
        if compact and compact not in variants:
            variants.append(compact)

        no_stop = [t for t in tokens if t not in _STOPWORDS]
        if no_stop:
            no_stop_q = " ".join(no_stop)
            if no_stop_q and no_stop_q not in variants:
                variants.append(no_stop_q)

            synonym_tokens: list[str] = []
            for token in no_stop:
                synonym_tokens.extend(_SYNONYM_MAP.get(token, []))
            if synonym_tokens:
                expanded = " ".join(no_stop + synonym_tokens[:4])
                if expanded and expanded not in variants:
                    variants.append(expanded)

    ascii_query = _strip_diacritics(base.lower())
    if ascii_query and ascii_query not in variants:
        variants.append(ascii_query)

    max_variants = 2 if is_factual else max(1, settings.RAG_MAX_QUERY_VARIANTS)
    return variants[:max_variants]


def _adaptive_min_similarity(query: str, minimum: float) -> float:
    token_count = len(_tokenize(query))
    if token_count <= 3:
        return min(minimum, settings.RAG_SHORT_QUERY_MIN_SIMILARITY)
    if token_count <= 6:
        return min(minimum, settings.RAG_MEDIUM_QUERY_MIN_SIMILARITY)
    return minimum


def _overlap_score(query: str, text: str) -> float:
    q = _tokenize(query)
    if not q:
        return 0.0
    t = _tokenize(text)
    if not t:
        return 0.0
    return len(q.intersection(t)) / len(q)


def _normalize_scores(values: list[float]) -> list[float]:
    if not values:
        return []
    vmax = max(values)
    if vmax <= 0:
        return [0.0 for _ in values]
    return [v / vmax for v in values]


async def _fetch_vector_candidates(
    session: AsyncSession,
    query: str,
    source_types: list[str] | None,
) -> list[tuple[object, float]]:
    try:
        query_vector = await asyncio.wait_for(
            generate_query_embedding(query),
            timeout=settings.RAG_QUERY_EMBED_TIMEOUT_SEC,
        )
    except TimeoutError:
        logger.warning("Query embedding zaman asimina ugradi, bu turde vector adimi atlanacak.")
        return []
    except Exception as exc:
        logger.warning(f"Query embedding uretilemedi, vector adimi atlanacak: {exc}")
        return []
    distance_col = DocumentChunk.embedding.cosine_distance(query_vector).label("distance")
    stmt = select(DocumentChunk, distance_col).order_by(distance_col).limit(settings.RAG_VECTOR_CANDIDATES)
    if source_types:
        stmt = stmt.where(DocumentChunk.source_type.in_(source_types))
    result = await session.execute(stmt)
    return [(doc, 1.0 - distance) for doc, distance in result]


async def _fetch_lexical_candidates(
    session: AsyncSession,
    query: str,
    source_types: list[str] | None,
) -> list[tuple[object, float]]:
    ts_vector = func.to_tsvector("simple", DocumentChunk.content)
    ts_query = func.plainto_tsquery("simple", query)
    rank_col = func.ts_rank_cd(ts_vector, ts_query).label("lexical_rank")

    stmt = (
        select(DocumentChunk, rank_col)
        .where(ts_vector.op("@@")(ts_query))
        .order_by(rank_col.desc())
        .limit(settings.RAG_LEXICAL_CANDIDATES)
    )
    if source_types:
        stmt = stmt.where(DocumentChunk.source_type.in_(source_types))

    result = await session.execute(stmt)
    return [(doc, rank) for doc, rank in result]


def _rerank_candidates(query: str, candidates: list[dict]) -> list[dict]:
    if not settings.RAG_RERANK_ENABLED:
        for c in candidates:
            c["rerank_score"] = c["fusion_score"]
        return candidates

    max_candidates = max(1, settings.RAG_RERANK_TOP_N)
    head = candidates[:max_candidates]
    tail = candidates[max_candidates:]

    for c in head:
        overlap = _overlap_score(query, c["content"])
        c["overlap_score"] = overlap
        c["rerank_score"] = (0.7 * c["fusion_score"]) + (0.3 * overlap)

    head.sort(key=lambda x: x["rerank_score"], reverse=True)
    for c in tail:
        c["overlap_score"] = _overlap_score(query, c["content"])
        c["rerank_score"] = c["fusion_score"]

    return head + tail


async def search_similar_chunks(
    session: AsyncSession,
    query: str,
    limit: int | None = None,
    min_similarity: float | None = None,
    source_types: list[str] | None = None,
    is_factual: bool = False,
) -> list[dict]:
    """
    Returns the most relevant chunks for query.

    Returned item keys:
    - similarity: vector similarity
    - lexical_score: normalized lexical score
    - fusion_score: weighted fusion score
    - rerank_score: final ranking score
    """
    if not HAS_VECTOR:
        logger.warning("RAG aramasi yapilamiyor: pgvector destekli DocumentChunk yok.")
        return []

    k = limit or settings.RAG_TOP_K
    base_min_similarity = min_similarity if min_similarity is not None else settings.RAG_MIN_SIMILARITY
    effective_min_similarity = _adaptive_min_similarity(query, base_min_similarity)
    query_variants = _build_query_variants(query, is_factual=is_factual)
    logger.debug(f"[RAG_DEBUG] search_similar_chunks - query: '{query}', limit: {k}, variants_count: {len(query_variants)}")

    try:
        vector_by_id: dict[str, tuple[object, float]] = {}
        lexical_rows: list[tuple[object, float]] = []

        tasks = []
        for variant in query_variants:
            tasks.append(_fetch_vector_candidates(session, variant, source_types))
            tasks.append(_fetch_lexical_candidates(session, variant, source_types))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i in range(0, len(results), 2):
            variant_vector_rows = results[i]
            lexical_candidates = results[i+1]
            
            if not isinstance(variant_vector_rows, Exception):
                for doc, similarity in variant_vector_rows:
                    doc_id = str(doc.id)
                    prev = vector_by_id.get(doc_id)
                    if prev is None or similarity > prev[1]:
                        vector_by_id[doc_id] = (doc, float(similarity))
                        
            if not isinstance(lexical_candidates, Exception):
                lexical_rows.extend(lexical_candidates)

        vector_rows = list(vector_by_id.values())

        if not vector_rows and not lexical_rows:
            logger.info(f"RAG aramasi: '{query}' icin sonuc bulunamadi.")
            return []

        candidate_map: dict[str, dict] = {}
        lexical_scores_by_id: defaultdict[str, float] = defaultdict(float)

        for doc, similarity in vector_rows:
            candidate_map[str(doc.id)] = {
                "id": str(doc.id),
                "source_type": doc.source_type,
                "source_id": doc.source_id,
                "content": doc.content,
                "similarity": float(similarity),
                "metadata": doc.metadata_json or {},
            }

        for doc, lexical_rank in lexical_rows:
            doc_id = str(doc.id)
            lexical_scores_by_id[doc_id] = max(lexical_scores_by_id[doc_id], float(lexical_rank or 0.0))
            if doc_id not in candidate_map:
                candidate_map[doc_id] = {
                    "id": doc_id,
                    "source_type": doc.source_type,
                    "source_id": doc.source_id,
                    "content": doc.content,
                    "similarity": 0.0,
                    "metadata": doc.metadata_json or {},
                }

        lexical_ids = list(lexical_scores_by_id.keys())
        normalized_lex = _normalize_scores([lexical_scores_by_id[i] for i in lexical_ids])
        lexical_lookup = {doc_id: normalized_lex[idx] for idx, doc_id in enumerate(lexical_ids)}

        filtered: list[dict] = []
        taxonomy_query = _looks_taxonomy_query(query)
        lexical_rescue_enabled = bool(source_types) or taxonomy_query
        near_similarity = max(effective_min_similarity - 0.10, 0.0)

        for candidate in candidate_map.values():
            lexical_score = lexical_lookup.get(candidate["id"], 0.0)
            similarity = candidate["similarity"]
            fusion_score = (
                (settings.RAG_VECTOR_WEIGHT * similarity)
                + (settings.RAG_LEXICAL_WEIGHT * lexical_score)
            )
            candidate["lexical_score"] = lexical_score
            candidate["fusion_score"] = fusion_score

            lexical_rescue = lexical_rescue_enabled and lexical_score >= settings.RAG_LEXICAL_RESCUE_SCORE
            if (
                similarity >= effective_min_similarity
                or (similarity >= near_similarity and lexical_score >= 0.3)
                or lexical_rescue
                or lexical_score > 0.0  # Herhangi bir lexical eşleşme varsa al
            ):
                filtered.append(candidate)

        # Eğer hala filtrelenen yoksa, en iyi fusion skorlu adayları al
        if not filtered and candidate_map:
            filtered = sorted(
                candidate_map.values(),
                key=lambda x: x["fusion_score"],
                reverse=True,
            )[: max(k, 5)]

        filtered.sort(key=lambda x: x["fusion_score"], reverse=True)
        reranked = _rerank_candidates(query, filtered)
        reranked.sort(key=lambda x: x["rerank_score"], reverse=True)

        final = reranked[:k]
        logger.info(
            f"RAG aramasi: '{query}' source_filter={source_types or 'ALL'} -> {len(final)} sonuc "
            f"(vector={len(vector_rows)}, lexical={len(lexical_rows)}, variants={len(query_variants)}, "
            f"min_sim={effective_min_similarity:.2f})"
        )
        return final
    except Exception as exc:
        global _LAST_ERROR_SIGNATURE, _LAST_ERROR_AT
        signature = str(exc)
        now = time.time()
        if signature != _LAST_ERROR_SIGNATURE or (now - _LAST_ERROR_AT) > 30:
            logger.error(f"RAG arama hatasi: {exc}")
            _LAST_ERROR_SIGNATURE = signature
            _LAST_ERROR_AT = now
        else:
            logger.debug(f"RAG arama hatasi (tekrarlayan): {signature}")
        return []
