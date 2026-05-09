import asyncio

from loguru import logger

from app.database import async_session
from app.services.chunk_indexer import sync_all_document_chunks
from app.services.collectapi_client import fetch_all
from app.services.data_quality import run_data_quality_pass
from app.services.earthquake_client import fetch_earthquakes
from app.services.scraper_news import scrape_and_save_news, sync_events_from_news
from app.services.seed_data_extended import seed_extended
from app.services.scraper_aliaga_bel import scrape_aliaga_bel_all
from app.services.scraper_izmir_mezarlik import scrape_izmir_mezarlik
from app.services.scraper_izmir_open_data import sync_open_data_city_tables
from app.services.scraper_knowledge_layers import sync_knowledge_layers
from app.services.scraper_outages import scrape_outages


async def run_all():
    logger.info("Canli veri kaziyicilar baslatiliyor...")

    async with async_session() as session:
        try:
            logger.info("CollectAPI servisleri cagriliyor...")
            await fetch_all(session)
        except Exception as e:
            logger.error(f"CollectAPI hatasi: {e}")

        try:
            logger.info("Kandilli deprem servisi cagriliyor...")
            await fetch_earthquakes(session)
        except Exception as e:
            logger.error(f"Deprem servisi hatasi: {e}")

        try:
            logger.info("Aliaga haberleri cekiliyor...")
            await scrape_and_save_news(session)
            await sync_events_from_news(session)
            await session.commit()
        except Exception as e:
            logger.error(f"Haber/Etkinlik botu hatasi: {e}")

        try:
            logger.info("Statik gercek veriler ekleniyor...")
            res = await seed_extended(session)
            logger.info(f"Statik veri sonucu: {res}")
        except Exception as e:
            logger.error(f"Statik verileri yukleme hatasi: {e}")

        try:
            logger.info("Aliaga Belediyesi sayfalarindan kazima yapiliyor...")
            await scrape_aliaga_bel_all(session)
        except Exception as e:
            logger.error(f"Belediye botu hatasi: {e}")

        try:
            logger.info("Izmir Acik Veri ile taksi/pazar tablolari senkronize ediliyor...")
            stats = await sync_open_data_city_tables(session)
            logger.info(f"OpenData sehir tablolari sonucu: {stats}")
        except Exception as e:
            logger.error(f"OpenData sehir tablolari senkronizasyon hatasi: {e}")

        try:
            logger.info("Yeni bilgi katmanlari (ulasim/poi/kurumsal/demografi) senkronize ediliyor...")
            k_stats = await sync_knowledge_layers(session)
            logger.info(f"Knowledge layer sonucu: {k_stats}")
        except Exception as e:
            logger.error(f"Knowledge layer senkronizasyon hatasi: {e}")

        try:
            logger.info("Vefat ve kesinti kaynaklari kaziniyor...")
            await scrape_izmir_mezarlik(session)
            await scrape_outages(session)
        except Exception as e:
            logger.error(f"Vefat/Kesinti botu hatasi: {e}")

        try:
            logger.info("Data quality pass calistiriliyor...")
            await run_data_quality_pass(session)
        except Exception as e:
            logger.error(f"Data quality pass hatasi: {e}")

        try:
            logger.info("Yeni bilgi katmanlari icin chunk indeksleri guncelleniyor...")
            chunk_stats = await sync_all_document_chunks(
                session,
                source_types=[
                    "transport_route",
                    "transport_stop",
                    "transport_departure",
                    "poi_catalog",
                    "municipal_service",
                    "district_stat",
                ],
            )
            logger.info(f"Knowledge layer chunk sonucu: {chunk_stats}")
            await session.commit()
        except Exception as e:
            logger.error(f"Knowledge layer chunk hatasi: {e}")

    logger.success("Tum canli veri toplama islemleri tamamlandi. check_tables.py ile kontrol edilebilir.")


if __name__ == "__main__":
    asyncio.run(run_all())
