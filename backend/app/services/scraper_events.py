"""
AliagaAI - aliaga.bel.tr etkinlikler scraper'i.

Belediye sitesinden resmi etkinlik takvimini ceker, events tablosuna kaydeder.
"""
from datetime import date, datetime
import re
from typing import Any

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Event
from app.services.scraper_base import BaseScraper


def _parse_event_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        # Example: 19.05.2026 or 19 Mayıs 2026
        from app.services.scraper_news import _parse_news_date
        return _parse_news_date(value)
    except Exception:
        return None


class EventsScraper(BaseScraper):
    """aliaga.bel.tr /etkinlikler sayfasindan etkinlik ceker."""

    LIST_URL = "/etkinlikler"

    async def scrape(self, **kwargs) -> list[dict[str, Any]]:
        """Etkinlik listesini ceker."""
        items: list[dict[str, Any]] = []
        soup = await self._fetch_page(self.LIST_URL)
        if not soup:
            return items

        cards = soup.select(".item, .etkinlik, a[href*='/etkinlik/']")
        seen_urls = set()

        for card in cards:
            try:
                link_el = card if card.name == "a" else card.select_one("a[href*='/etkinlik/']")
                if not link_el:
                    continue

                href = (link_el.get("href") or "").strip()
                if not href or href == "/etkinlikler":
                    continue

                source_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"
                if source_url in seen_urls:
                    continue
                seen_urls.add(source_url)

                title_el = card.select_one(".title, h1, h2, h3, h4") if card.name != "a" else link_el.select_one(".title, h1, h2, h3, h4")
                title = self.clean_text(title_el.get_text()) if title_el else self.clean_text(link_el.get_text())
                if len(title) < 3:
                    title = "Etkinlik"

                summary_el = card.select_one(".text, .desc") if card.name != "a" else link_el.select_one(".text, .desc")
                summary = self.clean_text(summary_el.get_text()) if summary_el else None

                date_el = card.select_one(".date, .tarih") if card.name != "a" else link_el.select_one(".date, .tarih")
                event_date = _parse_event_date(self.clean_text(date_el.get_text()) if date_el else None)

                img_el = card.select_one("img") if card.name != "a" else link_el.select_one("img")
                image_url = None
                if img_el:
                    src = img_el.get("src") or img_el.get("data-src")
                    if src:
                        image_url = src if src.startswith("http") else f"{self.BASE_URL}{src}"

                from app.services.scraper_news import _classify_event_category
                category = _classify_event_category(title + " " + (summary or ""))

                items.append(
                    {
                        "title": title,
                        "description": summary,
                        "category": category,
                        "event_date": event_date,
                        "source_url": source_url,
                        "image_url": image_url,
                        "location": "Aliağa",
                    }
                )
            except Exception as e:
                logger.warning(f"Etkinlik parse hatasi: {e}")

        return items

    async def scrape_detail(self, url: str) -> str | None:
        """Etkinlik detayini ceker."""
        soup = await self._fetch_page(url)
        if not soup:
            return None

        content_el = soup.select_one(".content, .etkinlik-detay, article")
        if content_el:
            for el in content_el.select("script, style, nav"):
                el.decompose()
            return self.clean_text(content_el.get_text(" "))
        return None


async def scrape_and_save_events(session: AsyncSession) -> int:
    """Etkinlikleri ceker, DB'ye kaydeder."""
    scraper = EventsScraper()
    items = await scraper.scrape()

    count = 0
    for item in items:
        existing = await session.execute(select(Event).where(Event.source_url == item["source_url"]).limit(1))
        if existing.scalars().first():
            continue

        content = None
        if item.get("source_url"):
            content = await scraper.scrape_detail(item["source_url"])

        event = Event(
            title=item["title"],
            description=content or item.get("description"),
            location=item.get("location"),
            category=item.get("category"),
            event_date=item.get("event_date") or date.today(),
            source_url=item.get("source_url"),
            image_url=item.get("image_url"),
        )
        session.add(event)
        count += 1

    if count > 0:
        await session.flush()
    logger.info(f"Etkinlik: {count} yeni etkinlik kaydedildi.")
    return count
