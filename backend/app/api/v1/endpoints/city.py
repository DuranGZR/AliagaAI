"""Şehir Altyapı Endpoint'leri."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.city import EmergencyContact, StreetMarket, TaxiStand, PostalCode
from app.schemas.city import (
    EmergencyContactResponse, StreetMarketResponse, TaxiStandResponse, PostalCodeResponse
)

router = APIRouter()

@router.get("/emergency", response_model=list[EmergencyContactResponse])
async def get_emergency_contacts(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), session: AsyncSession = Depends(get_db)):
    stmt = select(EmergencyContact).order_by(EmergencyContact.priority.asc()).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()

@router.get("/markets", response_model=list[StreetMarketResponse])
async def get_markets(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), session: AsyncSession = Depends(get_db)):
    stmt = select(StreetMarket).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()

@router.get("/taxis", response_model=list[TaxiStandResponse])
async def get_taxis(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), session: AsyncSession = Depends(get_db)):
    stmt = select(TaxiStand).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()

@router.get("/postalcodes", response_model=list[PostalCodeResponse])
async def get_postalcodes(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=200), session: AsyncSession = Depends(get_db)):
    stmt = select(PostalCode).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()
