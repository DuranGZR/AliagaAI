"""Sehir altyapi endpointleri."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.city import (
    EmergencyContact,
    IzbanSchedule,
    PostalCode,
    StreetMarket,
    TaxiStand,
    UtilityOutage,
)
from app.schemas.city import (
    EmergencyContactResponse,
    IzbanSummaryResponse,
    PostalCodeResponse,
    StreetMarketResponse,
    TaxiStandResponse,
    UtilityOutageResponse,
)

router = APIRouter()


@router.get("/emergency", response_model=list[EmergencyContactResponse])
async def get_emergency_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    stmt = select(EmergencyContact).order_by(EmergencyContact.priority.asc()).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get("/markets", response_model=list[StreetMarketResponse])
async def get_markets(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    stmt = select(StreetMarket).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get("/taxis", response_model=list[TaxiStandResponse])
async def get_taxis(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    stmt = select(TaxiStand).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get("/postalcodes", response_model=list[PostalCodeResponse])
async def get_postalcodes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    session: AsyncSession = Depends(get_db),
):
    stmt = select(PostalCode).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get("/outages", response_model=list[UtilityOutageResponse])
async def get_outages(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db),
):
    stmt = select(UtilityOutage).order_by(UtilityOutage.start_date.desc()).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get("/izban/summary", response_model=IzbanSummaryResponse)
async def get_izban_summary(session: AsyncSession = Depends(get_db)):
    rows = (await session.execute(select(IzbanSchedule).order_by(IzbanSchedule.departure_time.asc()))).scalars().all()
    total = len(rows)
    if total == 0:
        return IzbanSummaryResponse(
            total_records=0,
            status="unknown",
            message="IZBAN verisi henuz mevcut degil.",
        )

    now_time = datetime.now().time()
    next_row = next((row for row in rows if row.departure_time and row.departure_time >= now_time), None)
    if next_row and next_row.departure_time:
        next_text = next_row.departure_time.strftime("%H:%M")
        status = "ok"
        message = f"Sonraki sefer: {next_text}"
    else:
        next_text = None
        status = "limited"
        message = "Bugun icin yeni sefer gorunmuyor."

    latest_update = max((row.updated_at for row in rows if row.updated_at), default=None)
    return IzbanSummaryResponse(
        total_records=total,
        next_departure=next_text,
        status=status,
        message=message,
        updated_at=latest_update,
    )
