from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.database import async_session, close_db, init_db
from app.services.city_data_ingestion import (
    ALL_CITY_DATA_SOURCE_TYPES,
    get_city_data_counts,
    ingest_all_city_data,
    sync_osm_city_directory,
)
from app.services.chunk_indexer import sync_all_document_chunks
from app.services.data_completeness import ensure_core_city_data
from app.services.data_quality import run_data_quality_pass
from app.services.embedding import generate_embedding
from app.services.scraper_city_info import scrape_and_save_city_info
from app.services.scraper_izmir_mezarlik import scrape_izmir_mezarlik
from app.services.scraper_knowledge_layers import sync_knowledge_layers
from app.services.scraper_outages import scrape_outages


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest broad Aliaga city data into SQL tables and pgvector chunks."
    )
    parser.add_argument("--no-osm", action="store_true", help="Skip OpenStreetMap/Overpass ingestion.")
    parser.add_argument("--no-chunks", action="store_true", help="Skip document_chunks synchronization.")
    parser.add_argument(
        "--no-legacy-city-info",
        action="store_true",
        help="Skip legacy direct city_info chunk refresh.",
    )
    parser.add_argument(
        "--resume-after-open-data",
        action="store_true",
        help="Run only OSM, knowledge layers, cleanup, and chunk sync.",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    await init_db()
    async with async_session() as session:
        if args.resume_after_open_data:
            stats = {}
            if not args.no_osm:
                stats["osm_directory"] = await sync_osm_city_directory(session)
                await session.commit()
            stats["knowledge_layers"] = await sync_knowledge_layers(session)
            await session.commit()
            stats["obituaries"] = await scrape_izmir_mezarlik(session) or 0
            stats["outages"] = await scrape_outages(session) or 0
            await session.commit()
            stats["data_completeness"] = await ensure_core_city_data(session)
            await session.commit()
            stats["data_quality"] = await run_data_quality_pass(session)
            if not args.no_chunks and not args.no_legacy_city_info:
                stats["legacy_city_info_chunks"] = await scrape_and_save_city_info(
                    session,
                    embedding_fn=generate_embedding,
                )
                await session.commit()
            if not args.no_chunks:
                stats["chunk_sync"] = await sync_all_document_chunks(
                    session,
                    source_types=ALL_CITY_DATA_SOURCE_TYPES,
                )
                await session.commit()
            stats["counts"] = await get_city_data_counts(session)
        else:
            stats = await ingest_all_city_data(
                session,
                include_osm=not args.no_osm,
                sync_chunks=not args.no_chunks,
                include_legacy_city_info_chunks=not args.no_legacy_city_info,
            )
    print(json.dumps(stats, ensure_ascii=False, indent=2, default=str))
    await close_db()


if __name__ == "__main__":
    asyncio.run(main())
