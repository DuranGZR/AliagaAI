"""Eczane API Endpoint'leri."""
from datetime import date
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.places import Pharmacy
from app.schemas.places import PharmacyResponse
from app.services.collectapi_client import fetch_pharmacies
from app.core.limiter import limiter
from app.utils.cache import cache_store

router = APIRouter()

@router.get("/duty", response_model=list[PharmacyResponse])
@limiter.limit("30/minute")
async def get_duty_pharmacies(request: Request, session: AsyncSession = Depends(get_db)):
    """Sadece bugünün nöbetçi eczanelerini getirir."""
    cached = cache_store.get("duty_pharmacies")
    if cached is not None:
        return cached

    today = date.today()
    stmt = select(Pharmacy).where(Pharmacy.duty_date == today).order_by(Pharmacy.name.asc())
    result = await session.execute(stmt)
    pharmacies = result.scalars().all()

    if not pharmacies:
        await fetch_pharmacies(session)
        await session.commit()
        result = await session.execute(stmt)
        pharmacies = result.scalars().all()
    
    if not pharmacies:
        # Eğer bugünün verisi yoksa en son kayıtlı günü dönmeyi deneyebiliriz.
        # Basitlik için şu an hata dönmüyoruz, boş liste dönebilir.
        latest_date = await session.scalar(select(Pharmacy.duty_date).order_by(Pharmacy.duty_date.desc()).limit(1))
        if latest_date:
            result = await session.execute(
                select(Pharmacy)
                .where(Pharmacy.duty_date == latest_date)
                .order_by(Pharmacy.name.asc())
            )
            pharmacies = result.scalars().all()
        
    # Deduplicate pharmacies by name and address to prevent duplicate records
    seen = set()
    deduped = []
    for item in pharmacies:
        norm_name = "".join((item.name or "").split()).lower()
        norm_addr = "".join((item.address or "").split()).lower()
        key = (norm_name, norm_addr)
        if key not in seen:
            seen.add(key)
            deduped.append(item)
    pharmacies = deduped

    serialized = [PharmacyResponse.model_validate(item) for item in pharmacies]
    cache_store.set("duty_pharmacies", serialized, 300) # 5 dk
    return serialized
