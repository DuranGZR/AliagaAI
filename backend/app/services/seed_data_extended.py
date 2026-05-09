"""
AliağaAI — Genişletilmiş Test Verisi Yükleyici.

Toplu taşıma, etkinlik, projeler, su kesintileri gibi henüz canlı apisi olmayan 
ancak AI'nin cevap verebilmesi için gerekli olan statik örnek (seed) verilerini veritabanına atar.
"""
from datetime import datetime, timedelta, time
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.city import IzbanSchedule, FerrySchedule, UtilityOutage
from app.models.content import Event, Announcement, Project, JobListing, Obituary
from app.models.places import ServiceProvider

# --- GERÇEK İZBAN SİSTEMİ (Statik) ---
# Aliağa'dan her 24 dakikada bir hareket eder (05:20 - 01:00 arası)
IZBAN_SCHEDULES = []
for m in range(5 * 60 + 20, 25 * 60, 24):
    hr = (m // 60) % 24
    mn = m % 60
    IZBAN_SCHEDULES.append({
        "line": "Kuzey Aksı",
        "station": "Aliağa",
        "direction": "Cumaovası/Tepeköy yönü",
        "departure_time": time(hr, mn),
        "day_type": "her_gun"
    })

# --- GERÇEK FERİBOT SİSTEMİ (Statik) ---
# İzdeniz Aliağa - Foça yaz dönemi (Temsili gerçek sefer saatleri)
FERRY_SCHEDULES = [
    {"route": "Aliağa - Foça", "departure_time": time(8, 30), "day_type": "her_gun"},
    {"route": "Aliağa - Foça", "departure_time": time(19, 0), "day_type": "her_gun"},
]

# --- SCRAPER İLE GERÇEK ZAMANLI DOLDURULACAKLAR (Aşağıdaki çakmalar silindi) ---
SERVICE_PROVIDERS = []
UTILITY_OUTAGES = []
EVENTS = []

ANNOUNCEMENTS = []
PROJECTS = []
JOB_LISTINGS = []
OBITUARIES = []


async def _insert_if_empty(session: AsyncSession, model, data_list: list[dict]):
    """Tablo boşsa verileri yükler, doluysa atlar."""
    result = await session.execute(select(model).limit(1))
    if result.scalars().first() is not None:
        return 0

    count = 0
    for item in data_list:
        session.add(model(**item))
        count += 1
    await session.flush()
    return count


async def seed_extended(session: AsyncSession) -> dict[str, int]:
    """Test (seed) statik verilerini yükler."""
    results = {}

    results["izban_schedules"] = await _insert_if_empty(session, IzbanSchedule, IZBAN_SCHEDULES)
    results["ferry_schedules"] = await _insert_if_empty(session, FerrySchedule, FERRY_SCHEDULES)
    results["service_providers"] = await _insert_if_empty(session, ServiceProvider, SERVICE_PROVIDERS)
    results["utility_outages"] = await _insert_if_empty(session, UtilityOutage, UTILITY_OUTAGES)
    results["events"] = await _insert_if_empty(session, Event, EVENTS)
    results["announcements"] = await _insert_if_empty(session, Announcement, ANNOUNCEMENTS)
    results["projects"] = await _insert_if_empty(session, Project, PROJECTS)
    results["job_listings"] = await _insert_if_empty(session, JobListing, JOB_LISTINGS)
    results["obituaries"] = await _insert_if_empty(session, Obituary, OBITUARIES)

    await session.commit()
    return results

