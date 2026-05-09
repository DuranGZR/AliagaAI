"""
AliağaAI - Yapılandırılmış içerikleri pgvector document_chunks tablosuna indeksler.

Bu modül RAG veri kalitesini merkezi olarak yönetir:
- Ortak chunking kuralları
- Hash tabanlı değişiklik takibi
- source_type bazlı güvenli yeniden indeksleme
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Callable

from loguru import logger
from sqlalchemy import delete, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.city import CityKnowledge, DocumentChunk, FerrySchedule, IzbanSchedule, UtilityOutage
from app.models.content import Announcement, Event, JobListing, News, Obituary, Project
from app.models.knowledge_layers import (
    DistrictStat,
    MunicipalService,
    PoiCatalog,
    TransportDeparture,
    TransportRoute,
    TransportStop,
)
from app.models.places import Institution, Place
from app.services.chunking import build_text, chunk_text, content_hash
from app.services.embedding import generate_embedding


if DocumentChunk is None:
    HAS_VECTOR = False
else:
    HAS_VECTOR = True


def _to_iso(value: Any) -> str | None:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return None


@dataclass(frozen=True)
class SourceIndexerConfig:
    source_type: str
    model: Any
    id_attr: str
    text_builder: Callable[[Any], str]
    metadata_builder: Callable[[Any], dict[str, Any]]
    is_active: Callable[[Any], bool] = lambda _: True
    min_chunk_length: int | None = None


def _news_text(row: News) -> str:
    return build_text([row.title, row.content, row.category])


def _event_text(row: Event) -> str:
    return build_text([row.title, row.description, row.location, row.event_time])


def _announcement_text(row: Announcement) -> str:
    return build_text([row.title, row.content, row.type])


def _project_text(row: Project) -> str:
    return build_text([row.title, row.description, row.status, row.category])


def _job_text(row: JobListing) -> str:
    return build_text([row.title, row.company, row.location, row.description])


def _place_text(row: Place) -> str:
    tags = ", ".join(row.tags) if row.tags else None
    return build_text([row.name, row.category, row.subcategory, row.description, tags, row.address, row.phone, row.website, row.working_hours])


def _institution_text(row: Institution) -> str:
    return build_text([row.name, row.category, row.subcategory, row.description, row.address, row.phone, row.website, row.working_hours])


def _outage_text(row: UtilityOutage) -> str:
    return build_text([row.type, row.district, row.neighborhood, row.description, row.source])


def _obituary_text(row: Obituary) -> str:
    return build_text([row.name, row.details, row.funeral_location, row.neighborhood, row.source])


def _city_knowledge_text(row: CityKnowledge) -> str:
    tags = ", ".join(row.tags) if row.tags else None
    return build_text([row.layer, row.title, row.neighborhood, row.summary, tags])


def _transport_route_text(row: TransportRoute) -> str:
    return build_text([row.mode, row.hat_no, row.guzergah])


def _transport_stop_text(row: TransportStop) -> str:
    return build_text([row.mode, row.stop_id, row.ad, row.ilce, row.mahalle])


def _transport_departure_text(row: TransportDeparture) -> str:
    return build_text(
        [
            row.stop_id,
            row.day_type,
            str(row.zaman) if row.zaman else None,
            "realtime" if row.realtime_flag else "scheduled",
        ]
    )


def _poi_catalog_text(row: PoiCatalog) -> str:
    return build_text([row.kategori, row.ad, row.aciklama, row.mahalle])


def _municipal_service_text(row: MunicipalService) -> str:
    return build_text([row.hizmet_tipi, row.birim, row.calisma_saatleri, row.iletisim])


def _district_stat_text(row: DistrictStat) -> str:
    return build_text(
        [
            row.district,
            row.neighborhood,
            str(row.yil) if row.yil is not None else None,
            row.metrik_adi,
            str(row.metrik_degeri) if row.metrik_degeri is not None else None,
            row.birim,
        ]
    )


def _izban_schedule_text(row: IzbanSchedule) -> str:
    departure = str(row.departure_time) if row.departure_time else ""
    return build_text([
        "İZBAN", row.line, row.station, row.direction,
        f"kalkış {departure}" if departure else None,
        row.day_type,
        "İZBAN banliyö tren hattı Aliağa İzmir toplu taşıma ulaşım",
    ])


def _ferry_schedule_text(row: FerrySchedule) -> str:
    departure = str(row.departure_time) if row.departure_time else ""
    return build_text([
        "Feribot", row.route, row.company,
        f"kalkış {departure}" if departure else None,
        row.departure_port, row.arrival_port,
        row.day_type, row.season,
        f"süre {row.duration}" if row.duration else None,
        row.price_info,
        "feribot vapur deniz ulaşımı Aliağa Midilli",
    ])


SOURCE_CONFIGS: dict[str, SourceIndexerConfig] = {
    "news": SourceIndexerConfig(
        source_type="news",
        model=News,
        id_attr="id",
        text_builder=_news_text,
        metadata_builder=lambda row: {
            "title": row.title,
            "url": row.source_url,
            "date": _to_iso(row.published_at),
            "category": row.category,
        },
        min_chunk_length=40,
    ),
    "event": SourceIndexerConfig(
        source_type="event",
        model=Event,
        id_attr="id",
        text_builder=_event_text,
        metadata_builder=lambda row: {
            "title": row.title,
            "url": row.source_url,
            "date": _to_iso(row.event_date),
            "category": row.category,
            "location": row.location,
        },
        is_active=lambda row: row.event_date is None or (
            isinstance(row.event_date, datetime) and row.event_date.date() >= datetime.now().date() - timedelta(days=3)
        ) or (
            isinstance(row.event_date, date) and not isinstance(row.event_date, datetime) and row.event_date >= datetime.now().date() - timedelta(days=3)
        ),
        min_chunk_length=40,
    ),
    "announcement": SourceIndexerConfig(
        source_type="announcement",
        model=Announcement,
        id_attr="id",
        text_builder=_announcement_text,
        metadata_builder=lambda row: {
            "title": row.title,
            "url": row.source_url,
            "date": _to_iso(row.published_at),
            "announcement_type": row.type,
        },
        is_active=lambda row: row.published_at is None or (
            isinstance(row.published_at, datetime) and row.published_at.date() >= datetime.now().date() - timedelta(days=30)
        ),
        min_chunk_length=40,
    ),
    "project": SourceIndexerConfig(
        source_type="project",
        model=Project,
        id_attr="id",
        text_builder=_project_text,
        metadata_builder=lambda row: {
            "title": row.title,
            "url": row.source_url,
            "status": row.status,
            "category": row.category,
        },
        min_chunk_length=40,
    ),
    "job": SourceIndexerConfig(
        source_type="job",
        model=JobListing,
        id_attr="id",
        text_builder=_job_text,
        metadata_builder=lambda row: {
            "title": row.title,
            "url": row.source_url,
            "date": _to_iso(row.published_at),
            "company": row.company,
            "is_active": bool(row.is_active),
        },
        is_active=lambda row: bool(row.is_active),
        min_chunk_length=40,
    ),
    "place": SourceIndexerConfig(
        source_type="place",
        model=Place,
        id_attr="id",
        text_builder=_place_text,
        metadata_builder=lambda row: {
            "title": row.name,
            "category": row.category,
            "subcategory": row.subcategory,
            "tags": row.tags or [],
            "address": row.address,
        },
        is_active=lambda row: bool(row.is_active),
    ),
    "institution": SourceIndexerConfig(
        source_type="institution",
        model=Institution,
        id_attr="id",
        text_builder=_institution_text,
        metadata_builder=lambda row: {
            "title": row.name,
            "category": row.category,
            "subcategory": row.subcategory,
            "address": row.address,
        },
        is_active=lambda row: bool(row.is_active),
        min_chunk_length=20,
    ),
    "outage": SourceIndexerConfig(
        source_type="outage",
        model=UtilityOutage,
        id_attr="id",
        text_builder=_outage_text,
        metadata_builder=lambda row: {
            "title": f"{row.type.upper()} Kesintisi",
            "district": row.district,
            "neighborhood": row.neighborhood,
            "source": row.source,
            "start_date": _to_iso(row.start_date),
            "end_date": _to_iso(row.end_date),
        },
        is_active=lambda row: row.end_date is None or (
            isinstance(row.end_date, datetime) and row.end_date >= datetime.now() - timedelta(days=2)
        ),
        min_chunk_length=40,
    ),
    "obituary": SourceIndexerConfig(
        source_type="obituary",
        model=Obituary,
        id_attr="id",
        text_builder=_obituary_text,
        metadata_builder=lambda row: {
            "title": row.name,
            "date": _to_iso(row.death_date),
            "location": row.funeral_location,
            "source": row.source,
        },
        min_chunk_length=40,
    ),
    "city_knowledge": SourceIndexerConfig(
        source_type="city_knowledge",
        model=CityKnowledge,
        id_attr="id",
        text_builder=_city_knowledge_text,
        metadata_builder=lambda row: {
            "title": row.title,
            "url": row.source_url,
            "last_verified_at": _to_iso(row.last_verified_at),
            "layer": row.layer,
            "neighborhood": row.neighborhood,
        },
        min_chunk_length=30,
    ),
    "transport_route": SourceIndexerConfig(
        source_type="transport_route",
        model=TransportRoute,
        id_attr="id",
        text_builder=_transport_route_text,
        metadata_builder=lambda row: {
            "title": f"{row.mode.upper()} {row.hat_no or ''}".strip(),
            "url": row.source_url,
            "last_verified_at": _to_iso(row.last_verified_at),
            "mode": row.mode,
        },
        min_chunk_length=15,
    ),
    "transport_stop": SourceIndexerConfig(
        source_type="transport_stop",
        model=TransportStop,
        id_attr="id",
        text_builder=_transport_stop_text,
        metadata_builder=lambda row: {
            "title": row.ad,
            "url": row.source_url,
            "last_verified_at": _to_iso(row.last_verified_at),
            "mode": row.mode,
            "stop_id": row.stop_id,
        },
        min_chunk_length=12,
    ),
    "transport_departure": SourceIndexerConfig(
        source_type="transport_departure",
        model=TransportDeparture,
        id_attr="id",
        text_builder=_transport_departure_text,
        metadata_builder=lambda row: {
            "title": f"Sefer {row.day_type or ''}".strip(),
            "url": row.source_url,
            "last_verified_at": _to_iso(row.last_verified_at),
            "day_type": row.day_type,
            "stop_id": row.stop_id,
        },
        min_chunk_length=10,
    ),
    "poi_catalog": SourceIndexerConfig(
        source_type="poi_catalog",
        model=PoiCatalog,
        id_attr="id",
        text_builder=_poi_catalog_text,
        metadata_builder=lambda row: {
            "title": row.ad,
            "url": row.resmi_url or row.source_url,
            "last_verified_at": _to_iso(row.last_verified_at),
            "category": row.kategori,
            "neighborhood": row.mahalle,
        },
        min_chunk_length=20,
    ),
    "municipal_service": SourceIndexerConfig(
        source_type="municipal_service",
        model=MunicipalService,
        id_attr="id",
        text_builder=_municipal_service_text,
        metadata_builder=lambda row: {
            "title": row.birim,
            "url": row.source_url,
            "last_verified_at": _to_iso(row.last_verified_at),
            "service_type": row.hizmet_tipi,
        },
        min_chunk_length=18,
    ),
    "district_stat": SourceIndexerConfig(
        source_type="district_stat",
        model=DistrictStat,
        id_attr="id",
        text_builder=_district_stat_text,
        metadata_builder=lambda row: {
            "title": f"{row.metrik_adi} {row.yil}",
            "url": row.source_url,
            "last_verified_at": _to_iso(row.last_verified_at),
            "district": row.district,
            "neighborhood": row.neighborhood,
        },
        min_chunk_length=12,
    ),
    "izban_schedule": SourceIndexerConfig(
        source_type="izban_schedule",
        model=IzbanSchedule,
        id_attr="id",
        text_builder=_izban_schedule_text,
        metadata_builder=lambda row: {
            "title": f"İZBAN {row.station or ''} {row.direction or ''}".strip(),
            "line": row.line,
            "station": row.station,
            "direction": row.direction,
            "departure_time": str(row.departure_time) if row.departure_time else None,
            "day_type": row.day_type,
        },
        min_chunk_length=10,
    ),
    "ferry_schedule": SourceIndexerConfig(
        source_type="ferry_schedule",
        model=FerrySchedule,
        id_attr="id",
        text_builder=_ferry_schedule_text,
        metadata_builder=lambda row: {
            "title": f"Feribot {row.route or ''}".strip(),
            "route": row.route,
            "company": row.company,
            "departure_time": str(row.departure_time) if row.departure_time else None,
            "day_type": row.day_type,
            "season": row.season,
        },
        min_chunk_length=10,
    ),
}


async def _fetch_existing_head(
    session: AsyncSession,
    source_type: str,
    source_id: int,
) -> DocumentChunk | None:
    stmt = (
        select(DocumentChunk)
        .where(
            DocumentChunk.source_type == source_type,
            DocumentChunk.source_id == source_id,
            DocumentChunk.chunk_index == 0,
        )
        .limit(1)
    )
    res = await session.execute(stmt)
    return res.scalars().first()


async def _delete_source_chunks(session: AsyncSession, source_type: str, source_id: int) -> None:
    await session.execute(
        delete(DocumentChunk).where(
            DocumentChunk.source_type == source_type,
            DocumentChunk.source_id == source_id,
        )
    )


async def _cleanup_stale_source_rows(
    session: AsyncSession,
    source_type: str,
    valid_ids: list[int],
) -> int:
    if valid_ids:
        stmt = delete(DocumentChunk).where(
            DocumentChunk.source_type == source_type,
            DocumentChunk.source_id.is_not(None),
            DocumentChunk.source_id.not_in(valid_ids),
        )
    else:
        stmt = delete(DocumentChunk).where(
            DocumentChunk.source_type == source_type,
            DocumentChunk.source_id.is_not(None),
        )
    res = await session.execute(stmt)
    return res.rowcount or 0


async def _index_record(
    session: AsyncSession,
    config: SourceIndexerConfig,
    record: Any,
) -> tuple[int, bool]:
    source_id = getattr(record, config.id_attr)
    text = config.text_builder(record)
    if not text:
        await _delete_source_chunks(session, config.source_type, source_id)
        return 0, False

    record_hash = content_hash(text)
    existing = await _fetch_existing_head(session, config.source_type, source_id)
    existing_meta = existing.metadata_json or {} if existing else {}
    if (
        existing
        and existing_meta.get("content_hash") == record_hash
        and existing_meta.get("embedding_model") == settings.EMBEDDING_MODEL
    ):
        return 0, True

    # UPSERT mantığı: Mevcut chunk'ları tamamen silmek yerine, çakışanları güncelle (UPSERT),
    # ardından artık kalan (stale) chunk'ları sil.
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    chunks = chunk_text(
        text,
        chunk_size=settings.CHUNK_SIZE,
        overlap=settings.CHUNK_OVERLAP,
        min_length=config.min_chunk_length or settings.CHUNK_MIN_LENGTH,
    )
    if not chunks:
        return 0, False

    base_meta = config.metadata_builder(record)
    inserted = 0
    for chunk_index, chunk in enumerate(chunks):
        try:
            embedding = await generate_embedding(chunk, prefix="passage: ")
        except Exception as exc:
            logger.warning(
                f"Embedding üretilemedi (source_type={config.source_type}, source_id={source_id}, chunk={chunk_index}): {exc}"
            )
            continue

        stmt = pg_insert(DocumentChunk).values(
            source_type=config.source_type,
            source_id=source_id,
            chunk_index=chunk_index,
            content=chunk,
            embedding=embedding,
            metadata_json={
                **base_meta,
                "content_hash": record_hash,
                "embedding_model": settings.EMBEDDING_MODEL,
                "chunk_index": chunk_index,
                "total_chunks": len(chunks),
            },
        )
        
        stmt = stmt.on_conflict_do_update(
            constraint="uix_source_chunk",
            set_={
                "content": stmt.excluded.content,
                "embedding": stmt.excluded.embedding,
                "metadata_json": stmt.excluded.metadata_json,
                "created_at": func.now(),
            }
        )
        
        await session.execute(stmt)
        inserted += 1

    # Eğer yeni chunk sayısı eski olandan az ise, artık kalan chunkları temizle
    cleanup_stmt = delete(DocumentChunk).where(
        DocumentChunk.source_type == config.source_type,
        DocumentChunk.source_id == source_id,
        DocumentChunk.chunk_index >= len(chunks)
    )
    await session.execute(cleanup_stmt)

    return inserted, False


async def sync_source_type_chunks(session: AsyncSession, source_type: str) -> dict[str, int]:
    """
    Tek bir source_type için SQL kayıtlarını document_chunks ile senkronize eder.
    """
    if not HAS_VECTOR:
        logger.warning("Chunk senkronizasyonu atlandı: pgvector destekli DocumentChunk modeli yok.")
        return {"indexed": 0, "unchanged": 0, "deleted": 0}

    config = SOURCE_CONFIGS.get(source_type)
    if not config:
        raise ValueError(f"Desteklenmeyen source_type: {source_type}")

    rows = (await session.execute(select(config.model))).scalars().all()
    valid_rows = [row for row in rows if config.is_active(row)]
    valid_ids = [getattr(row, config.id_attr) for row in valid_rows]
    deleted = await _cleanup_stale_source_rows(session, source_type, valid_ids)

    indexed = 0
    unchanged = 0
    for row in valid_rows:
        inserted, was_unchanged = await _index_record(session, config, row)
        indexed += inserted
        if was_unchanged:
            unchanged += 1

    logger.info(
        f"Chunk sync [{source_type}] tamamlandı. indexed={indexed}, unchanged={unchanged}, deleted={deleted}"
    )
    return {"indexed": indexed, "unchanged": unchanged, "deleted": deleted}


async def sync_all_document_chunks(
    session: AsyncSession,
    source_types: list[str] | None = None,
) -> dict[str, dict[str, int]]:
    """
    Tüm (veya seçili) source_type'lar için chunk senkronizasyonu.
    """
    targets = source_types or list(SOURCE_CONFIGS.keys())
    results: dict[str, dict[str, int]] = {}
    for source_type in targets:
        try:
            results[source_type] = await sync_source_type_chunks(session, source_type)
        except Exception as exc:
            logger.error(f"Chunk sync hatası [{source_type}]: {exc}")
            results[source_type] = {"indexed": 0, "unchanged": 0, "deleted": 0}
    return results
