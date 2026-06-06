"""Mekanlar Endpoint'leri."""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import case, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.places import Place, Institution, ServiceProvider
from app.schemas.places import PlaceResponse, InstitutionResponse, ServiceProviderResponse
from app.core.limiter import limiter

router = APIRouter()

@router.get("/", response_model=list[PlaceResponse])
@limiter.limit("60/minute")
async def get_places(request: Request, category: str = None, skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=1000), session: AsyncSession = Depends(get_db)):
    stmt = select(Place).where(Place.is_active == True)
    if category:
        stmt = stmt.where(Place.category == category)
    discover_priority = case(
        (Place.category.in_(["turistik", "restoran", "kafe", "park", "plaj", "sahil", "kultur", "spor_park"]), 0),
        (Place.category.in_(["market", "magaza", "hizmet", "konaklama"]), 1),
        else_=2,
    )
    completeness_priority = (
        case((Place.description.is_not(None), 0), else_=1)
        + case((Place.image_url.is_not(None), 0), else_=1)
        + case((Place.latitude.is_not(None), 0), else_=1)
    )
    stmt = stmt.order_by(
        discover_priority.asc(),
        completeness_priority.asc(),
        Place.rating.desc(),
        Place.name.asc(),
    ).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()

@router.get("/institutions", response_model=list[InstitutionResponse])
async def get_institutions(category: str = None, skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), session: AsyncSession = Depends(get_db)):
    stmt = select(Institution).where(Institution.is_active == True)
    if category:
        stmt = stmt.where(Institution.category == category)
    stmt = stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()

@router.get("/services", response_model=list[ServiceProviderResponse])
async def get_services(category: str = None, skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), session: AsyncSession = Depends(get_db)):
    stmt = select(ServiceProvider).where(ServiceProvider.is_active == True)
    if category:
        stmt = stmt.where(ServiceProvider.category == category)
    stmt = stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()
