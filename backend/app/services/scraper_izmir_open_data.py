from __future__ import annotations

import csv
import io
import unicodedata

import httpx
from loguru import logger
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.city import StreetMarket, TaxiStand

TAXI_CSV_URL = "https://openfiles.izmir.bel.tr/100104/docs/izbb-taksi-durak-bilgileri.csv"
MARKETS_CSV_URL = "https://acikveri.bizizmir.com/dataset/919d327a-9023-42b4-989c-124945bff7f0/resource/3e63e16e-74a9-40f6-8ad3-043ad4fa4a16/download/izbb-semt-pazar-yerleri.csv"
TIMEOUT = 25


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


def _safe_float(value) -> float | None:
    if value is None:
        return None
    text = str(value).strip().replace(",", ".")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _to_reader(csv_text: str) -> csv.DictReader:
    reader = csv.DictReader(io.StringIO(csv_text), delimiter=";")
    if reader.fieldnames:
        reader.fieldnames = [(name or "").lstrip("\ufeff").strip() for name in reader.fieldnames]
    return reader


def _extract_market_day(text: str | None) -> str:
    norm = _norm_tr(text)
    mapping = [
        ("pazartesi", "pazartesi"),
        ("cumartesi", "cumartesi"),
        ("carsamba", "carsamba"),
        ("persembe", "persembe"),
        ("sali", "sali"),
        ("cuma", "cuma"),
        ("pazar", "pazar"),
    ]
    for key, value in mapping:
        if key in norm:
            return value
    return "belirsiz"


async def _download_text(url: str) -> str:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        return resp.text


async def sync_taxi_stands(session: AsyncSession) -> int:
    """İzmir Açık Veri CSV kaynağından Aliağa taksi duraklarını senkronize eder."""
    csv_text = await _download_text(TAXI_CSV_URL)
    rows = _to_reader(csv_text)

    parsed: list[dict] = []
    for row in rows:
        if _norm_tr(row.get("ILCE")) != "aliaga":
            continue

        name = (row.get("ADI") or "").strip()
        if len(name) < 2:
            continue

        road = (row.get("YOL") or "").strip()
        no = (row.get("KAPINO") or "").strip()
        neighborhood = (row.get("MAHALLE") or "").strip()
        address_bits = [x for x in [road, no, neighborhood, "Aliağa"] if x]
        address = ", ".join(address_bits)[:900] if address_bits else None

        parsed.append(
            {
                "name": name[:255],
                "phone": None,
                "address": address,
                "latitude": _safe_float(row.get("ENLEM")),
                "longitude": _safe_float(row.get("BOYLAM")),
                "is_24h": True,
            }
        )

    unique: dict[tuple[str, str], dict] = {}
    for item in parsed:
        key = ((item.get("name") or "").lower(), (item.get("address") or "").lower())
        unique[key] = item

    await session.execute(delete(TaxiStand))
    for item in unique.values():
        session.add(TaxiStand(**item))
    await session.flush()

    count = len(unique)
    logger.info(f"OpenData taxi senkronizasyonu: {count} Aliağa kaydı.")
    return count


async def sync_street_markets(session: AsyncSession) -> int:
    """İzmir Açık Veri CSV kaynağından Aliağa semt pazarlarını senkronize eder."""
    csv_text = await _download_text(MARKETS_CSV_URL)
    rows = _to_reader(csv_text)

    parsed: list[dict] = []
    for row in rows:
        if _norm_tr(row.get("ILCE")) != "aliaga":
            continue

        name = (row.get("ADI") or "").strip()
        if len(name) < 2:
            continue

        neighborhood = (row.get("MAHALLE") or "").strip() or None
        road = (row.get("YOL") or "").strip()
        no = (row.get("KAPINO") or "").strip()
        address_bits = [x for x in [road, no, neighborhood, "Aliağa"] if x]
        address = ", ".join(address_bits)[:900] if address_bits else None
        note = (row.get("ACIKLAMA") or "").strip()

        parsed.append(
            {
                "name": name[:255],
                "day_of_week": _extract_market_day(note),
                "neighborhood": neighborhood[:100] if neighborhood else None,
                "address": address,
                "description": note[:1000] if note else None,
            }
        )

    unique: dict[str, dict] = {}
    for item in parsed:
        key = (item.get("name") or "").lower()
        unique[key] = item

    await session.execute(delete(StreetMarket))
    for item in unique.values():
        session.add(StreetMarket(**item))
    await session.flush()

    count = len(unique)
    logger.info(f"OpenData semt pazari senkronizasyonu: {count} Aliağa kaydı.")
    return count


async def sync_open_data_city_tables(session: AsyncSession) -> dict[str, int]:
    """Aliağa için şehir tablolarını İzmir Açık Veri kaynaklarından günceller."""
    taxi_count = await sync_taxi_stands(session)
    market_count = await sync_street_markets(session)
    return {"taxi_stands": taxi_count, "street_markets": market_count}
