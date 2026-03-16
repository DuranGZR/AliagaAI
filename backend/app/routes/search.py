from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date

from app.database import get_db
from app.models import PharmacyDuty, Place, News, Event, Announcement, PublicInstitution, HealthFacility
from app.schemas import PharmacyOut, PlaceOut, NewsOut, EventOut, AnnouncementOut, InstitutionOut, ChatRequest, ChatResponse
from app.services.query_router import QueryRouter

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, db: AsyncSession = Depends(get_db)):
    router_service = QueryRouter(db)
    result = await router_service.process_query(body.query)
    return ChatResponse(
        query=result["query"],
        ai_response=result["ai_response"],
        intent=result["intent"],
        results=result["sql_results"] + result["rag_results"],
        result_count=result["result_count"],
    )


@router.get("/pharmacies", response_model=list[PharmacyOut])
async def get_pharmacies(
    today_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(PharmacyDuty)
    if today_only:
        stmt = stmt.where(PharmacyDuty.duty_date == date.today())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/places", response_model=list[PlaceOut])
async def get_places(
    category: str | None = Query(None),
    limit: int = Query(10, le=50),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Place).where(Place.is_active.is_(True))
    if category:
        stmt = stmt.where(Place.category == category)
    stmt = stmt.order_by(Place.rating.desc().nullslast()).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/places/categories")
async def get_place_categories(db: AsyncSession = Depends(get_db)):
    stmt = select(Place.category).distinct().where(Place.is_active.is_(True))
    result = await db.execute(stmt)
    return [row[0] for row in result.all() if row[0]]


@router.get("/news", response_model=list[NewsOut])
async def get_news(
    limit: int = Query(10, le=50),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(News).order_by(News.published_date.desc().nullslast()).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/events", response_model=list[EventOut])
async def get_events(
    upcoming: bool = Query(True),
    limit: int = Query(10, le=50),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Event)
    if upcoming:
        stmt = stmt.where(Event.event_date >= date.today())
    stmt = stmt.order_by(Event.event_date.asc()).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/announcements", response_model=list[AnnouncementOut])
async def get_announcements(
    limit: int = Query(10, le=50),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Announcement).order_by(Announcement.published_date.desc().nullslast()).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/institutions", response_model=list[InstitutionOut])
async def get_institutions(db: AsyncSession = Depends(get_db)):
    stmt = select(PublicInstitution).limit(50)
    result = await db.execute(stmt)
    return result.scalars().all()
