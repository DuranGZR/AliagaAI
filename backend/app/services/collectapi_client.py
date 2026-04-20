"""
AliağaAI — CollectAPI istemcisi.

6 servis: Eczane, Hava Durumu, Namaz, Akaryakıt, Döviz, Altın.
Her servis için veri çeker ve ilgili cache tablosuna upsert eder.
"""
from datetime import date, datetime

import httpx
from loguru import logger
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.cache import (
    CurrencyCache,
    FuelPricesCache,
    GoldCache,
    PrayerTimesCache,
    WeatherCache,
)
from app.models.places import Pharmacy

BASE_URL = "https://api.collectapi.com"
TIMEOUT = 15


def _headers() -> dict:
    return {
        "authorization": settings.COLLECTAPI_KEY,
        "content-type": "application/json",
    }


async def _get(path: str, params: dict | None = None) -> dict | None:
    """CollectAPI'ye GET isteği atar, sonucu JSON olarak döner."""
    url = f"{BASE_URL}{path}"
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(url, headers=_headers(), params=params)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("success"):
                logger.warning(f"CollectAPI başarısız yanıt: {path} → {data}")
                return None
            return data
    except httpx.HTTPError as e:
        logger.error(f"CollectAPI HTTP hatası: {path} → {e}")
        return None
    except Exception as e:
        logger.error(f"CollectAPI genel hata: {path} → {e}")
        return None


# ─── ECZANE ───────────────────────────────────────
async def fetch_pharmacies(session: AsyncSession) -> int:
    """Aliağa nöbetçi eczanelerini çeker ve pharmacies tablosuna yazar."""
    data = await _get("/health/dutyPharmacy", {"il": "İzmir", "ilce": "Aliağa"})
    if not data:
        return 0

    today = date.today()
    # Bugünkü eczaneleri sil, yenilerini ekle
    await session.execute(
        delete(Pharmacy).where(Pharmacy.duty_date == today)
    )

    count = 0
    for item in data.get("result", []):
        lat, lon = None, None
        loc = item.get("loc")
        if loc and "," in loc:
            parts = loc.split(",")
            try:
                lat, lon = float(parts[0].strip()), float(parts[1].strip())
            except (ValueError, IndexError):
                pass

        pharmacy = Pharmacy(
            name=item.get("name", ""),
            address=item.get("address"),
            phone=item.get("phone"),
            latitude=lat,
            longitude=lon,
            duty_date=today,
            district=item.get("dist", "Aliağa"),
        )
        session.add(pharmacy)
        count += 1

    await session.flush()
    logger.info(f"Eczane: {count} nöbetçi eczane güncellendi.")
    return count


# ─── HAVA DURUMU ──────────────────────────────────
async def fetch_weather(session: AsyncSession) -> int:
    """İzmir hava durumu verisini çeker ve cache'e yazar."""
    data = await _get("/weather/getWeather", {"city": "izmir", "lang": "tr"})
    if not data:
        return 0

    results = data.get("result", [])
    if not results:
        return 0

    today = date.today()
    await session.execute(
        delete(WeatherCache).where(WeatherCache.date == today)
    )

    first = results[0]
    weather = WeatherCache(
        city="izmir",
        date=today,
        temperature=_safe_float(first.get("degree")),
        description=first.get("description"),
        icon=first.get("icon"),
        humidity=first.get("humidity"),
        wind=first.get("wind"),
        min_temp=_safe_float(first.get("min")),
        max_temp=_safe_float(first.get("max")),
        forecast_json={"days": results},
    )
    session.add(weather)
    await session.flush()
    logger.info("Hava durumu güncellendi.")
    return 1


# ─── NAMAZ VAKİTLERİ ─────────────────────────────
async def fetch_prayer_times(session: AsyncSession) -> int:
    """İzmir namaz vakitlerini çeker ve cache'e yazar."""
    data = await _get("/pray/all", {"city": "izmir"})
    if not data:
        return 0

    results = data.get("result", [])
    if not results:
        return 0

    today = date.today()
    await session.execute(
        delete(PrayerTimesCache).where(PrayerTimesCache.date == today)
    )

    first = results[0]
    times_data = first.get("times", [])
    time_names = ["fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"]
    time_values = {}
    for i, name in enumerate(time_names):
        time_values[name] = times_data[i] if i < len(times_data) else None

    prayer = PrayerTimesCache(
        city="izmir",
        date=today,
        **time_values,
    )
    session.add(prayer)
    await session.flush()
    logger.info("Namaz vakitleri güncellendi.")
    return 1


# ─── AKARYAKIT ────────────────────────────────────
async def fetch_fuel_prices(session: AsyncSession) -> int:
    """Akaryakıt fiyatlarını çeker."""
    data = await _get("/gasPrice/allGasPrice")
    if not data:
        return 0

    results = data.get("result", [])
    if not results:
        return 0

    # Tüm eski verileri sil
    await session.execute(delete(FuelPricesCache))

    # İzmir verisini bul
    gasoline, diesel, lpg = None, None, None
    for item in results:
        if "izmir" in (item.get("city") or "").lower():
            gasoline = _safe_float(item.get("gasoline"))
            diesel = _safe_float(item.get("diesel"))
            lpg = _safe_float(item.get("lpg"))
            break

    if gasoline is None:
        # İlk veriyi al
        first = results[0]
        gasoline = _safe_float(first.get("gasoline"))
        diesel = _safe_float(first.get("diesel"))
        lpg = _safe_float(first.get("lpg"))

    fuel = FuelPricesCache(city="izmir", gasoline=gasoline, diesel=diesel, lpg=lpg)
    session.add(fuel)
    await session.flush()
    logger.info("Akaryakıt fiyatları güncellendi.")
    return 1


# ─── DÖVİZ ───────────────────────────────────────
async def fetch_currency(session: AsyncSession) -> int:
    """Döviz kurlarını çeker."""
    data = await _get("/economy/allCurrency")
    if not data:
        return 0

    results = data.get("result", [])
    if not results:
        return 0

    await session.execute(delete(CurrencyCache))

    count = 0
    target_codes = {"USD", "EUR", "GBP", "CHF", "JPY", "SAR", "CAD", "AUD"}
    for item in results:
        code = (item.get("code") or "").upper()
        if code not in target_codes:
            continue
        currency = CurrencyCache(
            code=code,
            name=item.get("name"),
            buying=_safe_float(item.get("buying")),
            selling=_safe_float(item.get("selling")),
            change_pct=_safe_float(item.get("rate")),
        )
        session.add(currency)
        count += 1

    await session.flush()
    logger.info(f"Döviz kurları: {count} para birimi güncellendi.")
    return count


# ─── ALTIN ────────────────────────────────────────
async def fetch_gold(session: AsyncSession) -> int:
    """Altın fiyatlarını çeker."""
    data = await _get("/economy/goldPrice")
    if not data:
        return 0

    results = data.get("result", [])
    if not results:
        return 0

    await session.execute(delete(GoldCache))

    count = 0
    for item in results:
        gold = GoldCache(
            name=item.get("name", ""),
            buying=_safe_float(item.get("buying")),
            selling=_safe_float(item.get("selling")),
            change_pct=_safe_float(item.get("rate")),
        )
        session.add(gold)
        count += 1

    await session.flush()
    logger.info(f"Altın fiyatları: {count} tür güncellendi.")
    return count


# ─── YARDIMCI ────────────────────────────────────
def _safe_float(val) -> float | None:
    """Değeri güvenli şekilde float'a çevirir."""
    if val is None:
        return None
    try:
        # Türkçe format — virgüllü sayılar
        if isinstance(val, str):
            val = val.replace(",", ".").strip()
        return float(val)
    except (ValueError, TypeError):
        return None


# ─── TOPLU GÜNCELLEME ────────────────────────────
async def fetch_all(session: AsyncSession) -> dict[str, int]:
    """Tüm CollectAPI verilerini tek seferde çeker."""
    results = {}
    results["pharmacies"] = await fetch_pharmacies(session)
    results["weather"] = await fetch_weather(session)
    results["prayer_times"] = await fetch_prayer_times(session)
    results["fuel_prices"] = await fetch_fuel_prices(session)
    results["currency"] = await fetch_currency(session)
    results["gold"] = await fetch_gold(session)
    await session.commit()
    logger.success(f"CollectAPI toplu güncelleme tamamlandı: {results}")
    return results
