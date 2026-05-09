from __future__ import annotations

import csv
import io
import json
import unicodedata
from datetime import date, datetime, time

import httpx
from loguru import logger
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.city import CityKnowledge, EmergencyContact, FerrySchedule, IzbanSchedule
from app.models.knowledge_layers import (
    DistrictStat,
    MunicipalService,
    PoiCatalog,
    TransportDeparture,
    TransportRoute,
    TransportStop,
)
from app.models.places import Institution, Place

ESHOT_LINES_CSV = "https://openfiles.izmir.bel.tr/211488/docs/eshot-otobus-hatlari.csv"
ESHOT_STOPS_CSV = "https://openfiles.izmir.bel.tr/211488/docs/eshot-otobus-duraklari.csv"
ESHOT_TIMES_CSV = "https://openfiles.izmir.bel.tr/211488/docs/eshot-otobus-hareketsaatleri.csv"
IZBAN_STATIONS_JSON = "https://acikveri.bizizmir.com/dataset/e3854620-a776-47d4-a63c-9180fc1d4e9e/resource/0187172e-45e1-465f-bb0c-1c4f2c75eed3/download/izban-istasyonlar.json"
POP_2023_CSV = "https://acikveri.bizizmir.com/dataset/133f2cf5-4202-4da7-97cc-7fbfd6365abe/resource/5b0761ce-e97d-4f0d-bcbe-99ff6b8afc91/download/cinsiyete-gore-mahalle-nufuslari.csv"
POP_2022_CSV = "https://acikveri.bizizmir.com/dataset/133f2cf5-4202-4da7-97cc-7fbfd6365abe/resource/52e06fbb-6434-4fd8-bddb-ac9b7bff1e94/download/cinsiyete-gore-mahalle-nufuslari-2022.csv"
KNOWLEDGE_SYNC_LOCK_ID = 88427155


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


def _parse_time(value: str | None) -> time | None:
    text = str(value or "").strip()
    if not text or ":" not in text:
        return None
    try:
        hh, mm = text.split(":", 1)
        return time(int(hh), int(mm))
    except Exception:
        return None


def _is_aliaga_bbox(latitude: float | None, longitude: float | None) -> bool:
    if latitude is None or longitude is None:
        return False
    # Aliağa + yakın çevre (Yeni Şakran / Helvacı dahil) odaklı kabaca bounding box
    return 38.60 <= latitude <= 39.00 and 26.80 <= longitude <= 27.25


async def _download_text(url: str, timeout: int = 40) -> str:
    last_exc: Exception | None = None
    for attempt in range(1, 4):
        try:
            async with httpx.AsyncClient(timeout=timeout + (attempt - 1) * 20) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                resp.encoding = "utf-8"
                return resp.text
        except Exception as exc:
            last_exc = exc
            logger.warning(f"Kaynak indirilemedi (deneme {attempt}/3): {url} -> {exc}")
    raise RuntimeError(f"Kaynak 3 denemede indirilemedi: {url}") from last_exc


def _csv_reader(csv_text: str) -> csv.DictReader:
    reader = csv.DictReader(io.StringIO(csv_text), delimiter=";")
    if reader.fieldnames:
        reader.fieldnames = [(f or "").lstrip("\ufeff").strip() for f in reader.fieldnames]
    return reader


def _is_aliaga_related_line(name: str) -> bool:
    n = _norm_tr(name)
    hints = [
        "aliaga",
        "yenisakran",
        "yeni sakran",
        "helvaci",
        "samurlu",
        "foca",
        "bicerova",
        "dikili-aliaga",
        "kinik - aliaga",
    ]
    return any(h in n for h in hints)


async def sync_transport_layers(session: AsyncSession, batch_id: str, verified_at: date) -> dict[str, int]:
    # Hard reset with stable IDs for deterministic and incremental-friendly indexing.
    await session.execute(
        text("TRUNCATE TABLE transport_departures, transport_stops, transport_routes RESTART IDENTITY")
    )

    route_count = 0
    stop_count = 0
    departure_count = 0

    route_ids_by_key: dict[str, int] = {}
    eshot_hat_numbers: set[str] = set()

    # ESHOT routes
    lines_text = await _download_text(ESHOT_LINES_CSV)
    for row in _csv_reader(lines_text):
        hat_no = str(row.get("HAT_NO") or "").strip()
        hat_adi = str(row.get("HAT_ADI") or "").strip()
        if not hat_no or not hat_adi:
            continue
        if not _is_aliaga_related_line(hat_adi):
            continue

        guzergah = " | ".join(
            x
            for x in [
                hat_adi,
                str(row.get("GUZERGAH_ACIKLAMA") or "").strip(),
                f"{row.get('HAT_BASLANGIC') or ''} -> {row.get('HAT_BITIS') or ''}".strip(),
            ]
            if x
        )
        model = TransportRoute(
            mode="eshot",
            hat_no=hat_no,
            guzergah=guzergah[:1500],
            source_url=ESHOT_LINES_CSV,
            last_verified_at=verified_at,
            quality_score=0.84,
            ingestion_batch_id=batch_id,
        )
        session.add(model)
        await session.flush()
        route_ids_by_key[f"eshot:{hat_no}"] = model.id
        eshot_hat_numbers.add(hat_no)
        route_count += 1

    # IZBAN route
    izban_route = TransportRoute(
        mode="izban",
        hat_no="IZBAN",
        guzergah="Aliağa - İzmir Banliyö Ana Hattı",
        source_url=IZBAN_STATIONS_JSON,
        last_verified_at=verified_at,
        quality_score=0.8,
        ingestion_batch_id=batch_id,
    )
    session.add(izban_route)
    await session.flush()
    route_ids_by_key["izban:main"] = izban_route.id
    route_count += 1

    # Vapur routes from existing ferry table
    ferries = (await session.execute(select(FerrySchedule))).scalars().all()
    for ferry in ferries:
        route = TransportRoute(
            mode="vapur",
            hat_no=None,
            guzergah=(ferry.route or "Aliağa Deniz Hattı")[:1500],
            source_url="https://acikveri.bizizmir.com/tr/dataset/vapur-hareket-saatleri",
            last_verified_at=verified_at,
            quality_score=0.7,
            ingestion_batch_id=batch_id,
        )
        session.add(route)
        await session.flush()
        route_ids_by_key[f"vapur:{ferry.id}"] = route.id
        route_count += 1

    # ESHOT stops associated with Aliağa related hat numbers
    stops_text = await _download_text(ESHOT_STOPS_CSV)
    unique_stops: dict[str, TransportStop] = {}
    for row in _csv_reader(stops_text):
        raw_lines = str(row.get("DURAKTAN_GECEN_HATLAR") or "").strip()
        if not raw_lines:
            continue
        line_tokens = {tok.strip() for tok in raw_lines.split("-") if tok.strip()}
        if not (line_tokens & eshot_hat_numbers):
            continue

        stop_id = str(row.get("DURAK_ID") or "").strip()
        stop_name = str(row.get("DURAK_ADI") or "").strip()
        if not stop_id or not stop_name:
            continue

        key = f"eshot:{stop_id}"
        lat = _safe_float(row.get("ENLEM"))
        lon = _safe_float(row.get("BOYLAM"))
        if not _is_aliaga_bbox(lat, lon):
            continue

        unique_stops[key] = TransportStop(
            stop_id=stop_id,
            ad=stop_name[:255],
            ilce="İzmir",
            mahalle=None,
            latitude=lat,
            longitude=lon,
            mode="eshot",
            source_url=ESHOT_STOPS_CSV,
            last_verified_at=verified_at,
            quality_score=0.8,
            ingestion_batch_id=batch_id,
        )

    # IZBAN stations
    izban_text = await _download_text(IZBAN_STATIONS_JSON)
    izban_rows = json.loads(izban_text)
    for row in izban_rows:
        station_id = str(row.get("IstasyonId") or "").strip()
        station_name = str(row.get("IstasyonAdi") or "").strip()
        if not station_id or not station_name:
            continue
        key = f"izban:{station_id}"
        unique_stops[key] = TransportStop(
            stop_id=station_id,
            ad=station_name[:255],
            ilce="İzmir",
            mahalle=None,
            latitude=_safe_float(row.get("Enlem")),
            longitude=_safe_float(row.get("Boylam")),
            mode="izban",
            source_url=IZBAN_STATIONS_JSON,
            last_verified_at=verified_at,
            quality_score=0.78,
            ingestion_batch_id=batch_id,
        )

    # Vapur terminals from ferry schedules
    for ferry in ferries:
        dep = (ferry.departure_port or "Aliaport").strip()
        arr = (ferry.arrival_port or "").strip()
        for idx, stop_name in enumerate([dep, arr], start=1):
            if not stop_name:
                continue
            key = f"vapur:{ferry.id}:{idx}"
            unique_stops[key] = TransportStop(
                stop_id=key,
                ad=stop_name[:255],
                ilce="Aliağa" if "alia" in _norm_tr(stop_name) else None,
                mahalle=None,
                latitude=None,
                longitude=None,
                mode="vapur",
                source_url="https://acikveri.bizizmir.com/tr/dataset/vapur-hareket-saatleri",
                last_verified_at=verified_at,
                quality_score=0.65,
                ingestion_batch_id=batch_id,
            )

    for item in unique_stops.values():
        session.add(item)
    await session.flush()
    stop_count = len(unique_stops)

    # ESHOT departures
    times_text = await _download_text(ESHOT_TIMES_CSV)
    for row in _csv_reader(times_text):
        hat_no = str(row.get("HAT_NO") or "").strip()
        if hat_no not in eshot_hat_numbers:
            continue

        route_id = route_ids_by_key.get(f"eshot:{hat_no}")
        tarife = str(row.get("TARIFE_ID") or "").strip()
        day_type = f"tarife_{tarife}" if tarife else None

        gidis = _parse_time(row.get("GIDIS_SAATI"))
        if gidis:
            session.add(
                TransportDeparture(
                    route_id=route_id,
                    stop_id=None,
                    zaman=gidis,
                    day_type=day_type,
                    realtime_flag=False,
                    source_url=ESHOT_TIMES_CSV,
                    last_verified_at=verified_at,
                    quality_score=0.78,
                    ingestion_batch_id=batch_id,
                )
            )
            departure_count += 1

        donus = _parse_time(row.get("DONUS_SAATI"))
        if donus:
            session.add(
                TransportDeparture(
                    route_id=route_id,
                    stop_id=None,
                    zaman=donus,
                    day_type=day_type,
                    realtime_flag=False,
                    source_url=ESHOT_TIMES_CSV,
                    last_verified_at=verified_at,
                    quality_score=0.78,
                    ingestion_batch_id=batch_id,
                )
            )
            departure_count += 1

    # IZBAN departures (existing schedule table)
    izban_rows = (await session.execute(select(IzbanSchedule))).scalars().all()
    aliaga_stop_id = None
    for stop in unique_stops.values():
        if stop.mode == "izban" and "aliaga" in _norm_tr(stop.ad):
            aliaga_stop_id = stop.stop_id
            break
    for row in izban_rows:
        if not row.departure_time:
            continue
        session.add(
            TransportDeparture(
                route_id=route_ids_by_key.get("izban:main"),
                stop_id=aliaga_stop_id,
                zaman=row.departure_time,
                day_type=row.day_type,
                realtime_flag=False,
                source_url=IZBAN_STATIONS_JSON,
                last_verified_at=verified_at,
                quality_score=0.74,
                ingestion_batch_id=batch_id,
            )
        )
        departure_count += 1

    # Vapur departures (existing ferry schedule table)
    for ferry in ferries:
        if not ferry.departure_time:
            continue
        session.add(
            TransportDeparture(
                route_id=route_ids_by_key.get(f"vapur:{ferry.id}"),
                stop_id=f"vapur:{ferry.id}:1",
                zaman=ferry.departure_time,
                day_type=ferry.day_type,
                realtime_flag=False,
                source_url="https://acikveri.bizizmir.com/tr/dataset/vapur-hareket-saatleri",
                last_verified_at=verified_at,
                quality_score=0.7,
                ingestion_batch_id=batch_id,
            )
        )
        departure_count += 1

    await session.flush()
    return {
        "transport_routes": route_count,
        "transport_stops": stop_count,
        "transport_departures": departure_count,
    }


async def sync_poi_catalog(session: AsyncSession, batch_id: str, verified_at: date) -> int:
    await session.execute(text("TRUNCATE TABLE poi_catalog RESTART IDENTITY"))
    count = 0

    places = (await session.execute(select(Place).where(Place.is_active.is_(True)))).scalars().all()
    for row in places:
        session.add(
            PoiCatalog(
                kategori=(row.category or "mekan")[:100],
                ad=row.name[:255],
                aciklama=(row.description or None),
                mahalle=None,
                latitude=row.latitude,
                longitude=row.longitude,
                resmi_url=row.website,
                source_url=row.website or "https://www.aliaga.bel.tr/",
                last_verified_at=verified_at,
                quality_score=0.76,
                ingestion_batch_id=batch_id,
            )
        )
        count += 1

    institutions = (await session.execute(select(Institution).where(Institution.is_active.is_(True)))).scalars().all()
    for row in institutions:
        session.add(
            PoiCatalog(
                kategori=f"kurum:{row.category or 'genel'}"[:100],
                ad=row.name[:255],
                aciklama=(row.description or None),
                mahalle=None,
                latitude=row.latitude,
                longitude=row.longitude,
                resmi_url=row.website,
                source_url=row.website or "https://www.aliaga.bel.tr/",
                last_verified_at=verified_at,
                quality_score=0.78,
                ingestion_batch_id=batch_id,
            )
        )
        count += 1

    city_rows = (
        await session.execute(
            select(CityKnowledge).where(CityKnowledge.layer.in_(["gezi", "gastronomi", "kurumlar"]))
        )
    ).scalars().all()
    for row in city_rows:
        session.add(
            PoiCatalog(
                kategori=f"city_knowledge:{row.layer}"[:100],
                ad=row.title[:255],
                aciklama=row.summary,
                mahalle=row.neighborhood,
                latitude=None,
                longitude=None,
                resmi_url=row.source_url,
                source_url=row.source_url,
                last_verified_at=row.last_verified_at,
                quality_score=0.72,
                ingestion_batch_id=batch_id,
            )
        )
        count += 1

    await session.flush()
    return count


def _working_hours_to_text(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, dict):
        parts = [f"{k}: {v}" for k, v in value.items()]
        return "; ".join(parts)[:255] if parts else None
    text = str(value).strip()
    return text[:255] if text else None


async def sync_municipal_services(session: AsyncSession, batch_id: str, verified_at: date) -> int:
    await session.execute(text("TRUNCATE TABLE municipal_services RESTART IDENTITY"))
    count = 0

    contacts = (await session.execute(select(EmergencyContact))).scalars().all()
    for row in contacts:
        session.add(
            MunicipalService(
                hizmet_tipi=(row.category or "acil")[:100],
                birim=row.name[:255],
                calisma_saatleri="7/24" if (row.phone in {"112", "110", "155", "156", "185", "186"}) else None,
                iletisim=row.phone[:255],
                source_url="https://www.aliaga.bel.tr/",
                last_verified_at=verified_at,
                quality_score=0.86,
                ingestion_batch_id=batch_id,
            )
        )
        count += 1

    institutions = (
        await session.execute(
            select(Institution).where(
                Institution.category.in_(["kamu", "saglik", "egitim", "kutuphane", "kultur"])
            )
        )
    ).scalars().all()
    for row in institutions:
        contact = row.phone or row.website
        session.add(
            MunicipalService(
                hizmet_tipi=(row.category or "kamu")[:100],
                birim=row.name[:255],
                calisma_saatleri=_working_hours_to_text(row.working_hours),
                iletisim=(contact[:255] if contact else None),
                source_url=row.website or "https://www.aliaga.bel.tr/",
                last_verified_at=verified_at,
                quality_score=0.75,
                ingestion_batch_id=batch_id,
            )
        )
        count += 1

    await session.flush()
    return count


async def _sync_population_csv(
    session: AsyncSession,
    csv_url: str,
    year_value: int,
    batch_id: str,
    verified_at: date,
) -> int:
    text = await _download_text(csv_url)
    count = 0
    reader = _csv_reader(text)
    headers = {_norm_tr(h): h for h in (reader.fieldnames or [])}
    male_key = headers.get("nufus_erkek_toplam") or headers.get("erkek")
    female_key = headers.get("nufus_kadin_toplam") or headers.get("kadin")

    for row in reader:
        if _norm_tr(row.get("ILCE_ADI")) != "aliaga":
            continue

        neighborhood = str(row.get("MAHALLE_ADI") or "").strip() or None
        male = _safe_float(row.get(male_key)) if male_key else 0.0
        female = _safe_float(row.get(female_key)) if female_key else 0.0
        male = male or 0.0
        female = female or 0.0
        total = male + female

        for metric_name, metric_value in [
            ("nufus_erkek", male),
            ("nufus_kadin", female),
            ("nufus_toplam", total),
        ]:
            session.add(
                DistrictStat(
                    yil=year_value,
                    metrik_adi=metric_name,
                    metrik_degeri=float(metric_value),
                    birim="kisi",
                    district="Aliağa",
                    neighborhood=neighborhood[:100] if neighborhood else None,
                    source_url=csv_url,
                    last_verified_at=verified_at,
                    quality_score=0.83,
                    ingestion_batch_id=batch_id,
                )
            )
            count += 1

    await session.flush()
    return count


async def sync_district_stats(session: AsyncSession, batch_id: str, verified_at: date) -> int:
    await session.execute(text("TRUNCATE TABLE district_stats RESTART IDENTITY"))
    c2023 = await _sync_population_csv(
        session=session,
        csv_url=POP_2023_CSV,
        year_value=2023,
        batch_id=batch_id,
        verified_at=verified_at,
    )
    c2022 = await _sync_population_csv(
        session=session,
        csv_url=POP_2022_CSV,
        year_value=2022,
        batch_id=batch_id,
        verified_at=verified_at,
    )
    return c2023 + c2022


async def sync_knowledge_layers(session: AsyncSession) -> dict[str, int]:
    """
    Yeni bilgi katmanlarını (ulasim, poi, kurumsal, demografi) senkronize eder.
    """
    lock_sql = text("SELECT pg_advisory_lock(:lock_id)")
    unlock_sql = text("SELECT pg_advisory_unlock(:lock_id)")
    await session.execute(lock_sql, {"lock_id": KNOWLEDGE_SYNC_LOCK_ID})
    try:
        batch_id = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        verified_at = date.today()

        transport_stats = await sync_transport_layers(session, batch_id=batch_id, verified_at=verified_at)
        poi_count = await sync_poi_catalog(session, batch_id=batch_id, verified_at=verified_at)
        municipal_count = await sync_municipal_services(session, batch_id=batch_id, verified_at=verified_at)
        district_count = await sync_district_stats(session, batch_id=batch_id, verified_at=verified_at)

        stats = {
            **transport_stats,
            "poi_catalog": poi_count,
            "municipal_services": municipal_count,
            "district_stats": district_count,
        }
        logger.info(f"Knowledge layer sync tamamlandi: {stats}")
        return stats
    finally:
        await session.execute(unlock_sql, {"lock_id": KNOWLEDGE_SYNC_LOCK_ID})
