from datetime import datetime, timedelta
import re

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.city import UtilityOutage
from app.services.scraper_base import BaseScraper


DATE_RE = re.compile(r"(\d{1,2}[./-]\d{1,2}[./-]\d{4})")


def _normalize_tr(text: str) -> str:
    value = (text or "").lower()
    table = str.maketrans("çğıöşü", "cgiosu")
    return value.translate(table)


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    m = DATE_RE.search(value)
    if not m:
        return None
    raw = m.group(1).replace("/", ".").replace("-", ".")
    parts = raw.split(".")
    try:
        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
        return datetime(year, month, day)
    except Exception:
        return None


def _extract_neighborhoods(text: str) -> str | None:
    # Mahalle adini metinden cikarir; sadece 1-3 kelimelik adaylari alir.
    matches = re.findall(
        r"([A-Za-zÇĞİÖŞÜçğıöşü]+(?:[\s\-][A-Za-zÇĞİÖŞÜçğıöşü]+){0,2})\s+Mah\.?",
        text,
        flags=re.IGNORECASE,
    )
    if not matches:
        return None

    blocked = {"izmir", "aliaga", "aliağa", "elektrik", "su", "kesintisi", "ariza", "arıza"}
    for m in matches:
        value = " ".join(m.split()).strip(" -,:;")
        norm = _normalize_tr(value)
        if len(value) < 4:
            continue
        if any(tok in norm.split() for tok in blocked):
            continue
        if re.search(r"\d", value):
            continue
        return value[:100]

    return None


class OutageScraper(BaseScraper):
    """Aliağa su/elektrik kesintilerini guncelkesintiler.com listesinden ceker."""

    def __init__(self):
        super().__init__()
        self.sources = {
            "su": "https://www.guncelkesintiler.com/izmir/aliaga/su-kesintisi/",
            "elektrik": "https://www.guncelkesintiler.com/izmir/aliaga/elektrik-kesintisi/",
        }
        self.max_pages = 5

    async def _fetch_cards(self, base_url: str) -> list[tuple[str, str, str]]:
        """(title, body, detail_url) listesi dondurur."""
        results: list[tuple[str, str, str]] = []
        seen: set[str] = set()

        for page in range(1, self.max_pages + 1):
            url = base_url if page == 1 else f"{base_url}?page={page}"
            soup = await self._fetch_page(url)
            if not soup:
                continue

            cards = soup.select(".card")
            page_hits = 0
            for card in cards:
                title = self.clean_text((card.select_one(".card-title") or card).get_text(" "))
                body = self.clean_text((card.select_one(".card-content") or card).get_text(" "))
                a = card.select_one("a[href]")
                detail_url = ""
                if a:
                    href = (a.get("href") or "").strip()
                    detail_url = href if href.startswith("http") else f"https://www.guncelkesintiler.com{href}"

                key = detail_url or f"{title}|{body[:120]}"
                if key in seen:
                    continue
                seen.add(key)

                if len(title) < 5 and len(body) < 20:
                    continue
                if "alia" not in _normalize_tr(f"{title} {body}"):
                    continue

                results.append((title, body, detail_url))
                page_hits += 1

            if page_hits == 0:
                break

        return results

    async def fetch_outages(self, session: AsyncSession, outage_type: str) -> int:
        count = 0
        source_url = self.sources[outage_type]
        cards = await self._fetch_cards(source_url)
        logger.info(f"Kesinti scraper ({outage_type}): {len(cards)} aday kayit bulundu.")

        for title, body, detail_url in cards:
            description = " ".join(x for x in [title, body] if x).strip()[:5000]
            if len(description) < 20:
                continue

            start_date = _parse_date(f"{title} {body}") or datetime.now()
            end_date = start_date + timedelta(hours=3)
            neighborhood = _extract_neighborhoods(description)

            existing = (
                await session.execute(
                    select(UtilityOutage).where(
                        UtilityOutage.type == outage_type,
                        UtilityOutage.description == description,
                    )
                )
            ).scalars().first()
            if existing:
                continue

            session.add(
                UtilityOutage(
                    type=outage_type,
                    district="Aliağa",
                    neighborhood=neighborhood,
                    description=description,
                    start_date=start_date,
                    end_date=end_date,
                    source="guncelkesintiler" if detail_url else "guncelkesintiler",
                )
            )
            count += 1

        if count > 0:
            await session.commit()
            logger.info(f"{outage_type} kesintisi: {count} yeni kayit eklendi.")
        else:
            logger.debug(f"{outage_type} icin yeni kesinti kaydi bulunamadi.")

        return count

    async def scrape(self, **kwargs) -> list[dict]:
        return []


async def scrape_outages(session: AsyncSession):
    scraper = OutageScraper()
    await scraper.fetch_outages(session, "su")
    await scraper.fetch_outages(session, "elektrik")

