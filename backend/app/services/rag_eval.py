"""
AliağaAI - RAG değerlendirme servisi.

Metrikler:
- Recall@k
- MRR
- Citation Precision
- No-Answer Accuracy
- Faithfulness Proxy
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.city import UtilityOutage
from app.models.content import Announcement, Event, JobListing, News, Project
from app.models.places import Institution, Place
from app.services.query_router import process_chat_query
from app.services.rag import search_similar_chunks


DEFAULT_EVAL_SET_PATH = Path("evaluation/rag_eval_set.json")
REPORTS_DIR = Path("../logs/rag_eval_reports")
_CITATION_RE = re.compile(r"\[S(\d+)\]")


def load_eval_set(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_eval_set(path: Path, items: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def _append_item(items: list[dict[str, Any]], item: dict[str, Any], seen: set[str]) -> None:
    q = item["question"].strip().lower()
    if not q or q in seen:
        return
    seen.add(q)
    items.append(item)


async def generate_bootstrap_eval_set(
    session: AsyncSession,
    target_size: int = 200,
    output_path: Path | None = None,
) -> list[dict[str, Any]]:
    """
    Veritabanındaki gerçek içeriklerden otomatik bir eval set üretir.
    """
    items: list[dict[str, Any]] = []
    seen: set[str] = set()

    places = (await session.execute(select(Place).where(Place.is_active.is_(True)).limit(50))).scalars().all()
    for p in places:
        _append_item(items, {"question": f"{p.name} hakkında bilgi verir misin?", "expected_source_types": ["place"], "expect_no_answer": False}, seen)
        _append_item(items, {"question": f"{p.category} kategorisinde {p.name} gibi bir yer önerir misin?", "expected_source_types": ["place"], "expect_no_answer": False}, seen)

    institutions = (await session.execute(select(Institution).where(Institution.is_active.is_(True)).limit(40))).scalars().all()
    for i in institutions:
        _append_item(items, {"question": f"{i.name} nerede?", "expected_source_types": ["institution"], "expect_no_answer": False}, seen)
        _append_item(items, {"question": f"{i.category} kategorisinde kurum önerir misin?", "expected_source_types": ["institution"], "expect_no_answer": False}, seen)

    news = (await session.execute(select(News).order_by(News.published_at.desc()).limit(50))).scalars().all()
    for n in news:
        if n.title:
            _append_item(items, {"question": f"'{n.title}' haberiyle ilgili özet verir misin?", "expected_source_types": ["news"], "expect_no_answer": False}, seen)

    events = (await session.execute(select(Event).order_by(Event.event_date.desc()).limit(50))).scalars().all()
    for e in events:
        _append_item(items, {"question": f"{e.title} etkinliği ne zaman?", "expected_source_types": ["event"], "expect_no_answer": False}, seen)

    announcements = (await session.execute(select(Announcement).order_by(Announcement.published_at.desc()).limit(40))).scalars().all()
    for a in announcements:
        _append_item(items, {"question": f"{a.title} duyurusu hakkında bilgi verir misin?", "expected_source_types": ["announcement"], "expect_no_answer": False}, seen)

    projects = (await session.execute(select(Project).limit(40))).scalars().all()
    for p in projects:
        _append_item(items, {"question": f"{p.title} projesinin durumu nedir?", "expected_source_types": ["project"], "expect_no_answer": False}, seen)

    jobs = (await session.execute(select(JobListing).where(JobListing.is_active.is_(True)).limit(40))).scalars().all()
    for j in jobs:
        _append_item(items, {"question": f"{j.title} pozisyonu halen açık mı?", "expected_source_types": ["job"], "expect_no_answer": False}, seen)

    outages = (await session.execute(select(UtilityOutage).limit(30))).scalars().all()
    for o in outages:
        locality = o.neighborhood or o.district or "Aliağa"
        _append_item(items, {"question": f"{locality} bölgesinde {o.type} kesintisi var mı?", "expected_source_types": ["outage"], "expect_no_answer": False}, seen)

    # No-answer testleri
    no_answer_questions = [
        "Aliağa'da Mars'a uçuş bileti ne kadar?",
        "Aliağa belediyesi bugün uzay asansörü açtı mı?",
        "Aliağa'da Hogwarts kampüsü var mı?",
        "Yeni çıkan iPhone modelinin teknik özellikleri nedir?",
        "Dünya kupasını kim kazandı?",
        "Aliağa'da ejderha turu var mı?",
        "Kripto para yatırım tavsiyesi verir misin?",
        "Aliağa'da 1800 yılındaki canlı trafik durumu nedir?",
        "Uzaylı istilası için belediye planı var mı?",
        "Yarın Ay'da hava nasıl olacak?",
    ]
    for q in no_answer_questions:
        _append_item(items, {"question": q, "expected_source_types": [], "expect_no_answer": True}, seen)

    # Yetersizse basit varyasyonlarla çoğalt
    base_items = list(items)
    idx = 0
    while len(items) < target_size and base_items:
        item = base_items[idx % len(base_items)]
        variant = dict(item)
        variant["question"] = f"{item['question']} (detaylı)"
        _append_item(items, variant, seen)
        idx += 1

    if output_path:
        save_eval_set(output_path, items)
    logger.info(f"Bootstrap eval set hazırlandı: {len(items)} soru")
    return items


def _is_no_answer(text: str) -> bool:
    lowered = text.lower()
    patterns = [
        "doğrulanmış bir veri bulamıyorum",
        "şu an bu bilgiye",
        "net erişemiyorum",
        "sınırlı veri",
    ]
    return any(p in lowered for p in patterns)


async def evaluate_rag(
    session: AsyncSession,
    eval_items: list[dict[str, Any]],
    k: int | None = None,
    run_generation: bool = True,
) -> dict[str, Any]:
    if not eval_items:
        return {
            "summary": {
                "total": 0,
                "retrieval_count": 0,
                "recall_at_k": 0.0,
                "mrr": 0.0,
                "citation_precision": 0.0,
                "no_answer_accuracy": 0.0,
                "faithfulness_proxy": 0.0,
            },
            "items": [],
        }

    k = k or settings.RAG_TOP_K

    retrieval_total = 0
    recall_hits = 0
    mrr_total = 0.0

    citation_total = 0
    citation_valid = 0
    no_answer_total = 0
    no_answer_correct = 0
    faithfulness_total = 0
    faithfulness_score = 0

    item_reports: list[dict[str, Any]] = []

    for item in eval_items:
        question = item["question"]
        expected_types = set(item.get("expected_source_types", []))
        expect_no_answer = bool(item.get("expect_no_answer", False))

        retrieved = await search_similar_chunks(session, question, limit=k, min_similarity=settings.RAG_MIN_SIMILARITY)
        retrieval_rank = None
        if expected_types:
            retrieval_total += 1
            for idx, chunk in enumerate(retrieved, start=1):
                if chunk.get("source_type") in expected_types:
                    retrieval_rank = idx
                    break
            if retrieval_rank is not None:
                recall_hits += 1
                mrr_total += 1.0 / retrieval_rank

        answer_text = ""
        sources_count = 0
        citations: list[int] = []
        valid_citations: list[int] = []
        search_method = "n/a"

        if run_generation:
            response = await process_chat_query(session, question)
            answer_text = response.answer or ""
            sources_count = len(response.sources)
            search_method = response.search_method
            citations = [int(m.group(1)) for m in _CITATION_RE.finditer(answer_text)]
            valid_citations = [c for c in citations if 1 <= c <= len(response.sources)]

            if expect_no_answer:
                no_answer_total += 1
                if _is_no_answer(answer_text):
                    no_answer_correct += 1
            else:
                if response.sources:
                    citation_total += max(1, len(citations))
                    citation_valid += len(valid_citations)

            faithfulness_total += 1
            if expect_no_answer:
                faithfulness_score += 1 if _is_no_answer(answer_text) else 0
            else:
                if response.sources and citations:
                    faithfulness_score += 1 if len(valid_citations) == len(citations) else 0
                elif response.sources and not citations:
                    faithfulness_score += 0
                else:
                    faithfulness_score += 1 if _is_no_answer(answer_text) else 0

        item_reports.append(
            {
                "question": question,
                "expected_source_types": sorted(list(expected_types)),
                "expect_no_answer": expect_no_answer,
                "retrieval_rank": retrieval_rank,
                "retrieved_source_types": [c.get("source_type") for c in retrieved],
                "answer": answer_text,
                "sources_count": sources_count,
                "citations_found": citations,
                "valid_citations": valid_citations,
                "search_method": search_method,
            }
        )

    summary = {
        "total": len(eval_items),
        "retrieval_count": retrieval_total,
        "recall_at_k": (recall_hits / retrieval_total) if retrieval_total else 0.0,
        "mrr": (mrr_total / retrieval_total) if retrieval_total else 0.0,
        "citation_precision": (citation_valid / citation_total) if run_generation and citation_total else 0.0,
        "no_answer_accuracy": (no_answer_correct / no_answer_total) if run_generation and no_answer_total else 0.0,
        "faithfulness_proxy": (faithfulness_score / faithfulness_total) if run_generation and faithfulness_total else 0.0,
        "generation_metrics_enabled": run_generation,
    }
    return {"summary": summary, "items": item_reports}


def write_eval_report(report: dict[str, Any], output_dir: Path | None = None) -> Path:
    out_dir = output_dir or REPORTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = out_dir / f"rag_eval_report_{now}.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return report_path
