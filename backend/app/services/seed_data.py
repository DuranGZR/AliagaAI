"""
AliağaAI - Seed data yükleyici.

Sabit ve nadiren değişen verileri veritabanına yükler.
Artık veriler seed_data_massive.py dosyasından çekilmektedir.
"""
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.city import CityKnowledge, EmergencyContact, StreetMarket, PostalCode, TaxiStand
from app.models.places import Place, Institution

from app.services.seed_data_massive import (
    EMERGENCY_CONTACTS,
    STREET_MARKETS,
    PLACES,
    INSTITUTIONS,
    TAXI_STANDS,
    POSTAL_CODES,
    CITY_KNOWLEDGE,
)

async def _insert_if_empty(session: AsyncSession, model, data_list: list[dict]):
    """Tablo boşsa verileri yükler, doluysa atlar."""
    result = await session.execute(select(model).limit(1))
    if result.scalars().first() is not None:
        return 0  # zaten dolu

    count = 0
    for item in data_list:
        session.add(model(**item))
        count += 1
    await session.flush()
    return count


async def _sync_city_knowledge(session: AsyncSession, data_list: list[dict]) -> int:
    """
    city_knowledge tablosunu seed setiyle senkronize eder.
    - Aynı (layer, title) varsa günceller
    - Yoksa ekler
    - Seed setinde olmayanları siler
    """
    existing_rows = (await session.execute(select(CityKnowledge))).scalars().all()
    existing_map = {
        ((row.layer or "").strip().lower(), (row.title or "").strip().lower()): row
        for row in existing_rows
    }

    seen_keys: set[tuple[str, str]] = set()
    changes = 0

    for item in data_list:
        key = ((item.get("layer") or "").strip().lower(), (item.get("title") or "").strip().lower())
        seen_keys.add(key)
        existing = existing_map.get(key)
        if existing is None:
            session.add(CityKnowledge(**item))
            changes += 1
            continue

        updated = False
        for field in ("neighborhood", "summary", "tags", "source_url", "last_verified_at"):
            incoming = item.get(field)
            if getattr(existing, field) != incoming:
                setattr(existing, field, incoming)
                updated = True
        if updated:
            changes += 1

    for key, stale_row in existing_map.items():
        if key not in seen_keys:
            await session.delete(stale_row)
            changes += 1

    await session.flush()
    return changes


async def seed_all(session: AsyncSession) -> dict[str, int]:
    """
    Tüm seed verileri yükler. Zaten veri olan tablolara dokunmaz.
    Dönen dict, tablo adı -> eklenen satır sayısı eşlemesidir.
    """
    results = {}

    results["emergency_contacts"] = await _insert_if_empty(
        session, EmergencyContact, EMERGENCY_CONTACTS
    )
    results["street_markets"] = await _insert_if_empty(
        session, StreetMarket, STREET_MARKETS
    )
    results["places"] = await _insert_if_empty(session, Place, PLACES)
    results["institutions"] = await _insert_if_empty(
        session, Institution, INSTITUTIONS
    )
    results["taxi_stands"] = await _insert_if_empty(session, TaxiStand, TAXI_STANDS)
    results["postal_codes"] = await _insert_if_empty(session, PostalCode, POSTAL_CODES)
    results["city_knowledge"] = await _sync_city_knowledge(session, CITY_KNOWLEDGE)

    # RAG İçin Şehir Bilgilerini (Tarihçe vb.) İndir ve Vektörleştir
    try:
        from app.models.city import DocumentChunk
        from loguru import logger
        chunk_check = await session.execute(select(DocumentChunk).where(DocumentChunk.source_type == "city_info").limit(1))
        if chunk_check.scalars().first() is None:
            logger.info("Şehir bilgileri (city_info) RAG veritabanı için yükleniyor...")
            from app.services.scraper_city_info import scrape_and_save_city_info
            from app.services.embedding import generate_embedding
            results["city_info_chunks"] = await scrape_and_save_city_info(session, embedding_fn=generate_embedding)
    except Exception as e:
        from loguru import logger
        logger.error(f"Şehir bilgisi RAG verileri yüklenirken hata oluştu: {e}")

    # Yapılandırılmış içerikleri de document_chunks ile senkronize et
    try:
        from app.services.chunk_indexer import sync_all_document_chunks
        chunk_sync = await sync_all_document_chunks(
            session,
            source_types=[
                "news", "event", "announcement", "project", "job",
                "place", "institution", "outage", "obituary",
                "city_knowledge", "transport_route", "transport_stop",
                "poi_catalog", "municipal_service", "district_stat",
                "izban_schedule", "ferry_schedule",
            ],
        )
        results["chunk_sync"] = sum(v.get("indexed", 0) for v in chunk_sync.values())
    except Exception as e:
        from loguru import logger
        logger.error(f"Structured içerik chunk senkronizasyonunda hata: {e}")

    await session.commit()
    return results
