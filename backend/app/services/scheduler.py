"""
AliağaAI — Görev Zamanlayıcı (APScheduler).

Belirli periyotlarla veri çekici fonksiyonları (CollectAPI, scraper vb.) çalıştırır.
FastAPI lifespan (startup/shutdown) içine entegre edilecek.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from app.database import async_session
from app.services.collectapi_client import fetch_all
from app.services.earthquake_client import fetch_earthquakes
from app.services.scraper_news import scrape_and_save_news

scheduler = AsyncIOScheduler()

async def job_collectapi():
    """CollectAPI verilerini günceller."""
    try:
        async with async_session() as session:
            await fetch_all(session)
    except Exception as e:
        logger.error(f"Zamanlanmış görev hatası (CollectAPI): {e}")

async def job_earthquakes():
    """Kandilli deprem verilerini günceller."""
    try:
        async with async_session() as session:
            await fetch_earthquakes(session)
    except Exception as e:
        logger.error(f"Zamanlanmış görev hatası (Deprem): {e}")

async def job_news():
    """Haberleri çeker."""
    try:
        async with async_session() as session:
            await scrape_and_save_news(session)
    except Exception as e:
        logger.error(f"Zamanlanmış görev hatası (Haberler): {e}")


def start_scheduler():
    """Zamanlayıcıyı başlatır ve görevleri ekler."""
    # Eczane, hava, namaz vb. CollectAPI servisleri — Her saat başı
    scheduler.add_job(job_collectapi, "interval", hours=1, id="job_collectapi", replace_existing=True)
    
    # Deprem verisi — 15 dakikada bir
    scheduler.add_job(job_earthquakes, "interval", minutes=15, id="job_earthquakes", replace_existing=True)
    
    # Haberler — 6 saatte bir
    scheduler.add_job(job_news, "interval", hours=6, id="job_news", replace_existing=True)

    scheduler.start()
    logger.info("APScheduler başlatıldı ve periyodik görevler eklendi.")


def stop_scheduler():
    """Zamanlayıcıyı durdurur."""
    scheduler.shutdown()
    logger.info("APScheduler durduruldu.")
