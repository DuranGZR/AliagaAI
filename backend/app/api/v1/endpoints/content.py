"""İçerik Endpoint'leri."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.content import News, Event, Announcement, Project, JobListing, Gallery
from app.schemas.content import (
    NewsResponse,
    EventResponse,
    AnnouncementResponse,
    ProjectResponse,
    JobListingResponse,
    GalleryResponse,
)
from sqlalchemy.orm import selectinload

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
async def get_announcements(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    item_type: str | None = Query(None, alias="type"),
    session: AsyncSession = Depends(get_db),
):
    stmt = select(Announcement)
    if item_type:
        stmt = stmt.where(Announcement.type == item_type)
    stmt = stmt.order_by(Announcement.published_at.desc(), Announcement.id.desc()).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()

@router.get("/projects", response_model=list[ProjectResponse])
async def get_projects(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), session: AsyncSession = Depends(get_db)):
    stmt = select(Project).order_by(Project.id.desc()).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()

@router.get("/jobs", response_model=list[JobListingResponse])
async def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    active_only: bool = Query(True),
    session: AsyncSession = Depends(get_db),
):
    stmt = select(JobListing)
    if active_only:
        stmt = stmt.where(JobListing.is_active.is_(True))
    stmt = stmt.order_by(JobListing.published_at.desc(), JobListing.id.desc()).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()

@router.get("/galleries", response_model=list[GalleryResponse])
async def get_galleries(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), session: AsyncSession = Depends(get_db)):
    stmt = select(Gallery).options(selectinload(Gallery.images)).order_by(Gallery.publish_date.desc().nullslast(), Gallery.id.desc()).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()

@router.get("/galleries/{gallery_id}", response_model=GalleryResponse)
async def get_gallery(gallery_id: int, session: AsyncSession = Depends(get_db)):
    stmt = select(Gallery).options(selectinload(Gallery.images)).where(Gallery.id == gallery_id)
    result = await session.execute(stmt)
    gallery = result.scalars().first()
    if not gallery:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Gallery not found")
    return gallery

