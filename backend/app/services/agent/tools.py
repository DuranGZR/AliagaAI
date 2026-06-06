"""
AliağaAI — Ajan Araçları (Agent Tools).

Her fonksiyon LLM tarafından çağrılabilir bağımsız bir araçtır.
Tümü async, tek sorumluluk ilkesine uygun ve string sonuç döner.
Veritabanı oturumu her çağrıda dışarıdan sağlanır.
"""
from __future__ import annotations

from datetime import date
import re

from loguru import logger
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
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
    EmergencyContact,
    FerrySchedule,
    IzbanSchedule,
    PostalCode,
    StreetMarket,
    TaxiStand,
    UtilityOutage,
)
from app.models.content import Announcement, Event, JobListing, News, Project
from app.models.places import Institution, Pharmacy, Place
from app.services.collectapi_client import fetch_pharmacies
from app.services.rag import search_similar_chunks


# ─────────────────────────────────────────────────────────────────────
# 1. HYBRID RAG ARAMA — Genel Bilgi
# ─────────────────────────────────────────────────────────────────────

async def search_knowledge(query: str, *, session: AsyncSession) -> str:
    """Aliağa hakkında genel bilgi, tarih, gezi, ulaşım, kurumlar,
    mahalleler ve belediye bilgileri için vektör + kelime tabanlı
    hibrit arama yapar.

    Dönüş: LLM'in bağlam olarak kullanacağı formatlı metin.
    """
    chunks = await search_similar_chunks(
        session=session,
        query=query,
        limit=settings.RAG_TOP_K,
        min_similarity=settings.RAG_MIN_SIMILARITY,
    )

    if not chunks:
        return "Bu konuda yerel veritabanında kayıt bulunamadı."

    lines: list[str] = []
    for idx, chunk in enumerate(chunks, start=1):
        meta = chunk.get("metadata") or {}
        title = meta.get("title", "Kaynak")
        source_type = chunk.get("source_type", "bilgi")
        score = chunk.get("rerank_score", chunk.get("fusion_score", 0.0))
        content = chunk.get("content", "")

        # Çok uzun chunk'ları kısalt
        if len(content) > 1500:
            content = content[:1500] + "..."

        lines.append(f"[{idx}] ({source_type}) {title} — skor: {score:.2f}\n{content}")

    return "\n\n".join(lines)


# ─────────────────────────────────────────────────────────────────────
# 2. NÖBETÇİ ECZANELER
# ─────────────────────────────────────────────────────────────────────

async def get_duty_pharmacies(*, session: AsyncSession) -> str:
    """Bugünkü nöbetçi eczaneleri listeler."""
    stmt = select(Pharmacy).where(Pharmacy.duty_date == date.today())
    pharmacies = (await session.execute(stmt)).scalars().all()

    if not pharmacies:
        await fetch_pharmacies(session)
        await session.flush()
        pharmacies = (await session.execute(stmt)).scalars().all()

    if not pharmacies:
        return "Bugün için nöbetçi eczane verisi bulunamadı."

    lines = [f"Bugünkü Nöbetçi Eczaneler ({date.today().isoformat()}):"]
    for p in pharmacies:
        parts = [f"• {p.name}"]
        if p.address:
            parts.append(f"  Adres: {p.address}")
        if p.phone:
            parts.append(f"  Tel: {p.phone}")
        lines.append("\n".join(parts))

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────
# 3. HAVA DURUMU
# ─────────────────────────────────────────────────────────────────────

async def get_weather(*, session: AsyncSession) -> str:
    """Güncel Aliağa/İzmir hava durumu bilgisini getirir."""
    weather = (
        await session.execute(
            select(WeatherCache).order_by(WeatherCache.date.desc()).limit(1)
        )
    ).scalars().first()

    if not weather:
        return "Güncel hava durumu verisi bulunamadı."

    parts = [
        f"Hava Durumu ({weather.date.isoformat()}):",
        f"• Sıcaklık: {weather.temperature}°C",
        f"• Durum: {weather.description}",
    ]
    if weather.min_temp is not None and weather.max_temp is not None:
        parts.append(f"• Min/Max: {weather.min_temp}°C — {weather.max_temp}°C")
    if weather.wind:
        parts.append(f"• Rüzgar: {weather.wind}")
    if weather.humidity:
        parts.append(f"• Nem: {weather.humidity}")

    return "\n".join(parts)


# ─────────────────────────────────────────────────────────────────────
# 4. NAMAZ VAKİTLERİ
# ─────────────────────────────────────────────────────────────────────

async def get_prayer_times(*, session: AsyncSession) -> str:
    """Güncel namaz vakitlerini getirir."""
    prayer = (
        await session.execute(
            select(PrayerTimesCache).order_by(PrayerTimesCache.date.desc()).limit(1)
        )
    ).scalars().first()

    if not prayer:
        return "Güncel namaz vakitleri bulunamadı."

    return (
        f"Namaz Vakitleri ({prayer.date.isoformat()}):\n"
        f"• İmsak: {prayer.fajr}\n"
        f"• Güneş: {prayer.sunrise}\n"
        f"• Öğle: {prayer.dhuhr}\n"
        f"• İkindi: {prayer.asr}\n"
        f"• Akşam: {prayer.maghrib}\n"
        f"• Yatsı: {prayer.isha}"
    )


# ─────────────────────────────────────────────────────────────────────
# 5. AKARYAKIT FİYATLARI
# ─────────────────────────────────────────────────────────────────────

async def get_fuel_prices(*, session: AsyncSession) -> str:
    """Güncel akaryakıt fiyatlarını getirir."""
    fuel = (
        await session.execute(
            select(FuelPricesCache).order_by(FuelPricesCache.fetched_at.desc()).limit(1)
        )
    ).scalars().first()

    if not fuel:
        return "Güncel akaryakıt fiyatları bulunamadı."

    return (
        f"Akaryakıt Fiyatları:\n"
        f"• Benzin: {fuel.gasoline} TL\n"
        f"• Motorin: {fuel.diesel} TL\n"
        f"• LPG: {fuel.lpg} TL"
    )


# ─────────────────────────────────────────────────────────────────────
# 6. DÖVİZ KURLARI
# ─────────────────────────────────────────────────────────────────────

async def get_currency_rates(*, session: AsyncSession) -> str:
    """Güncel döviz kurlarını getirir."""
    currencies = (await session.execute(select(CurrencyCache))).scalars().all()

    if not currencies:
        return "Güncel döviz kurları bulunamadı."

    lines = ["Güncel Döviz Kurları:"]
    for c in currencies:
        lines.append(f"• {c.name} ({c.code}): Alış {c.buying} TL, Satış {c.selling} TL")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────
# 7. ALTIN FİYATLARI
# ─────────────────────────────────────────────────────────────────────

async def get_gold_prices(*, session: AsyncSession) -> str:
    """Güncel altın fiyatlarını getirir."""
    golds = (await session.execute(select(GoldCache))).scalars().all()

    if not golds:
        return "Güncel altın fiyatları bulunamadı."

    lines = ["Güncel Altın Fiyatları:"]
    for g in golds:
        lines.append(f"• {g.name}: Alış {g.buying} TL, Satış {g.selling} TL")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────
# 8. SON DEPREMLER
# ─────────────────────────────────────────────────────────────────────

async def get_recent_earthquakes(*, session: AsyncSession) -> str:
    """Son 5 depremi listeler."""
    quakes = (
        await session.execute(
            select(EarthquakesCache)
            .order_by(EarthquakesCache.event_date.desc())
            .limit(5)
        )
    ).scalars().all()

    if not quakes:
        return "Son deprem verisi bulunamadı."

    lines = ["Son 5 Deprem:"]
    for q in quakes:
        lines.append(
            f"• {q.magnitude} büyüklüğünde — {q.location} "
            f"(Derinlik: {q.depth} km, Tarih: {q.event_date})"
        )

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────
# 9. ACİL DURUM TELEFONLARI
# ─────────────────────────────────────────────────────────────────────

async def get_emergency_contacts(*, session: AsyncSession) -> str:
    """Acil durum ve önemli telefon numaralarını listeler."""
    contacts = (
        await session.execute(
            select(EmergencyContact).order_by(EmergencyContact.priority.asc())
        )
    ).scalars().all()

    if not contacts:
        return "Acil durum numaraları bulunamadı."

    lines = ["Acil ve Önemli Numaralar:"]
    for c in contacts:
        desc = f" — {c.description}" if c.description else ""
        lines.append(f"• {c.name}: {c.phone}{desc}")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────
# 10. HABER / ETKİNLİK / DUYURU / PROJE / İŞ İLANI / KESİNTİ / PAZAR
def _extract_search_terms(query_str: str) -> list[str]:
    stop_words = {
        "nedir", "neler", "nerede", "nasıl", "hangi", "var", "mi", "mı", "mu", "mü", "aliağa", "aliaga",
        "haber", "etkinlik", "kesinti", "duyuru", "proje", "ilan", "hakkında", "bilgi", "günü", "tarihi",
        "saati", "saatleri", "son", "yeni", "güncel", "ve", "veya", "ile", "de", "da", "için", "olan"
    }
    words = re.findall(r"\w+", query_str.lower())
    return [w for w in words if len(w) >= 3 and w not in stop_words]


async def search_news_events(query: str, *, session: AsyncSession) -> str:
    """Haberler, etkinlikler, duyurular, belediye projeleri, iş ilanları,
    kesinti bilgileri ve semt pazarlarını arar.

    Hem SQL keyword araması hem de RAG vektör araması yaparak
    en kapsamlı sonucu döndürür.
    """
    results: list[str] = []
    query_lower = query.lower().strip()

    # Kategori algılama
    has_news = any(w in query_lower for w in ["haber", "gelişme", "son dakika", "manşet", "gazete", "duyurulan", "bildirilen"])
    has_events = any(w in query_lower for w in ["etkinlik", "konser", "tiyatro", "sinema", "festival", "gösteri", "sergi", "söyleşi", "konferans", "aktivite", "seminer"])
    has_announcements = any(w in query_lower for w in ["duyuru", "askı", "ihale", "ilan", "duyurusu"])
    has_projects = any(w in query_lower for w in ["proje", "yatırım", "inşaat", "altyapı", "peyzaj", "imar", "çalışma"])
    has_jobs = any(w in query_lower for w in ["iş", "kariyer", "istihdam", "eleman", "personel", "istihdamı", "başvuru"])
    has_outages = any(w in query_lower for w in ["kesinti", "arıza", "kesik", "su gitmedi", "elektrik gitti", "izsu", "gdz", "gdzelektrik", "kesintisi"])
    has_markets = any(w in query_lower for w in ["pazar", "market", "semt", "tezgah", "alışveriş", "pazarı"])

    is_general = not (has_news or has_events or has_announcements or has_projects or has_jobs or has_outages or has_markets)
    terms = _extract_search_terms(query)

    # ── SQL ile hızlı keyword arama ──

    # 1. Haberler
    if has_news or is_general:
        stmt = select(News).order_by(News.published_at.desc())
        if terms:
            stmt = stmt.where(or_(*(
                [News.title.ilike(f"%{t}%") for t in terms] +
                [News.content.ilike(f"%{t}%") for t in terms]
            )))
        news_rows = (await session.execute(stmt.limit(5 if terms else 3))).scalars().all()
        if news_rows:
            results.append("Son Haberler:")
            for n in news_rows:
                results.append(f"• {n.title} ({n.published_at})")
                if n.content:
                    results.append(f"  {n.content[:300]}...")

    # 2. Etkinlikler
    if has_events or is_general:
        stmt = select(Event).order_by(Event.event_date.desc())
        if terms:
            stmt = stmt.where(or_(*(
                [Event.title.ilike(f"%{t}%") for t in terms] +
                [Event.description.ilike(f"%{t}%") for t in terms] +
                [Event.location.ilike(f"%{t}%") for t in terms]
            )))
        events = (await session.execute(stmt.limit(5 if terms else 3))).scalars().all()
        if events:
            results.append("\nEtkinlikler:")
            for e in events:
                loc = f" @ {e.location}" if e.location else ""
                results.append(f"• {e.title} ({e.event_date}){loc}")
                if e.description:
                    results.append(f"  {e.description[:200]}...")

    # 3. Duyurular
    if has_announcements or is_general:
        stmt = select(Announcement).order_by(Announcement.published_at.desc())
        if terms:
            stmt = stmt.where(or_(*(
                [Announcement.title.ilike(f"%{t}%") for t in terms] +
                [Announcement.content.ilike(f"%{t}%") for t in terms]
            )))
        announcements = (await session.execute(stmt.limit(3))).scalars().all()
        if announcements:
            results.append("\nDuyurular:")
            for a in announcements:
                results.append(f"• [{a.type}] {a.title} ({a.published_at})")

    # 4. Projeler
    if has_projects:
        stmt = select(Project).order_by(Project.created_at.desc())
        if terms:
            stmt = stmt.where(or_(*(
                [Project.title.ilike(f"%{t}%") for t in terms] +
                [Project.description.ilike(f"%{t}%") for t in terms]
            )))
        projects = (await session.execute(stmt.limit(3))).scalars().all()
        if projects:
            results.append("\nBelediye Projeleri:")
            for p in projects:
                results.append(f"• {p.title} — Durum: {p.status}")

    # 5. İş ilanları
    if has_jobs:
        stmt = select(JobListing).where(JobListing.is_active.is_(True)).order_by(JobListing.published_at.desc())
        if terms:
            stmt = stmt.where(or_(*(
                [JobListing.title.ilike(f"%{t}%") for t in terms] +
                [JobListing.description.ilike(f"%{t}%") for t in terms] +
                [JobListing.company.ilike(f"%{t}%") for t in terms]
            )))
        jobs = (await session.execute(stmt.limit(3))).scalars().all()
        if jobs:
            results.append("\nİş İlanları:")
            for j in jobs:
                company = j.company or "Firma belirtilmemiş"
                results.append(f"• {j.title} — {company}")

    # 6. Kesintiler
    if has_outages:
        stmt = select(UtilityOutage).order_by(UtilityOutage.start_date.desc())
        if terms:
            stmt = stmt.where(or_(*(
                [UtilityOutage.neighborhood.ilike(f"%{t}%") for t in terms] +
                [UtilityOutage.district.ilike(f"%{t}%") for t in terms] +
                [UtilityOutage.description.ilike(f"%{t}%") for t in terms]
            )))
        outages = (await session.execute(stmt.limit(5 if terms else 3))).scalars().all()
        if outages:
            results.append("\nGüncel Kesintiler:")
            for o in outages:
                area = o.neighborhood or o.district or "Konum belirtilmemiş"
                results.append(f"• {o.type.upper()} kesintisi — {area}")
                if o.description:
                    results.append(f"  {o.description[:200]}")

    # 7. Semt pazarları
    if has_markets:
        stmt = select(StreetMarket)
        if terms:
            stmt = stmt.where(or_(*(
                [StreetMarket.name.ilike(f"%{t}%") for t in terms] +
                [StreetMarket.day_of_week.ilike(f"%{t}%") for t in terms] +
                [StreetMarket.neighborhood.ilike(f"%{t}%") for t in terms]
            )))
        markets = (await session.execute(stmt)).scalars().all()
        if markets:
            results.append("\nSemt Pazarları:")
            for m in markets:
                results.append(f"• {m.name} — {m.day_of_week} ({m.neighborhood or ''})")

    # ── RAG ile derin arama ──
    source_types = []
    if has_news or is_general:
        source_types.append("news")
    if has_events or is_general:
        source_types.append("event")
    if has_announcements or is_general:
        source_types.append("announcement")
    if has_projects:
        source_types.append("project")
    if has_jobs:
        source_types.append("job")
    if has_outages:
        source_types.append("outage")

    if source_types:
        rag_chunks = await search_similar_chunks(
            session=session,
            query=query,
            limit=5,
            min_similarity=settings.RAG_MIN_SIMILARITY,
            source_types=source_types,
        )
        if rag_chunks:
            results.append("\nDetaylı İçerik Araması:")
            for chunk in rag_chunks:
                meta = chunk.get("metadata") or {}
                title = meta.get("title", "İçerik")
                content = chunk.get("content", "")[:400]
                results.append(f"• {title}: {content}")

    if not results:
        return "Bu konuda güncel haber, etkinlik veya duyuru bulunamadı."

    return "\n".join(results)


# ─────────────────────────────────────────────────────────────────────
# 11. ULAŞIM SEFER SAATLERİ (İZBAN & Feribot)
# ─────────────────────────────────────────────────────────────────────

async def get_transport_schedules(
    mode: str,
    station: str | None = None,
    direction: str | None = None,
    *,
    session: AsyncSession,
) -> str:
    """İZBAN tren kalkış saatleri veya Feribot sefer saatlerini doğrudan
    SQL veritabanından çekip formatlı şekilde döndürür.
    """
    mode_lower = mode.lower().strip()
    if "izban" in mode_lower:
        stmt = select(IzbanSchedule).order_by(IzbanSchedule.departure_time.asc())
        if station:
            stmt = stmt.where(IzbanSchedule.station.ilike(f"%{station}%"))
        if direction:
            stmt = stmt.where(IzbanSchedule.direction.ilike(f"%{direction}%"))
        rows = (await session.execute(stmt)).scalars().all()
        if not rows:
            return "İZBAN sefer saatleri için kayıt bulunamadı."

        lines = []
        grouped: dict[tuple[str, str, str], list[str]] = {}
        for r in rows:
            dep_time = r.departure_time.strftime("%H:%M") if r.departure_time else ""
            key = (r.station or "Aliağa", r.direction or "Bilinmiyor", r.day_type or "her_gun")
            grouped.setdefault(key, []).append(dep_time)

        for (st, dir_name, dt), times in grouped.items():
            day_str = "Her Gün" if dt == "her_gun" else dt
            lines.append(f"İZBAN Kalkış Saatleri ({st} İstasyonu -> {dir_name}) [{day_str}]:")
            chunks = [times[i : i + 6] for i in range(0, len(times), 6)]
            for chunk in chunks:
                lines.append("  " + "   ".join(f"• {t}" for t in chunk))
        return "\n".join(lines)

    elif any(w in mode_lower for w in ["ferry", "feribot", "vapur"]):
        stmt = select(FerrySchedule).order_by(FerrySchedule.departure_time.asc())
        rows = (await session.execute(stmt)).scalars().all()
        if not rows:
            return "Feribot sefer saatleri için kayıt bulunamadı."

        lines = ["Aliağa Feribot Seferleri:"]
        for r in rows:
            dep_time = r.departure_time.strftime("%H:%M") if r.departure_time else ""
            day_str = "Her Gün" if r.day_type == "her_gun" else (r.day_type or "")
            price = f" (Ücret: {r.price_info})" if r.price_info else ""
            duration = f" (Süre: {r.duration})" if r.duration else ""
            company = f" ({r.company})" if r.company else ""
            lines.append(f"• {r.route} — Kalkış: {dep_time} [{day_str}]{company}{duration}{price}")
        return "\n".join(lines)

    else:
        return "Desteklenmeyen ulaşım türü. Lütfen 'izban' veya 'ferry' (feribot) belirtin."


# ─────────────────────────────────────────────────────────────────────
# 12. TAKSİ DURAKLARI
# ─────────────────────────────────────────────────────────────────────

async def get_taxi_stands(name: str | None = None, *, session: AsyncSession) -> str:
    """Aliağa taksi duraklarını isim, telefon, adres ve çalışma
    saatleriyle birlikte doğrudan SQL veritabanından çekip listeler.
    """
    stmt = select(TaxiStand).order_by(TaxiStand.name.asc())
    if name:
        stmt = stmt.where(TaxiStand.name.ilike(f"%{name}%"))
    stands = (await session.execute(stmt)).scalars().all()
    if not stands:
        return "Aliağa taksi durakları verisi bulunamadı."

    lines = ["Aliağa Taksi Durakları:"]
    for s in stands:
        parts = [f"• {s.name}"]
        if s.phone:
            parts.append(f"  Tel: {s.phone}")
        if s.address:
            parts.append(f"  Adres: {s.address}")
        is_24_str = "7/24 Açık" if s.is_24h else "Belirli saatlerde açık"
        parts.append(f"  Hizmet: {is_24_str}")
        lines.append("\n".join(parts))

    return "\n\n".join(lines)


# ─────────────────────────────────────────────────────────────────────
# 13. POSTA KODLARI
# ─────────────────────────────────────────────────────────────────────

async def get_postal_codes(neighborhood: str | None = None, *, session: AsyncSession) -> str:
    """Aliağa mahallelerinin posta kodlarını doğrudan SQL veritabanından çeker.
    İsteğe bağlı olarak mahalle adına göre arama yapabilir.
    """
    stmt = select(PostalCode).order_by(PostalCode.neighborhood.asc())
    if neighborhood:
        stmt = stmt.where(PostalCode.neighborhood.ilike(f"%{neighborhood}%"))
    rows = (await session.execute(stmt)).scalars().all()
    if not rows:
        return "Belirtilen mahalle için posta kodu bulunamadı."

    lines = ["Aliağa Mahalle Posta Kodları:"]
    for r in rows:
        lines.append(f"• {r.neighborhood} Mahallesi: {r.postal_code}")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────
# ARAÇ KAYDI — Ajan servisinin kullanacağı fonksiyon haritası
# ─────────────────────────────────────────────────────────────────────

TOOL_FUNCTIONS: dict[str, callable] = {
    "search_knowledge": search_knowledge,
    "get_duty_pharmacies": get_duty_pharmacies,
    "get_weather": get_weather,
    "get_prayer_times": get_prayer_times,
    "get_fuel_prices": get_fuel_prices,
    "get_currency_rates": get_currency_rates,
    "get_gold_prices": get_gold_prices,
    "get_recent_earthquakes": get_recent_earthquakes,
    "get_emergency_contacts": get_emergency_contacts,
    "search_news_events": search_news_events,
    "get_transport_schedules": get_transport_schedules,
    "get_taxi_stands": get_taxi_stands,
    "get_postal_codes": get_postal_codes,
}
