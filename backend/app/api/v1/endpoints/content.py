"""İçerik Endpoint'leri."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.content import News, Event, Announcement, Project
from app.schemas.content import NewsResponse, EventResponse, AnnouncementResponse, ProjectResponse

router = APIRouter()

@router.get("/news", response_model=list[NewsResponse])
async def get_news(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100), session: AsyncSession = Depends(get_db)):
    stmt = select(News).order_by(News.published_at.desc(), News.id.desc()).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()

@router.get("/events", response_model=list[EventResponse])
async def get_events(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100), session: AsyncSession = Depends(get_db)):
    stmt = select(Event).order_by(Event.event_date.asc()).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()

@router.get("/announcements", response_model=list[AnnouncementResponse])
async def get_announcements(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100), session: AsyncSession = Depends(get_db)):
    stmt = select(Announcement).order_by(Announcement.published_at.desc()).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()

@router.get("/projects", response_model=list[ProjectResponse])
async def get_projects(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), session: AsyncSession = Depends(get_db)):
    stmt = select(Project).order_by(Project.id.desc()).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()
