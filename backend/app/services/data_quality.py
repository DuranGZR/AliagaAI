from __future__ import annotations

import re
from collections import defaultdict

from loguru import logger
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.city import UtilityOutage
from app.models.content import Obituary


_TR_MAP = str.maketrans("çğıöşü", "cgiosu")


def _normalize_tr(text: str | None) -> str:
    return (text or "").lower().translate(_TR_MAP)


def _extract_neighborhood_from_description(text: str | None) -> str | None:
    if not text:
        return None

    # "Atatürk Mah.", "Yenişakran Mah." gibi mahalle kalıpları
    matches = re.findall(
        r"([A-Za-zÇĞİÖŞÜçğıöşü]+(?:[\s\-][A-Za-zÇĞİÖŞÜçğıöşü]+){0,2})\s+Mah\.?",
        text,
        flags=re.IGNORECASE,
    )
    if not matches:
        return None

    blocked = {"izmir", "aliaga", "aliağa", "elektrik", "su", "kesinti", "ariza", "arıza"}
    for m in matches:
        val = " ".join(m.split()).strip(" -,:;")
        norm = _normalize_tr(val)
        if len(val) < 4:
            continue
        if re.match(r"^[a-zA-ZçğıöşüÇĞİÖŞÜ]\s+", val):
            continue
        if any(tok in norm.split() for tok in blocked):
            continue
        return val.title()[:100]
    return None


def _is_obituary_like(text: str) -> bool:
    norm = _normalize_tr(text)
    positive = [
        "vefat",
        "topraga ver",
        "son yolculug",
        "cenaze",
        "defin",
        "rahmetle",
    ]
    return any(p in norm for p in positive)


def _is_noisy_obituary(text: str) -> bool:
    norm = _normalize_tr(text)
    negative = [
        "trafik kazasi",
        "is kazasi",
        "gemi sokum",
        "otomobil",
        "yarali",
        "gozaltina",
        "tutuklandi",
        "su kesintisi",
        "elektrik kesintisi",
        "ihale",
        "kampanya",
        "spor musabakasi",
        "maci",
        "festival programi",
        "hava durumu",
    ]
    return any(n in norm for n in negative)


def _normalize_person_name(name: str | None) -> str:
    if not name:
        return ""
    cleaned = re.sub(r"\s+", " ", name).strip(" -:|,")
    return cleaned[:255]


def _is_valid_person_name(name: str) -> bool:
    if len(name) < 5:
        return False
    # 2-6 kelimelik kişi adı formatına yakın kontrol
    parts = [p for p in re.split(r"\s+", name) if p]
    if not (2 <= len(parts) <= 6):
        return False
    if any(len(p) < 2 for p in parts):
        return False
    return True


async def clean_utility_outages(session: AsyncSession) -> dict[str, int]:
    rows = (await session.execute(select(UtilityOutage))).scalars().all()
    updated = 0
    deleted = 0

    # (type, description) bazında duplicate temizliği
    groups: dict[tuple[str, str], list[UtilityOutage]] = defaultdict(list)
    for row in rows:
        key = (row.type or "", row.description or "")
        groups[key].append(row)

    for items in groups.values():
        if len(items) <= 1:
            continue
        items_sorted = sorted(items, key=lambda x: x.id)
        for dup in items_sorted[1:]:
            await session.delete(dup)
            deleted += 1

    # Mahalle adı normalize/temizle
    rows2 = (await session.execute(select(UtilityOutage))).scalars().all()
    for row in rows2:
        candidate = _extract_neighborhood_from_description(row.description)
        new_neighborhood = candidate if candidate else None
        if row.neighborhood != new_neighborhood:
            row.neighborhood = new_neighborhood
            updated += 1

    await session.flush()
    return {"updated": updated, "deleted": deleted}


async def clean_obituaries(session: AsyncSession) -> dict[str, int]:
    rows = (await session.execute(select(Obituary))).scalars().all()
    updated = 0
    deleted = 0

    for row in rows:
        merged_text = " ".join(
            x for x in [row.name or "", row.details or "", row.funeral_location or ""] if x
        ).strip()
        source_norm = _normalize_tr(row.source or "")

        # Resmi kaynak değilse daha sıkı kalite filtresi
        is_official = "izmir bsb" in source_norm or "mezarlik bilgi sistemi" in source_norm

        if not is_official:
            if not _is_obituary_like(merged_text) or _is_noisy_obituary(merged_text):
                await session.delete(row)
                deleted += 1
                continue

        normalized_name = _normalize_person_name(row.name)
        if not _is_valid_person_name(normalized_name):
            await session.delete(row)
            deleted += 1
            continue

        if row.name != normalized_name:
            row.name = normalized_name
            updated += 1

        # Aliağa bağlamı için boş alanları normalize et
        if not row.funeral_location:
            row.funeral_location = "Aliağa"
            updated += 1

        if row.neighborhood:
            row.neighborhood = row.neighborhood[:100]

    await session.flush()
    return {"updated": updated, "deleted": deleted}


async def run_data_quality_pass(session: AsyncSession) -> dict[str, dict[str, int]]:
    outage_stats = await clean_utility_outages(session)
    obituary_stats = await clean_obituaries(session)
    await session.commit()

    stats = {
        "utility_outages": outage_stats,
        "obituaries": obituary_stats,
    }
    logger.info(f"Data quality pass tamamlandı: {stats}")
    return stats
