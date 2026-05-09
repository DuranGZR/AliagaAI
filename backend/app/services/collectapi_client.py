"""
AliagaAI - CollectAPI istemcisi.

6 servis: Eczane, Hava Durumu, Namaz, Akaryakit, Doviz, Altin.
Her servis icin veri ceker ve ilgili cache tablosuna upsert eder.
"""
from datetime import date
import re
import unicodedata

import httpx
from bs4 import BeautifulSoup
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
PETROL_OFISI_IZMIR_URL = "https://www.petrolofisi.com.tr/akaryakit-fiyatlari/izmir-akaryakit-fiyatlari"
IZMIR_OPENAPI_PHARMACIES_URL = "https://openapi.izmir.bel.tr/api/ibb/eczaneler"


def _headers() -> dict:
    return {
        "authorization": settings.COLLECTAPI_KEY,
        "content-type": "application/json",
    }


async def _get(path: str, params: dict | None = None) -> dict | None:
    """CollectAPI'ye GET istegi atar, sonucu JSON olarak doner."""
    url = f"{BASE_URL}{path}"
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(url, headers=_headers(), params=params)
            resp.raise_for_status()
            data = resp.json()

            if isinstance(data, list):
                return {"success": True, "result": data}

            if isinstance(data, dict) and "success" in data and not data.get("success"):
                logger.warning(f"CollectAPI basarisiz yanit: {path} -> {data}")
                return None
            return data
    except httpx.HTTPError as e:
        logger.error(f"CollectAPI HTTP hatasi: {path} -> {e}")
        return None
    except Exception as e:
        logger.error(f"CollectAPI genel hata: {path} -> {e}")
        return None


async def fetch_pharmacies(session: AsyncSession) -> int:
    """Aliaga nobetci eczanelerini ceker ve pharmacies tablosuna yazar."""
    data = await _get("/health/dutyPharmacy", {"il": "Izmir", "ilce": "Aliaga"})

    today = date.today()
    await session.execute(delete(Pharmacy).where(Pharmacy.duty_date == today))

    pharmacy_rows: list[dict] = []

    if data:
        for item in data.get("result", []):
            lat, lon = None, None
            loc = item.get("loc")
            if loc and "," in loc:
                parts = loc.split(",")
                try:
                    lat, lon = float(parts[0].strip()), float(parts[1].strip())
                except (ValueError, IndexError):
                    pass

            pharmacy_rows.append(
                {
                    "name": item.get("name", ""),
                    "address": item.get("address"),
                    "phone": item.get("phone"),
                    "latitude": lat,
                    "longitude": lon,
                    "duty_date": today,
                    "district": item.get("dist", "Aliaga"),
                }
            )

    # CollectAPI bazen 0 kayit dondurebiliyor; bu durumda Izmir acik veri API fallback'i
    if not pharmacy_rows:
        pharmacy_rows = await _fetch_pharmacies_from_izmir_openapi(today=today)
        if pharmacy_rows:
            logger.info("Eczane verisi Izmir Acik Veri API fallback kaynagindan alindi.")

    if not pharmacy_rows:
        logger.warning("Eczane verisi alinamadi (CollectAPI + Izmir OpenAPI fallback).")
        return 0

    count = 0
    for row in pharmacy_rows:
        pharmacy = Pharmacy(**row)
        session.add(pharmacy)
        count += 1

    await session.flush()
    logger.info(f"Eczane: {count} nobetci eczane guncellendi.")
    return count


def _norm_tr(text: str | None) -> str:
    raw = str(text or "").strip().lower()
    raw = (
        raw.replace("ı", "i")
        .replace("ş", "s")
        .replace("ğ", "g")
        .replace("ü", "u")
        .replace("ö", "o")
        .replace("ç", "c")
    )
    return "".join(ch for ch in unicodedata.normalize("NFKD", raw) if not unicodedata.combining(ch))


async def _fetch_pharmacies_from_izmir_openapi(today: date) -> list[dict]:
    """
    CollectAPI yoksa/boşsa İzmir Açık Veri eczane listesinden Aliağa kayıtlarını döndürür.
    Not: Bu kaynak "nöbetçi" değil, ilçe eczane listesi olduğundan duty_date=today ile işlenir.
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(IZMIR_OPENAPI_PHARMACIES_URL)
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.warning(f"Izmir Acik Veri eczane fallback hatasi: {e}")
        return []

    if not isinstance(data, list):
        return []

    rows: list[dict] = []
    for item in data:
        region = _norm_tr(item.get("Bolge"))
        if "aliaga" not in region:
            continue

        rows.append(
            {
                "name": str(item.get("Adi") or "").strip(),
                "address": str(item.get("Adres") or "").strip() or None,
                "phone": str(item.get("Telefon") or "").strip() or None,
                "latitude": _safe_float(item.get("LokasyonX")),
                "longitude": _safe_float(item.get("LokasyonY")),
                "duty_date": today,
                "district": "Aliağa",
            }
        )

    # (name, address) bazında tekrarları temizle
    unique: dict[tuple[str, str], dict] = {}
    for row in rows:
        key = ((row.get("name") or "").lower(), (row.get("address") or "").lower())
        if key == ("", ""):
            continue
        unique[key] = row

    return list(unique.values())


async def fetch_weather(session: AsyncSession) -> int:
    """Izmir hava durumu verisini ceker ve cache'e yazar."""
    data = await _get("/weather/getWeather", {"city": "izmir", "lang": "tr"})
    if not data:
        return 0

    results = data.get("result", [])
    if not results:
        return 0

    today = date.today()
    await session.execute(delete(WeatherCache).where(WeatherCache.date == today))

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
    logger.info("Hava durumu guncellendi.")
    return 1


async def fetch_prayer_times(session: AsyncSession) -> int:
    """Izmir namaz vakitlerini ceker ve cache'e yazar."""
    data = await _get("/pray/all", {"city": "izmir"})
    if not data:
        return 0

    results = data.get("result", [])
    if not results:
        return 0

    today = date.today()
    await session.execute(delete(PrayerTimesCache).where(PrayerTimesCache.date == today))

    first = results[0]
    times_data = first.get("times", [])
    time_names = ["fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"]
    time_values = {}
    for i, name in enumerate(time_names):
        time_values[name] = times_data[i] if i < len(times_data) else None

    prayer = PrayerTimesCache(city="izmir", date=today, **time_values)
    session.add(prayer)
    await session.flush()
    logger.info("Namaz vakitleri guncellendi.")
    return 1


def _safe_float(val) -> float | None:
    """Degeri guvenli sekilde float'a cevirir."""
    if val is None:
        return None
    try:
        if isinstance(val, str):
            val = val.replace(",", ".").strip()
        return float(val)
    except (ValueError, TypeError):
        return None


def _extract_first_number(value: str | None) -> float | None:
    if not value:
        return None
    match = re.search(r"(\d+[.,]\d+|\d+)", value)
    if not match:
        return None
    return _safe_float(match.group(1))


async def _fetch_fuel_prices_from_petro_ofisi() -> tuple[float | None, float | None, float | None]:
    """
    CollectAPI kapaliysa Petrol Ofisi Izmir ilce sayfasindan ALIAGA satirini parse eder.
    Donus: (gasoline, diesel, lpg)
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True, verify=False) as client:
            resp = await client.get(PETROL_OFISI_IZMIR_URL)
            resp.raise_for_status()
    except Exception as e:
        logger.warning(f"Petrol Ofisi fallback erisim hatasi: {e}")
        return None, None, None

    soup = BeautifulSoup(resp.text, "lxml")
    table = soup.select_one("table")
    if not table:
        logger.warning("Petrol Ofisi fallback: fiyat tablosu bulunamadi.")
        return None, None, None

    target_row: list[str] | None = None
    for row in table.select("tr"):
        cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])]
        if not cells:
            continue
        city = cells[0].upper()
        if city in {"ALIAGA", "ALİAĞA"}:
            target_row = cells
            break

    if not target_row:
        for row in table.select("tr"):
            cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])]
            if cells and cells[0].upper() == "IZMIR":
                target_row = cells
                break

    if not target_row or len(target_row) < 7:
        logger.warning("Petrol Ofisi fallback: ALIAGA/IZMIR satiri parse edilemedi.")
        return None, None, None

    gasoline = _extract_first_number(target_row[1])
    diesel = _extract_first_number(target_row[2])
    lpg = _extract_first_number(target_row[6])
    return gasoline, diesel, lpg


async def fetch_fuel_prices(session: AsyncSession) -> int:
    """Akaryakit fiyatlarini ceker."""
    gasoline = diesel = lpg = None

    data = await _get("/gasPrice/allGasPrice")
    if data:
        results = data.get("result", [])
        for item in results:
            if "izmir" in (item.get("city") or "").lower():
                gasoline = _safe_float(item.get("gasoline"))
                diesel = _safe_float(item.get("diesel"))
                lpg = _safe_float(item.get("lpg"))
                break

        if gasoline is None and results:
            first = results[0]
            gasoline = _safe_float(first.get("gasoline"))
            diesel = _safe_float(first.get("diesel"))
            lpg = _safe_float(first.get("lpg"))

    if gasoline is None and diesel is None and lpg is None:
        gasoline, diesel, lpg = await _fetch_fuel_prices_from_petro_ofisi()
        if gasoline is not None or diesel is not None or lpg is not None:
            logger.info("Akaryakit verisi Petrol Ofisi fallback kaynagindan alindi.")

    if gasoline is None and diesel is None and lpg is None:
        logger.warning("Akaryakit verisi alinamadi (CollectAPI + fallback basarisiz).")
        return 0

    await session.execute(delete(FuelPricesCache))
    fuel = FuelPricesCache(city="izmir", gasoline=gasoline, diesel=diesel, lpg=lpg)
    session.add(fuel)
    await session.flush()
    logger.info("Akaryakit fiyatlari guncellendi.")
    return 1


async def fetch_currency(session: AsyncSession) -> int:
    """Doviz kurlarini ceker."""
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
    logger.info(f"Doviz kurlari: {count} para birimi guncellendi.")
    return count


async def fetch_gold(session: AsyncSession) -> int:
    """Altin fiyatlarini ceker."""
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
    logger.info(f"Altin fiyatlari: {count} tur guncellendi.")
    return count


async def fetch_all(session: AsyncSession) -> dict[str, int]:
    """Tum CollectAPI verilerini tek seferde ceker."""
    results = {}
    results["pharmacies"] = await fetch_pharmacies(session)
    results["weather"] = await fetch_weather(session)
    results["prayer_times"] = await fetch_prayer_times(session)
    results["fuel_prices"] = await fetch_fuel_prices(session)
    results["currency"] = await fetch_currency(session)
    results["gold"] = await fetch_gold(session)
    await session.commit()
    logger.success(f"CollectAPI toplu guncelleme tamamlandi: {results}")
    return results
