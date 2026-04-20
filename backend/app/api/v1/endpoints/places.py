"""Mekanlar Endpoint'leri."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.places import Place, Institution, ServiceProvider
from app.schemas.places import PlaceResponse, InstitutionResponse, ServiceProviderResponse

router = APIRouter()

@router.get("/", response_model=list[PlaceResponse])
async def get_places(category: str = None, skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), session: AsyncSession = Depends(get_db)):
    stmt = select(Place).where(Place.is_active == True)
    if category:
        stmt = stmt.where(Place.category == category)
    stmt = stmt.offset(skip).limit(limit)
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
