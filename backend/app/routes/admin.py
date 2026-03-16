"""
Admin Routes - Scraper ve Scheduler Kontrolü
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

from app.scrapers import ComprehensiveScraper, DynamicScraper
from app.scheduler import get_scheduled_jobs, run_job_now

logger = logging.getLogger(__name__)
router = APIRouter()


class ScrapeResponse(BaseModel):
    status: str
    message: str
    count: Optional[int] = None
    scraped_at: datetime


class SchedulerJobResponse(BaseModel):
    id: str
    name: str
    next_run: Optional[str]
    trigger: str


# =============================================================================
# SCRAPER ENDPOINTS
# =============================================================================

@router.post("/scrape/static", response_model=ScrapeResponse)
async def scrape_static():
    """Tüm statik verileri çek (tarih, coğrafya, kurumlar, vb.)"""
    try:
        scraper = ComprehensiveScraper()
        results = scraper.run_all()
        total = sum(results.values())
        
        return ScrapeResponse(
            status="success",
            message=f"Scraped {total} static records",
            count=total,
            scraped_at=datetime.now()
        )
    except Exception as e:
        logger.error(f"Static scrape failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scrape/dynamic", response_model=ScrapeResponse)
async def scrape_dynamic():
    """Dinamik verileri çek (haberler, duyurular, projeler)"""
    try:
        scraper = DynamicScraper()
        results = scraper.run_all()
        total = sum(results.values())
        
        return ScrapeResponse(
            status="success",
            message=f"Scraped {total} dynamic records",
            count=total,
            scraped_at=datetime.now()
        )
    except Exception as e:
        logger.error(f"Dynamic scrape failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scrape/news", response_model=ScrapeResponse)
async def scrape_news():
    """Sadece haberleri çek"""
    try:
        scraper = DynamicScraper()
        count = scraper.scrape_news(pages=2)
        
        return ScrapeResponse(
            status="success",
            message=f"Scraped {count} news",
            count=count,
            scraped_at=datetime.now()
        )
    except Exception as e:
        logger.error(f"News scrape failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scrape/pharmacy", response_model=ScrapeResponse)
async def scrape_pharmacy():
    """Nöbetçi eczaneleri çek"""
    try:
        scraper = ComprehensiveScraper()
        count = scraper.scrape_pharmacy_duties()
        
        return ScrapeResponse(
            status="success",
            message=f"Scraped {count} pharmacies",
            count=count,
            scraped_at=datetime.now()
        )
    except Exception as e:
        logger.error(f"Pharmacy scrape failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scrape/all", response_model=ScrapeResponse)
async def scrape_all():
    """Tüm verileri çek (statik + dinamik)"""
    try:
        total = 0
        
        # Statik veriler
        static = ComprehensiveScraper()
        results = static.run_all()
        total += sum(results.values())
        
        # Dinamik veriler
        dynamic = DynamicScraper()
        results = dynamic.run_all()
        total += sum(results.values())
        
        return ScrapeResponse(
            status="success",
            message=f"Scraped {total} total records",
            count=total,
            scraped_at=datetime.now()
        )
    except Exception as e:
        logger.error(f"Full scrape failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# SCHEDULER ENDPOINTS
# =============================================================================

@router.get("/scheduler/jobs")
async def list_scheduled_jobs() -> List[Dict[str, Any]]:
    """Zamanlanmış görevleri listele"""
    return get_scheduled_jobs()


@router.post("/scheduler/run/{job_id}")
async def trigger_job(job_id: str):
    """Bir görevi manuel olarak çalıştır"""
    success = run_job_now(job_id)
    if success:
        return {"status": "success", "message": f"Job {job_id} triggered"}
    raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
