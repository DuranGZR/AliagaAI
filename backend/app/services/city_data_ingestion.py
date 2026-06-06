from __future__ import annotations

import io
import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from typing import Any, Awaitable, Callable
from urllib.parse import urljoin

import httpx
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cache import (
    CurrencyCache,
    EarthquakesCache,
    FuelPricesCache,
    GoldCache,
    PrayerTimesCache,
    WeatherCache,
)
from app.models.city import (
    CityKnowledge,
    DocumentChunk,
    EmergencyContact,
    FerrySchedule,
    IzbanSchedule,
    PostalCode,
    StreetMarket,
    TaxiStand,
    UtilityOutage,
)
from app.models.content import Announcement, Event, JobListing, News, Obituary, Project
from app.models.knowledge_layers import (
    DistrictStat,
    MunicipalService,
    PoiCatalog,
    TransportDeparture,
    TransportRoute,
    TransportStop,
)
from app.models.places import Institution, Place, ServiceProvider
from app.services.chunk_indexer import sync_all_document_chunks
from app.services.collectapi_client import fetch_all
from app.services.data_completeness import ensure_core_city_data
from app.services.data_quality import run_data_quality_pass
from app.services.earthquake_client import fetch_earthquakes
from app.services.embedding import generate_embedding
from app.services.scraper_aliaga_bel import AliagaBelScraper
from app.services.scraper_base import BaseScraper
from app.services.scraper_city_info import scrape_and_save_city_info
from app.services.scraper_izmir_mezarlik import scrape_izmir_mezarlik
from app.services.scraper_izmir_open_data import sync_open_data_city_tables
from app.services.scraper_knowledge_layers import sync_knowledge_layers
from app.services.scraper_news import scrape_and_save_news, sync_events_from_news
from app.services.scraper_outages import scrape_outages
from app.services.seed_data import seed_all
from app.services.seed_data_extended import seed_extended


ALL_CITY_DATA_SOURCE_TYPES = [
    "news",
    "event",
    "announcement",
    "project",
    "job",
    "place",
    "institution",
    "service_provider",
    "outage",
    "obituary",
    "city_knowledge",
    "transport_route",
    "transport_stop",
    "transport_departure",
    "poi_catalog",
    "municipal_service",
    "district_stat",
    "izban_schedule",
    "ferry_schedule",
    "taxi_stand",
    "postal_code",
]


@dataclass(frozen=True)
class OfficialPage:
    layer: str
    title: str
    path: str
    tags: tuple[str, ...]


OFFICIAL_PAGES = [
    OfficialPage("genel", "Aliaga tarihcesi", "/aliaga/tarihce", ("tarih", "kent")),
    OfficialPage("genel", "Aliaga antik kentler", "/aliaga/antik-kentler", ("antik kent", "arkeoloji")),
    OfficialPage("gezi", "Aliaga turizm", "/aliaga/turizm", ("turizm", "gezi")),
    OfficialPage("gastronomi", "Aliaga gastronomi", "/aliaga/gastronomi", ("gastronomi", "yeme icme")),
    OfficialPage("genel", "Aliaga cografyasi", "/aliaga/cografyasi", ("cografya", "konum")),
    OfficialPage("demografi", "Aliaga nufus ve demografi", "/aliaga/nufus-ve-demografi", ("nufus", "demografi")),
    OfficialPage("egitim", "Aliaga egitim", "/aliaga/egitim", ("egitim", "okul")),
    OfficialPage("kultur", "Aliaga kultur", "/aliaga/kultur", ("kultur", "sanat")),
    OfficialPage("saglik", "Aliaga saglik", "/aliaga/saglik", ("saglik", "hastane")),
    OfficialPage("ekonomi", "Aliaga ekonomi", "/aliaga/ekonomi", ("ekonomi", "sanayi")),
    OfficialPage("mahalle", "Aliaga mahalleleri", "/aliaga/mahallelerimiz", ("mahalle", "semt")),
    OfficialPage("gezi", "Aliaga gezi rotalari", "/aliaga/aliaga-da-gezi-rotalari", ("gezi", "rota")),
    OfficialPage("kultur", "Helvaci kilimi", "/aliaga/helvaci-kilimi", ("kilim", "kultur")),
    OfficialPage("ulasim", "Aliaga'ya nasil gelinir", "/aliaga/aliaga-ya-nasil-gelinir", ("ulasim", "rota")),
    OfficialPage("kurumlar", "Kent rehberi kamu kuruluslari", "/kent-rehberi/kamu-kuruluslari", ("kamu", "kurum")),
    OfficialPage("saglik", "Kent rehberi saglik kuruluslari", "/kent-rehberi/saglik-kuruluslari", ("saglik", "kurum")),
    OfficialPage("egitim", "Kent rehberi okullar", "/kent-rehberi/okullar", ("okul", "egitim")),
    OfficialPage("konaklama", "Kent rehberi oteller", "/kent-rehberi/oteller", ("otel", "konaklama")),
    OfficialPage("mahalle", "Muhtarliklar", "/kent-rehberi/muhtarliklarimiz", ("muhtar", "mahalle")),
    OfficialPage("saglik", "Nobetci eczane", "/kent-rehberi/nobetci-eczane", ("eczane", "saglik")),
    OfficialPage("belediye", "Bize ulasin", "/bize-ulasin", ("iletisim", "belediye")),
    OfficialPage("belediye", "Hizmetlerimiz", "/hizmetlerimiz", ("belediye", "hizmet")),
    OfficialPage("spor", "Aliaga genclik merkezi", "/hizmetlerimiz/aliaga-genclik-merkezi", ("spor", "havuz")),
    OfficialPage("kultur", "Aliaga sanat evi", "/hizmetlerimiz/aliaga-sanat-evi", ("kultur", "sanat")),
    OfficialPage("spor", "Spor ve yasam merkezi", "/hizmetlerimiz/spor-ve-yasam-merkezi", ("spor", "tesis")),
    OfficialPage("kutuphane", "Aliaga kent kitapligi", "/hizmetlerimiz/aliaga-kent-kitapligi", ("kutuphane", "kitap")),
    OfficialPage("kutuphane", "Aziz Sancar kutuphanesi", "/hizmetlerimiz/aziz-sancar-kutuphanesi", ("kutuphane", "kitap")),
    OfficialPage("kutuphane", "Nadir Nadi kutuphanesi", "/hizmetlerimiz/nadir-nadi-kutuphanesi", ("kutuphane", "kitap")),
    OfficialPage("sosyal", "Sosyal market", "/hizmetlerimiz/sosyal-market", ("sosyal destek", "belediye")),
]


OSM_BBOX = "38.55,26.70,39.08,27.35"
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
OVERPASS_TAG_GROUPS = [
    ("amenity", "amenity"),
    ("shop", "shop"),
    ("tourism", "tourism"),
    ("leisure", "leisure"),
    ("historic", "historic"),
    ("healthcare", "healthcare"),
    ("office", "office"),
    ("craft", "craft"),
    ("public_transport", "public_transport"),
]


def _norm(text: str | None) -> str:
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


def _clean_text(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def _truncate(value: str | None, limit: int) -> str | None:
    cleaned = _clean_text(value)
    return cleaned[:limit] if cleaned else None


def _absolute_aliaga_url(path: str) -> str:
    return urljoin("https://www.aliaga.bel.tr", path)


def _first_text(*values: str | None) -> str | None:
    for value in values:
        cleaned = _clean_text(value)
        if cleaned:
            return cleaned
    return None


class OfficialPageScraper(BaseScraper):
    BASE_URL = "https://www.aliaga.bel.tr"

    async def scrape(self, **kwargs) -> list[dict[str, Any]]:
        pages = kwargs.get("pages") or OFFICIAL_PAGES
        results = []
        for page in pages:
            soup = await self._fetch_page(page.path)
            if not soup:
                continue

            for el in soup.select(
                "script, style, nav, footer, header, iframe, form, .breadcrumb, .social-share, .menu, .navbar"
            ):
                el.decompose()

            main = soup.select_one("main, article, .content, .icerik, .sayfa-content, .page-content, body")
            if not main:
                continue

            blocks = []
            for el in main.select("h1, h2, h3, h4, p, li, td"):
                text = self.clean_text(el.get_text(" "))
                if len(text) >= 20:
                    blocks.append(text)

            if not blocks:
                body_text = self.clean_text(main.get_text(" "))
                if len(body_text) >= 80:
                    blocks.append(body_text)

            seen = set()
            unique_blocks = []
            for block in blocks:
                key = _norm(block)
                if key in seen:
                    continue
                seen.add(key)
                unique_blocks.append(block)

            content = "\n".join(unique_blocks).strip()
            if len(content) < 80:
                continue

            results.append(
                {
                    "layer": page.layer,
                    "title": page.title,
                    "content": content,
                    "source_url": _absolute_aliaga_url(page.path),
                    "tags": list(page.tags),
                }
            )
        return results


async def sync_official_pages_to_city_knowledge(session: AsyncSession) -> int:
    scraper = OfficialPageScraper()
    pages = await scraper.scrape()
    existing = (await session.execute(select(CityKnowledge))).scalars().all()
    by_url = {row.source_url: row for row in existing if row.source_url}
    by_key = {(_norm(row.layer), _norm(row.title)): row for row in existing}

    changed = 0
    today = date.today()
    for page in pages:
        row = by_url.get(page["source_url"]) or by_key.get((_norm(page["layer"]), _norm(page["title"])))
        summary = page["content"][:12000]
        tags = [*page["tags"], "Aliaga", "resmi kaynak"]
        if row is None:
            session.add(
                CityKnowledge(
                    layer=page["layer"][:30],
                    title=page["title"][:255],
                    summary=summary,
                    tags=tags,
                    source_url=page["source_url"],
                    last_verified_at=today,
                )
            )
            changed += 1
            continue

        updates = {
            "layer": page["layer"][:30],
            "title": page["title"][:255],
            "summary": summary,
            "tags": tags,
            "source_url": page["source_url"],
            "last_verified_at": today,
        }
        for field, value in updates.items():
            if getattr(row, field) != value:
                setattr(row, field, value)
                changed += 1

    await session.flush()
    return changed


def _build_overpass_query(tag_key: str) -> str:
    return f"""
[out:json][timeout:45];
relation(1268453);
map_to_area->.searchArea;
(
  node["name"]["{tag_key}"](area.searchArea);
  way["name"]["{tag_key}"](area.searchArea);
  relation["name"]["{tag_key}"](area.searchArea);
);
out center;
"""


async def _fetch_overpass_group(tag_key: str) -> list[dict[str, Any]]:
    last_error: Exception | None = None
    query = _build_overpass_query(tag_key)
    for endpoint in OVERPASS_ENDPOINTS:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    endpoint,
                    data={"data": query},
                    headers={
                        "User-Agent": "AliagaAI/1.0 (local city data ingestion)",
                        "Accept": "application/json",
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                return data.get("elements", [])
        except Exception as exc:
            last_error = exc
            logger.warning(f"OSM Overpass group failed ({tag_key}, {endpoint}): {exc}")
    if last_error:
        raise RuntimeError(f"OSM Overpass group failed: {tag_key}") from last_error
    return []


def _osm_lat_lon(element: dict[str, Any]) -> tuple[float | None, float | None]:
    lat = element.get("lat") or (element.get("center") or {}).get("lat")
    lon = element.get("lon") or (element.get("center") or {}).get("lon")
    try:
        return (float(lat) if lat is not None else None, float(lon) if lon is not None else None)
    except (TypeError, ValueError):
        return None, None


def _osm_source_url(element: dict[str, Any]) -> str:
    element_type = element.get("type") or "node"
    element_id = element.get("id")
    return f"https://www.openstreetmap.org/{element_type}/{element_id}" if element_id else "https://www.openstreetmap.org/"


def _osm_address(tags: dict[str, Any]) -> str | None:
    bits = [
        tags.get("addr:street"),
        tags.get("addr:housenumber"),
        tags.get("addr:neighbourhood") or tags.get("addr:suburb"),
        tags.get("addr:district"),
        tags.get("addr:city") or "Aliağa",
    ]
    return _truncate(", ".join(str(x) for x in bits if _clean_text(str(x) if x is not None else "")), 1000)


def _osm_phone(tags: dict[str, Any]) -> str | None:
    return _truncate(
        _first_text(tags.get("phone"), tags.get("contact:phone"), tags.get("mobile"), tags.get("contact:mobile")),
        50,
    )


def _osm_website(tags: dict[str, Any]) -> str | None:
    return _truncate(_first_text(tags.get("website"), tags.get("contact:website"), tags.get("url")), 1000)


def _classify_osm(tags: dict[str, Any], has_phone: bool) -> tuple[str, str, str | None]:
    amenity = tags.get("amenity")
    shop = tags.get("shop")
    tourism = tags.get("tourism")
    leisure = tags.get("leisure")
    historic = tags.get("historic")
    healthcare = tags.get("healthcare")
    office = tags.get("office")
    craft = tags.get("craft")
    public_transport = tags.get("public_transport")

    service_map = {
        ("craft", "plumber"): "tesisatci",
        ("craft", "electrician"): "elektrikci",
        ("craft", "locksmith"): "cilingir",
        ("shop", "car_repair"): "oto_tamir",
        ("shop", "tyres"): "lastikci",
        ("amenity", "car_wash"): "oto_yikama",
        ("shop", "hairdresser"): "kuafor",
        ("amenity", "veterinary"): "veteriner",
    }
    for key, value, in service_map:
        if tags.get(key) == value:
            category = service_map[(key, value)]
            return ("service_provider" if has_phone else "place", category, value)

    if amenity in {"restaurant", "fast_food", "food_court"}:
        return "place", "restoran", amenity
    if amenity in {"cafe", "bar", "pub", "ice_cream"}:
        return "place", "kafe", amenity
    if amenity in {"hospital", "clinic", "doctors", "dentist", "pharmacy"} or healthcare:
        return "institution", "saglik", healthcare or amenity
    if amenity in {"school", "kindergarten", "college", "university", "library"}:
        return "institution", "egitim" if amenity != "library" else "kutuphane", amenity
    if amenity in {"police", "fire_station", "townhall", "courthouse", "post_office", "prison"}:
        return "institution", "kamu", amenity
    if amenity in {"bank", "atm"}:
        return "institution", "banka" if amenity == "bank" else "atm", amenity
    if amenity == "place_of_worship":
        return "institution", "cami", tags.get("religion") or amenity
    if amenity in {"fuel", "parking", "taxi", "bus_station", "ferry_terminal"} or public_transport:
        return "place", "ulasim", public_transport or amenity
    if shop:
        if shop in {"supermarket", "convenience", "bakery", "butcher", "greengrocer"}:
            return "institution", "market", shop
        return "place", "magaza", shop
    if tourism:
        if tourism in {"hotel", "motel", "hostel", "guest_house", "apartment"}:
            return "institution", "otel", tourism
        return "place", "turistik", tourism
    if leisure:
        if leisure in {"sports_centre", "stadium", "fitness_centre"}:
            return "institution", "spor", leisure
        return "place", "park", leisure
    if historic:
        return "place", "turistik", historic
    if office:
        return "institution", "kamu" if office in {"government", "administrative"} else "diger", office
    if craft:
        return "place", "hizmet", craft
    return "place", "diger", None


def _osm_description(tags: dict[str, Any], category: str, subcategory: str | None, source_url: str) -> str:
    parts = [
        f"Kategori: {category}",
        f"Alt kategori: {subcategory}" if subcategory else None,
        f"Calisma saatleri: {tags.get('opening_hours')}" if tags.get("opening_hours") else None,
        f"Mutfak/Tur: {tags.get('cuisine')}" if tags.get("cuisine") else None,
        f"OSM kaynak: {source_url}",
    ]
    return " | ".join(part for part in parts if part)


def _fill_if_blank(row: Any, values: dict[str, Any]) -> int:
    changed = 0
    for field, value in values.items():
        if value is None:
            continue
        current = getattr(row, field)
        if current in (None, "", [], {}):
            setattr(row, field, value)
            changed += 1
    return changed


async def sync_osm_city_directory(session: AsyncSession) -> dict[str, int]:
    elements_by_key: dict[tuple[str, int], dict[str, Any]] = {}
    group_errors: dict[str, str] = {}
    for _, tag_key in OVERPASS_TAG_GROUPS:
        try:
            elements = await _fetch_overpass_group(tag_key)
            for element in elements:
                element_id = element.get("id")
                element_type = element.get("type")
                if element_id is None or element_type is None:
                    continue
                elements_by_key[(str(element_type), int(element_id))] = element
        except Exception as exc:
            group_errors[tag_key] = str(exc)

    places = (await session.execute(select(Place))).scalars().all()
    institutions = (await session.execute(select(Institution))).scalars().all()
    providers = (await session.execute(select(ServiceProvider))).scalars().all()
    place_by_key = {(_norm(row.name), _norm(row.category), _norm(row.subcategory)): row for row in places}
    inst_by_key = {(_norm(row.name), _norm(row.category), _norm(row.subcategory)): row for row in institutions}
    provider_by_key = {(_norm(row.name), _norm(row.category), _norm(row.phone)): row for row in providers}

    stats = {
        "osm_elements": len(elements_by_key),
        "places_added": 0,
        "places_updated": 0,
        "institutions_added": 0,
        "institutions_updated": 0,
        "service_providers_added": 0,
        "service_providers_updated": 0,
        "groups_failed": len(group_errors),
    }

    for element in elements_by_key.values():
        tags = element.get("tags") or {}
        name = _truncate(_first_text(tags.get("name:tr"), tags.get("name")), 255)
        if not name or len(name) < 2:
            continue

        lat, lon = _osm_lat_lon(element)
        phone = _osm_phone(tags)
        website = _osm_website(tags)
        source_url = _osm_source_url(element)
        target, category, subcategory = _classify_osm(tags, has_phone=bool(phone))
        address = _osm_address(tags)
        description = _osm_description(tags, category, subcategory, source_url)
        opening_hours = _truncate(tags.get("opening_hours"), 255)

        if target == "service_provider" and phone:
            key = (_norm(name), _norm(category), _norm(phone))
            existing = provider_by_key.get(key)
            data = {
                "name": name,
                "phone": phone,
                "category": category[:50],
                "address": address,
                "neighborhood": _truncate(tags.get("addr:neighbourhood") or tags.get("addr:suburb"), 100),
                "description": description,
                "is_24h": bool(opening_hours and "24/7" in opening_hours),
                "is_active": True,
            }
            if existing is None:
                provider = ServiceProvider(**data)
                session.add(provider)
                provider_by_key[key] = provider
                stats["service_providers_added"] += 1
            else:
                stats["service_providers_updated"] += _fill_if_blank(existing, data)
            continue

        if target == "institution":
            key = (_norm(name), _norm(category), _norm(subcategory))
            existing = inst_by_key.get(key)
            data = {
                "name": name,
                "category": category[:50],
                "subcategory": _truncate(subcategory, 50),
                "address": address,
                "phone": phone,
                "website": website,
                "latitude": lat,
                "longitude": lon,
                "description": description,
                "working_hours": {"raw": opening_hours} if opening_hours else None,
                "is_active": True,
            }
            if existing is None:
                institution = Institution(**data)
                session.add(institution)
                inst_by_key[key] = institution
                stats["institutions_added"] += 1
            else:
                stats["institutions_updated"] += _fill_if_blank(existing, data)
            continue

        key = (_norm(name), _norm(category), _norm(subcategory))
        existing = place_by_key.get(key)
        tags_list = [item for item in [category, subcategory, "OpenStreetMap", "Aliaga"] if item]
        data = {
            "name": name,
            "category": category[:50],
            "subcategory": _truncate(subcategory, 50),
            "address": address,
            "phone": phone,
            "website": website,
            "latitude": lat,
            "longitude": lon,
            "description": description,
            "working_hours": {"raw": opening_hours} if opening_hours else None,
            "tags": tags_list,
            "is_active": True,
        }
        if existing is None:
            place = Place(**data)
            session.add(place)
            place_by_key[key] = place
            stats["places_added"] += 1
        else:
            stats["places_updated"] += _fill_if_blank(existing, data)

    await session.flush()
    if group_errors:
        stats["group_errors"] = group_errors  # type: ignore[assignment]
    return stats


async def _sync_aliaga_bel_extended(session: AsyncSession) -> dict[str, int]:
    scraper = AliagaBelScraper()
    scraper.max_list_pages = 10
    return {
        "projects": await scraper.fetch_projects(session),
        "announcements": await scraper.fetch_announcements(session),
        "job_listings": await scraper.fetch_job_listings(session),
        "service_providers": await scraper.fetch_service_providers(session),
    }


async def _run_step(
    name: str,
    session: AsyncSession,
    stats: dict[str, Any],
    func_: Callable[[], Awaitable[Any]],
) -> None:
    logger.info(f"City data ingestion step started: {name}")
    try:
        result = await func_()
        await session.commit()
        stats[name] = result
        logger.info(f"City data ingestion step completed: {name} -> {result}")
    except Exception as exc:
        await session.rollback()
        stats[f"{name}_error"] = str(exc)
        logger.exception(f"City data ingestion step failed: {name}")


async def get_city_data_counts(session: AsyncSession) -> dict[str, Any]:
    table_models = [
        ("weather_cache", WeatherCache),
        ("prayer_times_cache", PrayerTimesCache),
        ("fuel_prices_cache", FuelPricesCache),
        ("currency_cache", CurrencyCache),
        ("gold_cache", GoldCache),
        ("earthquakes_cache", EarthquakesCache),
        ("news", News),
        ("events", Event),
        ("announcements", Announcement),
        ("projects", Project),
        ("job_listings", JobListing),
        ("obituaries", Obituary),
        ("utility_outages", UtilityOutage),
        ("places", Place),
        ("institutions", Institution),
        ("service_providers", ServiceProvider),
        ("city_knowledge", CityKnowledge),
        ("poi_catalog", PoiCatalog),
        ("municipal_services", MunicipalService),
        ("district_stats", DistrictStat),
        ("transport_routes", TransportRoute),
        ("transport_stops", TransportStop),
        ("transport_departures", TransportDeparture),
        ("izban_schedules", IzbanSchedule),
        ("ferry_schedules", FerrySchedule),
        ("street_markets", StreetMarket),
        ("emergency_contacts", EmergencyContact),
        ("taxi_stands", TaxiStand),
        ("postal_codes", PostalCode),
    ]

    tables: dict[str, int] = {}
    for name, model in table_models:
        result = await session.execute(select(func.count()).select_from(model))
        tables[name] = int(result.scalar_one() or 0)

    chunk_counts: dict[str, int] = {}
    total_chunks = 0
    if DocumentChunk is not None:
        rows = await session.execute(
            select(DocumentChunk.source_type, func.count()).group_by(DocumentChunk.source_type)
        )
        for source_type, count in rows:
            chunk_counts[source_type] = int(count or 0)
            total_chunks += int(count or 0)

    return {"tables": tables, "chunks": chunk_counts, "total_chunks": total_chunks}


async def ingest_all_city_data(
    session: AsyncSession,
    *,
    include_osm: bool = True,
    sync_chunks: bool = True,
    include_legacy_city_info_chunks: bool = True,
) -> dict[str, Any]:
    stats: dict[str, Any] = {}

    await _run_step("seed_core", session, stats, lambda: seed_all(session, sync_rag_chunks=False))
    await _run_step("collectapi", session, stats, lambda: fetch_all(session))
    await _run_step("earthquakes", session, stats, lambda: fetch_earthquakes(session))
    await _run_step("news_events", session, stats, lambda: _sync_news_events(session))
    await _run_step("seed_extended", session, stats, lambda: seed_extended(session))
    await _run_step("aliaga_bel_extended", session, stats, lambda: _sync_aliaga_bel_extended(session))
    await _run_step("official_pages", session, stats, lambda: sync_official_pages_to_city_knowledge(session))
    await _run_step("izmir_open_data", session, stats, lambda: sync_open_data_city_tables(session))

    if include_osm:
        await _run_step("osm_directory", session, stats, lambda: sync_osm_city_directory(session))

    await _run_step("knowledge_layers", session, stats, lambda: sync_knowledge_layers(session))
    await _run_step("obituaries_outages", session, stats, lambda: _sync_obituaries_outages(session))
    await _run_step("data_completeness", session, stats, lambda: ensure_core_city_data(session))
    await _run_step("data_quality", session, stats, lambda: run_data_quality_pass(session))

    if sync_chunks and include_legacy_city_info_chunks:
        await _run_step(
            "legacy_city_info_chunks",
            session,
            stats,
            lambda: scrape_and_save_city_info(session, embedding_fn=generate_embedding),
        )

    if sync_chunks:
        await _run_step(
            "chunk_sync",
            session,
            stats,
            lambda: sync_all_document_chunks(session, source_types=ALL_CITY_DATA_SOURCE_TYPES),
        )

    await _run_step("counts", session, stats, lambda: get_city_data_counts(session))
    return stats


async def _sync_news_events(session: AsyncSession) -> dict[str, int]:
    return {
        "news": await scrape_and_save_news(session),
        "events_from_news": await sync_events_from_news(session),
    }


async def _sync_obituaries_outages(session: AsyncSession) -> dict[str, int]:
    obituaries = await scrape_izmir_mezarlik(session)
    outages = await scrape_outages(session)
    return {"obituaries": obituaries or 0, "outages": outages or 0}
