"""Eczane API Endpoint'leri."""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.places import Pharmacy
from app.schemas.places import PharmacyResponse

router = APIRouter()

@router.get("/duty", response_model=list[PharmacyResponse])
async def get_duty_pharmacies(session: AsyncSession = Depends(get_db)):
    """Sadece bugünün nöbetçi eczanelerini getirir."""
    today = date.today()
    stmt = select(Pharmacy).where(Pharmacy.duty_date == today)
    result = await session.execute(stmt)
    pharmacies = result.scalars().all()
    
    if not pharmacies:
        # Eğer bugünün verisi yoksa en son kayıtlı günü dönmeyi deneyebiliriz.
        # Basitlik için şu an hata dönmüyoruz, boş liste dönebilir.
        pass
        
    return pharmacies
