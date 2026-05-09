"""
AliagaAI - Gorev Zamanlayici (APScheduler).
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from app.database import async_session
from app.services.chunk_indexer import sync_all_document_chunks
from app.services.collectapi_client import fetch_all
from app.services.data_quality import run_data_quality_pass
from app.services.earthquake_client import fetch_earthquakes
from app.services.scraper_aliaga_bel import scrape_aliaga_bel_all
from app.services.scraper_city_info import scrape_and_save_city_info
from app.services.scraper_news import scrape_and_save_news, sync_events_from_news
from app.services.scraper_izmir_mezarlik import scrape_izmir_mezarlik
from app.services.scraper_izmir_open_data import sync_open_data_city_tables
from app.services.scraper_knowledge_layers import sync_knowledge_layers
from app.services.scraper_outages import scrape_outages
from app.services.embedding import generate_embedding

scheduler = AsyncIOScheduler()


async def job_collectapi():
    try:
        async with async_session() as session:
            await fetch_all(session)
    except Exception as e:
        logger.error(f"Zamanlanmis gorev hatasi (CollectAPI): {e}")


async def job_earthquakes():
    try:
        async with async_session() as session:
            await fetch_earthquakes(session)
    except Exception as e:
        logger.error(f"Zamanlanmis gorev hatasi (Deprem): {e}")


async def job_news():
    try:
        async with async_session() as session:
            await scrape_and_save_news(session)
            await sync_events_from_news(session)
            await sync_all_document_chunks(session, source_types=["news", "event"])
            await session.commit()
    except Exception as e:
        logger.error(f"Zamanlanmis gorev hatasi (Haber/Etkinlik): {e}")


async def job_aliaga_bel():
    try:
        async with async_session() as session:
            await scrape_aliaga_bel_all(session)
            await sync_open_data_city_tables(session)
            await sync_knowledge_layers(session)
            await sync_all_document_chunks(
                session,
                source_types=[
                    "announcement",
                    "project",
                    "job",
                    "transport_route",
                    "transport_stop",
                    "transport_departure",
                    "poi_catalog",
                    "municipal_service",
                    "district_stat",
                ],
            )
            await session.commit()
    except Exception as e:
        logger.error(f"Zamanlanmis gorev hatasi (Aliaga Belediye icerikleri): {e}")


async def job_obituaries_outages():
    try:
        async with async_session() as session:
            await scrape_izmir_mezarlik(session)
            await scrape_outages(session)
            await run_data_quality_pass(session)
            await sync_all_document_chunks(session, source_types=["obituary", "outage"])
            await session.commit()
    except Exception as e:
        logger.error(f"Zamanlanmis gorev hatasi (Vefat/Kesinti): {e}")


async def job_chunk_sync():
    try:
        async with async_session() as session:
            await sync_all_document_chunks(
                session,
                source_types=[
                    "news",
                    "event",
                    "announcement",
                    "project",
                    "job",
                    "place",
                    "institution",
                    "outage",
                    "obituary",
                    "city_knowledge",
                    "transport_route",
                    "transport_stop",
                    "transport_departure",
                    "poi_catalog",
                    "municipal_service",
                    "district_stat",
                ],
            )
            await session.commit()
    except Exception as e:
        logger.error(f"Zamanlanmis gorev hatasi (Chunk sync): {e}")


async def job_city_info_refresh():
    try:
        async with async_session() as session:
            chunk_count = await scrape_and_save_city_info(session, embedding_fn=generate_embedding)
            await session.commit()
            logger.info(f"City info yenileme tamamlandi. Uretilen chunk: {chunk_count}")
    except Exception as e:
        logger.error(f"Zamanlanmis gorev hatasi (City info refresh): {e}")


def start_scheduler():
    scheduler.add_job(job_collectapi, "interval", hours=1, id="job_collectapi", replace_existing=True)
    scheduler.add_job(job_earthquakes, "interval", minutes=15, id="job_earthquakes", replace_existing=True)
    scheduler.add_job(job_news, "interval", hours=4, id="job_news", replace_existing=True)
    scheduler.add_job(job_aliaga_bel, "interval", hours=6, id="job_aliaga_bel", replace_existing=True)
    scheduler.add_job(job_obituaries_outages, "interval", hours=4, id="job_obituaries_outages", replace_existing=True)
    scheduler.add_job(job_chunk_sync, "interval", hours=2, id="job_chunk_sync", replace_existing=True)
    scheduler.add_job(job_city_info_refresh, "interval", hours=24, id="job_city_info_refresh", replace_existing=True)

    scheduler.start()
    logger.info("APScheduler baslatildi ve periyodik gorevler eklendi.")


def stop_scheduler():
    scheduler.shutdown()
    logger.info("APScheduler durduruldu.")
