"""
AliağaAI — Deprem verisi istemcisi.

Kandilli Rasathanesi / AFAD API'sinden son deprem verilerini çeker.
"""
from datetime import datetime

import httpx
from loguru import logger
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cache import EarthquakesCache

# Açık kaynak deprem API'si
EARTHQUAKE_API = "https://api.orhanaydogdu.com.tr/deprem/kandilli/live"
TIMEOUT = 15


async def fetch_earthquakes(session: AsyncSession, limit: int = 30) -> int:
    """Son depremleri çeker ve earthquakes_cache tablosuna yazar."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(EARTHQUAKE_API, params={"limit": limit})
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as e:
        logger.error(f"Deprem API HTTP hatası: {e}")
        return 0
    except Exception as e:
        logger.error(f"Deprem API genel hata: {e}")
        return 0

    results = data.get("result", [])
    if not results:
        logger.warning("Deprem API boş sonuç döndü.")
        return 0

    # Önce yeni kayıtları ekle (flush ile görünür yap), sonra eski kayıtları temizle.
    # Bu sayede concurrent okuyucular hiçbir zaman boş sonuç görmez.
    count = 0
    for item in results:
        try:
            event_date = None
            date_str = item.get("date") or item.get("date_time")
            if date_str:
                try:
                    event_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass
            if event_date is None and item.get("created_at"):
                try:
                    event_date = datetime.fromtimestamp(float(item["created_at"]))
                except (ValueError, TypeError, OSError):
                    pass

            geojson = item.get("geojson", {})
            coordinates = geojson.get("coordinates", [None, None])
            lon = coordinates[0] if len(coordinates) > 0 else None
            lat = coordinates[1] if len(coordinates) > 1 else None

            earthquake = EarthquakesCache(
                magnitude=float(item.get("mag", 0)),
                location=item.get("title"),
                depth=_safe_float(item.get("depth")),
                latitude=lat,
                longitude=lon,
                event_date=event_date,
                source="kandilli",
            )
            session.add(earthquake)
            count += 1
        except (ValueError, TypeError) as e:
            logger.warning(f"Deprem verisi atlandı: {e}")
            continue

    # Önce yeni kayıtları flush'la, sonra eski kayıtları temizle
    await session.flush()
    # Eklenen kayıtların ID'lerini topla (flush sonrası ID atanır)
    new_ids = {obj.id for obj in session.new if isinstance(obj, EarthquakesCache)}
    if new_ids:
        await session.execute(
            delete(EarthquakesCache).where(EarthquakesCache.id.not_in(new_ids))
        )
    logger.info(f"Deprem: {count} kayıt güncellendi.")
    return count


def _safe_float(val) -> float | None:
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None
