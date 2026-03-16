from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.database import get_db
from app.models import Place
from app.schemas import PlaceCreate, PlaceUpdate, PlaceOut, ScrapeResponse
from app.scrapers import ComprehensiveScraper, DynamicScraper
from app.scheduler import get_scheduled_jobs, run_job_now
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/places", response_model=PlaceOut)
async def create_place(body: PlaceCreate, db: AsyncSession = Depends(get_db)):
    place = Place(**body.model_dump(exclude_none=True))
    db.add(place)
    await db.flush()
    await db.refresh(place)
    return place


@router.put("/places/{place_id}", response_model=PlaceOut)
async def update_place(place_id: int, body: PlaceUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Place).where(Place.id == place_id))
    place = result.scalar_one_or_none()
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(place, field, value)

    await db.flush()
    await db.refresh(place)
    return place


@router.delete("/places/{place_id}")
async def delete_place(place_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Place).where(Place.id == place_id))
    place = result.scalar_one_or_none()
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    await db.delete(place)
    return {"status": "deleted", "id": place_id}


@router.post("/scrape/pharmacy", response_model=ScrapeResponse)
async def scrape_pharmacy():
    try:
        scraper = ComprehensiveScraper()
        count = scraper.scrape_pharmacy_duties()
        return ScrapeResponse(status="success", message=f"Scraped {count} pharmacies", count=count, scraped_at=datetime.now())
    except Exception as e:
        logger.error(f"Pharmacy scrape failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scrape/news", response_model=ScrapeResponse)
async def scrape_news():
    try:
        scraper = DynamicScraper()
        count = scraper.scrape_news(pages=2)
        return ScrapeResponse(status="success", message=f"Scraped {count} news", count=count, scraped_at=datetime.now())
    except Exception as e:
        logger.error(f"News scrape failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scrape/all", response_model=ScrapeResponse)
async def scrape_all():
    try:
        total = 0
        static = ComprehensiveScraper()
        results = static.run_all()
        total += sum(results.values())
        dynamic = DynamicScraper()
        results = dynamic.run_all()
        total += sum(results.values())
        return ScrapeResponse(status="success", message=f"Scraped {total} total records", count=total, scraped_at=datetime.now())
    except Exception as e:
        logger.error(f"Full scrape failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scheduler/jobs")
async def list_scheduled_jobs():
    return get_scheduled_jobs()


@router.post("/scheduler/run/{job_id}")
async def trigger_job(job_id: str):
    success = run_job_now(job_id)
    if success:
        return {"status": "success", "message": f"Job {job_id} triggered"}
    raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
