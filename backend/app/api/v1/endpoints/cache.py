"""Cache (CollectAPI vs) Endpoint'leri."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.cache import (
    WeatherCache, PrayerTimesCache, FuelPricesCache, 
    CurrencyCache, GoldCache, EarthquakesCache
)
from app.schemas.cache import (
    WeatherResponse, PrayerTimesResponse, FuelPricesResponse,
    CurrencyResponse, GoldResponse, EarthquakeResponse
)

router = APIRouter()

@router.get("/weather", response_model=list[WeatherResponse])
async def get_weather(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(WeatherCache).order_by(WeatherCache.date.desc()).limit(1))
    return result.scalars().all()

@router.get("/prayers", response_model=list[PrayerTimesResponse])
async def get_prayers(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(PrayerTimesCache).order_by(PrayerTimesCache.date.desc()).limit(1))
    return result.scalars().all()

@router.get("/fuel", response_model=list[FuelPricesResponse])
async def get_fuel(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(FuelPricesCache).order_by(FuelPricesCache.fetched_at.desc()).limit(1))
    return result.scalars().all()

@router.get("/currency", response_model=list[CurrencyResponse])
async def get_currency(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(CurrencyCache))
    return result.scalars().all()

@router.get("/gold", response_model=list[GoldResponse])
async def get_gold(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(GoldCache))
    return result.scalars().all()

@router.get("/earthquakes", response_model=list[EarthquakeResponse])
async def get_earthquakes(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(EarthquakesCache).order_by(EarthquakesCache.event_date.desc()).limit(20))
    return result.scalars().all()
