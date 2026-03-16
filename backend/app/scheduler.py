"""
AliağaAI Scheduler
Otomatik veri güncelleme için APScheduler yapılandırması
"""

import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.scrapers import ComprehensiveScraper, DynamicScraper

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = BackgroundScheduler()


def scrape_pharmacy():
    """Nöbetçi eczane - Günde 1 kez (00:05)"""
    logger.info("🏥 Nöbetçi eczane güncelleniyor...")
    try:
        scraper = ComprehensiveScraper()
        count = scraper.scrape_pharmacy_duties()
        logger.info(f"✅ Eczane güncellendi: {count} kayıt")
    except Exception as e:
        logger.error(f"❌ Eczane hatası: {e}")


def scrape_news_and_announcements():
    """Haberler ve Duyurular - Günde 2 kez (08:00, 18:00)"""
    logger.info("📰 Haberler ve duyurular güncelleniyor...")
    try:
        scraper = DynamicScraper()
        news = scraper.scrape_news(pages=1)
        announcements = scraper.scrape_announcements(pages=1)
        logger.info(f"✅ Haberler: {news}, Duyurular: {announcements}")
    except Exception as e:
        logger.error(f"❌ Haber hatası: {e}")


def scrape_projects():
    """Projeler - Haftada 1 kez (Pazartesi 06:00)"""
    logger.info("🏗️ Projeler güncelleniyor...")
    try:
        scraper = DynamicScraper()
        count = scraper.scrape_projects()
        logger.info(f"✅ Projeler güncellendi: {count} kayıt")
    except Exception as e:
        logger.error(f"❌ Proje hatası: {e}")


def scrape_all_static():
    """Tüm statik veriler - Ayda 1 kez (1. gün 03:00)"""
    logger.info("📊 Tüm statik veriler güncelleniyor...")
    try:
        scraper = ComprehensiveScraper()
        results = scraper.run_all()
        total = sum(results.values())
        logger.info(f"✅ Statik veriler güncellendi: {total} kayıt")
    except Exception as e:
        logger.error(f"❌ Statik veri hatası: {e}")


def init_scheduler():
    """Scheduler'ı başlat ve job'ları ekle"""
    
    # Nöbetçi Eczane - Her gün 00:05
    scheduler.add_job(
        scrape_pharmacy,
        CronTrigger(hour=0, minute=5),
        id="pharmacy_daily",
        name="Nöbetçi Eczane (Günlük)",
        replace_existing=True
    )
    
    # Haberler/Duyurular - Her gün 08:00 ve 18:00
    scheduler.add_job(
        scrape_news_and_announcements,
        CronTrigger(hour=8, minute=0),
        id="news_morning",
        name="Haberler (Sabah)",
        replace_existing=True
    )
    scheduler.add_job(
        scrape_news_and_announcements,
        CronTrigger(hour=18, minute=0),
        id="news_evening",
        name="Haberler (Akşam)",
        replace_existing=True
    )
    
    # Projeler - Her Pazartesi 06:00
    scheduler.add_job(
        scrape_projects,
        CronTrigger(day_of_week="mon", hour=6, minute=0),
        id="projects_weekly",
        name="Projeler (Haftalık)",
        replace_existing=True
    )
    
    # Tüm statik veriler - Her ayın 1'i 03:00
    scheduler.add_job(
        scrape_all_static,
        CronTrigger(day=1, hour=3, minute=0),
        id="static_monthly",
        name="Statik Veriler (Aylık)",
        replace_existing=True
    )
    
    # Scheduler'ı başlat
    scheduler.start()
    logger.info("⏰ Scheduler başlatıldı!")
    
    # Aktif job'ları listele
    jobs = scheduler.get_jobs()
    logger.info(f"📋 Aktif görevler ({len(jobs)}):")
    for job in jobs:
        logger.info(f"   - {job.name}: {job.trigger}")


def shutdown_scheduler():
    """Scheduler'ı kapat"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("⏰ Scheduler kapatıldı")


def get_scheduled_jobs():
    """API için aktif job'ları döndür"""
    return [
        {
            "id": job.id,
            "name": job.name,
            "next_run": str(job.next_run_time) if job.next_run_time else None,
            "trigger": str(job.trigger)
        }
        for job in scheduler.get_jobs()
    ]


def run_job_now(job_id: str) -> bool:
    """Manuel olarak bir job'u çalıştır"""
    job_map = {
        "pharmacy_daily": scrape_pharmacy,
        "news_morning": scrape_news_and_announcements,
        "news_evening": scrape_news_and_announcements,
        "projects_weekly": scrape_projects,
        "static_monthly": scrape_all_static,
    }
    
    if job_id in job_map:
        job_map[job_id]()
        return True
    return False
