"""
AliagaAI - aliaga.bel.tr haber scraper'i.

Belediye sitesinden haberleri ceker, news tablosuna kaydeder.
Ayrica etkinlik anahtar kelimelerine gore events tablosuna turetim yapar.
"""
from datetime import date, datetime
import re
from typing import Any

from loguru import logger
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Event, News
from app.services.scraper_base import BaseScraper


TR_MONTHS = {
    "ocak": 1,
    "subat": 2,
    "şubat": 2,
    "mart": 3,
    "nisan": 4,
    "mayis": 5,
    "mayıs": 5,
    "haziran": 6,
    "temmuz": 7,
    "agustos": 8,
    "ağustos": 8,
    "eylul": 9,
    "eylül": 9,
    "ekim": 10,
    "kasim": 11,
    "kasım": 11,
    "aralik": 12,
    "aralık": 12,
}

EVENT_KEYWORDS = (
    "etkinlik",
    "festival",
    "konser",
    "tiyatro",
    "sov",
    "şov",
    "senlik",
    "şenlik",
    "turnuva",
    "yarisma",
    "yarışma",
    "gosteri",
    "gösteri",
    "kutlama",
    "workshop",
    "atolye",
    "atölye",
)


def _normalize_tr(text: str) -> str:
    value = (text or "").lower()
    table = str.maketrans("çğıöşü", "cgiosu")
    return value.translate(table)


def _parse_news_date(value: str | None) -> date | None:
    """
    Ornekler:
      23 Nisan 2026 | 19:49
      23.04.2026
    """
    if not value:
        return None

    clean = " ".join(value.split()).strip()
    clean = clean.split("|")[0].strip()

    # dd.mm.yyyy
    m = re.search(r"(\d{1,2})[./-](\d{1,2})[./-](\d{4})", clean)
    if m:
        try:
            return datetime(int(m.group(3)), int(m.group(2)), int(m.group(1))).date()
        except ValueError:
            pass

    # dd <ay> yyyy
    m = re.search(r"(\d{1,2})\s+([a-zA-ZçğıöşüÇĞİÖŞÜ]+)\s+(\d{4})", clean)
    if m:
        day = int(m.group(1))
        month_name = _normalize_tr(m.group(2))
        month = TR_MONTHS.get(month_name)
        year = int(m.group(3))
        if month:
            try:
                return datetime(year, month, day).date()
            except ValueError:
                pass

    return None


def _classify_event_category(text: str) -> str:
    low = _normalize_tr(text)
    if "konser" in low:
        return "konser"
    if "tiyatro" in low:
        return "tiyatro"
    if "festival" in low or "senlik" in low:
        return "festival"
    if "turnuva" in low or "yarisma" in low:
        return "spor"
    return "etkinlik"


class NewsScraper(BaseScraper):
    """aliaga.bel.tr /haberler sayfasindan haber ceker."""

    LIST_URL = "/haberler"
    MAX_PAGES = 12

    async def scrape(self, **kwargs) -> list[dict[str, Any]]:
        """Haber listesini ceker ve dict listesi doner."""
        max_pages = int(kwargs.get("max_pages") or self.MAX_PAGES)
        items: list[dict[str, Any]] = []
        seen_urls: set[str] = set()

        for page in range(1, max_pages + 1):
            url = self.LIST_URL if page == 1 else f"{self.LIST_URL}?page={page}"
            soup = await self._fetch_page(url)
            if not soup:
                continue

            cards = soup.select(".tum-haberler .item")
            if not cards:
                cards = soup.select("a[href*='/haber/']")

            page_hits = 0
            for card in cards:
                try:
                    link_el = card if card.name == "a" else card.select_one("a[href*='/haber/']")
                    if not link_el:
                        continue

                    href = (link_el.get("href") or "").strip()
                    if not href or "/haber/" not in href:
                        continue

                    source_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"
                    if source_url in seen_urls:
                        continue
                    seen_urls.add(source_url)

                    title_el = card.select_one(".title") if card.name != "a" else link_el.select_one(".title")
                    if not title_el:
                        title_el = link_el.select_one("h1, h2, h3, h4")
                    title = self.clean_text(title_el.get_text()) if title_el else self.clean_text(link_el.get_text())
                    if len(title) < 4:
                        continue

                    summary_el = card.select_one(".text") if card.name != "a" else link_el.select_one(".text")
                    summary = self.clean_text(summary_el.get_text()) if summary_el else None

                    date_el = card.select_one(".date") if card.name != "a" else link_el.select_one(".date")
                    published_at = _parse_news_date(self.clean_text(date_el.get_text()) if date_el else None)

                    slug = href.split("/haber/")[-1].rstrip("/") if "/haber/" in href else None

                    img_el = card.select_one("img") if card.name != "a" else link_el.select_one("img")
                    image_url = None
                    if img_el:
                        src = img_el.get("src") or img_el.get("data-src")
                        if src:
                            image_url = src if src.startswith("http") else f"{self.BASE_URL}{src}"

                    items.append(
                        {
                            "title": title,
                            "slug": slug,
                            "source_url": source_url,
                            "image_url": image_url,
                            "summary": summary,
                            "published_at": published_at,
                        }
                    )
                    page_hits += 1
                except Exception as e:
                    logger.warning(f"Haber parse hatasi ({url}): {e}")

            if page_hits == 0:
                # Sonraki sayfalar bos ise gereksiz istekleri kes
                break

        logger.info(f"Haber scraper: {len(items)} haber bulundu.")
        return items

    async def scrape_detail(self, url: str) -> str | None:
        """Haber detay sayfasindan icerik metnini ceker."""
        soup = await self._fetch_page(url)
        if not soup:
            return None

        content_el = soup.select_one(
            ".haber-detay, .content, article .entry-content, .post-content, .detail-content, .sayfa-icerik"
        )
        if content_el:
            for el in content_el.select("script, style, nav, footer, .social-share"):
                el.decompose()
            text_blocks = [self.clean_text(p.get_text(" ")) for p in content_el.select("p, li")]
            text_blocks = [b for b in text_blocks if len(b) >= 10]
            if text_blocks:
                return "\n".join(text_blocks)
            return self.clean_text(content_el.get_text(" "))

        body_text = self.clean_text(soup.get_text(" "))
        return body_text[:2500] if body_text else None


async def scrape_and_save_news(session: AsyncSession) -> int:
    """Haberleri ceker, detaylarini alir ve DB'ye kaydeder."""
    scraper = NewsScraper()
    items = await scraper.scrape(max_pages=12)

    count = 0
    for item in items:
        existing = await session.execute(select(News).where(News.source_url == item["source_url"]).limit(1))
        if existing.scalars().first():
            continue

        content = None
        if item.get("source_url"):
            content = await scraper.scrape_detail(item["source_url"])

        news = News(
            title=item["title"],
            slug=item.get("slug"),
            content=content or item.get("summary"),
            source_url=item.get("source_url"),
            image_url=item.get("image_url"),
            category="belediye_haber",
            published_at=item.get("published_at") or date.today(),
        )
        session.add(news)
        count += 1

    if count > 0:
        await session.flush()
    logger.info(f"Haber: {count} yeni haber kaydedildi.")
    return count


async def sync_events_from_news(session: AsyncSession, limit: int = 400) -> int:
    """Haberlerden etkinlik anahtar kelimelerine gore events tablosu uretir."""
    rows = (
        (
            await session.execute(
                select(News).order_by(desc(News.published_at), desc(News.id)).limit(limit)
            )
        )
        .scalars()
        .all()
    )

    inserted = 0
    for row in rows:
        payload = f"{row.title or ''} {row.content or ''}"
        norm = _normalize_tr(payload)
        if not any(k in norm for k in EVENT_KEYWORDS):
            continue

        if row.source_url:
            existing = (
                await session.execute(select(Event).where(Event.source_url == row.source_url).limit(1))
            ).scalars().first()
            if existing:
                continue

        description = (row.content or row.title or "").strip()
        if not description:
            continue

        event = Event(
            title=(row.title or "Etkinlik")[:500],
            description=description[:4000],
            location="Aliağa",
            category=_classify_event_category(payload),
            event_date=row.published_at,
            end_date=None,
            event_time=None,
            source_url=row.source_url,
            image_url=row.image_url,
        )
        session.add(event)
        inserted += 1

    if inserted > 0:
        await session.flush()
    logger.info(f"Etkinlik turetimi: {inserted} yeni event eklendi.")
    return inserted

