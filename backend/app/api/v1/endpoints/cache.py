"""Cache (CollectAPI vs) Endpoint'leri."""
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
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
from app.services.collectapi_client import (
    fetch_currency,
    fetch_fuel_prices,
    fetch_gold,
    fetch_prayer_times,
    fetch_weather,
)
from app.utils.cache import cache_store

router = APIRouter()


def _is_stale(value: datetime | None, hours: int) -> bool:
    if value is None:
        return True
    now = datetime.now(timezone.utc)
    # Ensure value is timezone-aware for safe comparison
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return now - value > timedelta(hours=hours)

@router.get("/weather", response_model=list[WeatherResponse])
async def get_weather(session: AsyncSession = Depends(get_db)):
    cached = cache_store.get("weather")
    if cached is not None:
        return cached

    today = date.today()
    current = await session.scalar(select(WeatherCache).where(WeatherCache.date == today).limit(1))
    if not current or _is_stale(current.fetched_at, 3):
        await fetch_weather(session)
        await session.commit()
    result = await session.execute(select(WeatherCache).order_by(WeatherCache.date.desc()).limit(1))
    data = result.scalars().all()
    
    serialized = [WeatherResponse.model_validate(item) for item in data]
    cache_store.set("weather", serialized, 300) # 5 dk
    return serialized

@router.get("/prayers", response_model=list[PrayerTimesResponse])
async def get_prayers(session: AsyncSession = Depends(get_db)):
    cached = cache_store.get("prayers")
    if cached is not None:
        return cached

    today = date.today()
    current = await session.scalar(select(PrayerTimesCache).where(PrayerTimesCache.date == today).limit(1))
    if not current:
        await fetch_prayer_times(session)
        await session.commit()
    result = await session.execute(select(PrayerTimesCache).order_by(PrayerTimesCache.date.desc()).limit(1))
    data = result.scalars().all()

    serialized = [PrayerTimesResponse.model_validate(item) for item in data]
    cache_store.set("prayers", serialized, 300) # 5 dk
    return serialized

@router.get("/fuel", response_model=list[FuelPricesResponse])
async def get_fuel(session: AsyncSession = Depends(get_db)):
    cached = cache_store.get("fuel")
    if cached is not None:
        return cached

    latest = await session.scalar(select(FuelPricesCache).order_by(FuelPricesCache.fetched_at.desc()).limit(1))
    if not latest or _is_stale(latest.fetched_at, 6):
        await fetch_fuel_prices(session)
        await session.commit()
    result = await session.execute(select(FuelPricesCache).order_by(FuelPricesCache.fetched_at.desc()).limit(1))
    data = result.scalars().all()

    serialized = [FuelPricesResponse.model_validate(item) for item in data]
    cache_store.set("fuel", serialized, 300) # 5 dk
    return serialized

@router.get("/currency", response_model=list[CurrencyResponse])
async def get_currency(session: AsyncSession = Depends(get_db)):
    cached = cache_store.get("currency")
    if cached is not None:
        return cached

    latest = await session.scalar(select(CurrencyCache).order_by(CurrencyCache.fetched_at.desc()).limit(1))
    count = await session.scalar(select(func.count(CurrencyCache.id)))
    if not count or not latest or _is_stale(latest.fetched_at, 6):
        await fetch_currency(session)
        await session.commit()
    result = await session.execute(select(CurrencyCache))
    data = result.scalars().all()

    serialized = [CurrencyResponse.model_validate(item) for item in data]
    cache_store.set("currency", serialized, 300) # 5 dk
    return serialized

@router.get("/gold", response_model=list[GoldResponse])
async def get_gold(session: AsyncSession = Depends(get_db)):
    cached = cache_store.get("gold")
    if cached is not None:
        return cached

    latest = await session.scalar(select(GoldCache).order_by(GoldCache.fetched_at.desc()).limit(1))
    count = await session.scalar(select(func.count(GoldCache.id)))
    if not count or not latest or _is_stale(latest.fetched_at, 6):
        await fetch_gold(session)
        await session.commit()
    result = await session.execute(select(GoldCache))
    data = result.scalars().all()

    serialized = [GoldResponse.model_validate(item) for item in data]
    cache_store.set("gold", serialized, 300) # 5 dk
    return serialized

@router.get("/earthquakes", response_model=list[EarthquakeResponse])
async def get_earthquakes(session: AsyncSession = Depends(get_db)):
    cached = cache_store.get("earthquakes")
    if cached is not None:
        return cached

    result = await session.execute(select(EarthquakesCache).order_by(EarthquakesCache.event_date.desc()).limit(20))
    data = result.scalars().all()

    serialized = [EarthquakeResponse.model_validate(item) for item in data]
    cache_store.set("earthquakes", serialized, 60) # 1 dk (depremler daha sık güncellenebilir)
    return serialized
