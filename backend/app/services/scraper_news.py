"""
AliağaAI — aliaga.bel.tr haber scraper'ı.

Belediye sitesinden haberleri çekerek news tablosuna kaydeder.
"""
from datetime import date
from typing import Any

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import News
from app.services.scraper_base import BaseScraper


class NewsScraper(BaseScraper):
    """aliaga.bel.tr /haberler sayfasından haber çeker."""

    LIST_URL = "/haberler"

    async def scrape(self, **kwargs) -> list[dict[str, Any]]:
        """Haber listesini çeker ve dict listesi döner."""
        soup = await self._fetch_page(self.LIST_URL)
        if not soup:
            return []

        items = []
        # Belediye sitesindeki haber kartlarını bul
        cards = soup.select("div.card, div.haber-item, article, .news-item")
        if not cards:
            # Alternatif seçiciler dene
            cards = soup.select("a[href*='/haber/']")

        for card in cards[:20]:  # Son 20 haber
            try:
                # Başlık ve link
                link_el = card if card.name == "a" else card.select_one("a[href*='/haber/']")
                if not link_el:
                    continue

                href = link_el.get("href", "")
                if not href or "/haber/" not in href:
                    continue

                title_el = link_el.select_one("h2, h3, h4, .card-title, .title") or link_el
                title = self.clean_text(title_el.get_text())
                if not title:
                    continue

                # Slug ve URL
                source_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"
                slug = href.split("/haber/")[-1].rstrip("/") if "/haber/" in href else None

                # Resim
                img_el = card.select_one("img")
                image_url = None
                if img_el:
                    src = img_el.get("src") or img_el.get("data-src")
                    if src:
                        image_url = src if src.startswith("http") else f"{self.BASE_URL}{src}"

                items.append({
                    "title": title,
                    "slug": slug,
                    "source_url": source_url,
                    "image_url": image_url,
                })
            except Exception as e:
                logger.warning(f"Haber parse hatası: {e}")
                continue

        logger.info(f"Haber scraper: {len(items)} haber bulundu.")
        return items

    async def scrape_detail(self, url: str) -> str | None:
        """Haber detay sayfasından içerik metnini çeker."""
        soup = await self._fetch_page(url)
        if not soup:
            return None

        # İçerik alanını bul
        content_el = soup.select_one(
            ".haber-detay, .content, article .entry-content, .post-content, .detail-content"
        )
        if content_el:
            # Gereksiz elemanları temizle
            for el in content_el.select("script, style, nav, footer, .social-share"):
                el.decompose()
            return self.clean_text(content_el.get_text())

        return None


async def scrape_and_save_news(session: AsyncSession) -> int:
    """Haberleri çeker, detaylarını alır ve DB'ye kaydeder."""
    scraper = NewsScraper()
    items = await scraper.scrape()

    count = 0
    for item in items:
        # Aynı URL zaten var mı kontrol et
        existing = await session.execute(
            select(News).where(News.source_url == item["source_url"]).limit(1)
        )
        if existing.scalars().first():
            continue

        # Detay sayfasını çek
        content = None
        if item.get("source_url"):
            content = await scraper.scrape_detail(item["source_url"])

        news = News(
            title=item["title"],
            slug=item.get("slug"),
            content=content,
            source_url=item.get("source_url"),
            image_url=item.get("image_url"),
            published_at=date.today(),
        )
        session.add(news)
        count += 1

    if count > 0:
        await session.flush()
    logger.info(f"Haber: {count} yeni haber kaydedildi.")
    return count
