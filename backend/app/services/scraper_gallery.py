"""
AliagaAI - aliaga.bel.tr galeri scraper'i.

Belediye sitesinden fotograf galerilerini ceker, galleries ve gallery_images tablolarina kaydeder.
"""
from datetime import date, datetime
from typing import Any

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.content import Gallery, GalleryImage
from app.services.scraper_base import BaseScraper


class GalleryScraper(BaseScraper):
    """aliaga.bel.tr fotograf galerilerini ceker."""

    LIST_URL = "/galeri"

    async def scrape(self, **kwargs) -> list[dict[str, Any]]:
        """Galeri listesini ceker."""
        items: list[dict[str, Any]] = []
        soup = await self._fetch_page(self.LIST_URL)
        if not soup:
            return items

        # Sitedeki galeri ogelerini bulmayi deneriz
        # Sitede genelde .item, .galeri-item gibi classlar kullanilir
        cards = soup.select(".item, .album, a[href*='/galeri/']")
        seen_urls = set()

        for card in cards:
            try:
                link_el = card if card.name == "a" else card.select_one("a[href*='/galeri/']")
                if not link_el:
                    continue

                href = (link_el.get("href") or "").strip()
                if not href or href == "/galeri" or href == "/galeri/video-galeri":
                    continue

                source_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"
                if source_url in seen_urls:
                    continue
                seen_urls.add(source_url)

                title_el = card.select_one(".title, h1, h2, h3, h4") if card.name != "a" else link_el.select_one(".title, h1, h2, h3, h4")
                title = self.clean_text(title_el.get_text()) if title_el else self.clean_text(link_el.get_text())
                if len(title) < 3:
                    title = "Galeri"

                slug = href.split("/")[-1]

                img_el = card.select_one("img") if card.name != "a" else link_el.select_one("img")
                cover_image_url = None
                if img_el:
                    src = img_el.get("src") or img_el.get("data-src")
                    if src:
                        cover_image_url = src if src.startswith("http") else f"{self.BASE_URL}{src}"

                items.append(
                    {
                        "title": title,
                        "slug": slug,
                        "source_url": source_url,
                        "cover_image_url": cover_image_url,
                        "publish_date": date.today(),
                    }
                )
            except Exception as e:
                logger.warning(f"Galeri parse hatasi: {e}")

        return items

    async def scrape_detail(self, url: str) -> list[dict[str, Any]]:
        """Galeri detayindan fotograflari ceker."""
        soup = await self._fetch_page(url)
        if not soup:
            return []

        images = []
        # Galeri fotograflarini iceren container (fancybox vb.)
        content_el = soup.select_one(".content, .galeri-detay, article")
        if not content_el:
            content_el = soup

        img_els = content_el.select("a[data-fancybox] img, a.fancybox img, .item img, .gallery img")
        if not img_els:
            img_els = content_el.select("img")

        seen_srcs = set()
        for img in img_els:
            src = img.get("src") or img.get("data-src") or img.parent.get("href")
            if not src or "logo" in src.lower() or "icon" in src.lower() or "banner" in src.lower():
                continue
            
            full_src = src if src.startswith("http") else f"{self.BASE_URL}{src}"
            if full_src in seen_srcs:
                continue
            seen_srcs.add(full_src)

            desc = img.get("alt") or img.get("title")
            images.append({
                "image_url": full_src,
                "description": self.clean_text(desc)
            })
            
        return images


async def scrape_and_save_galleries(session: AsyncSession) -> int:
    """Galerileri ceker, fotograflari alir ve DB'ye kaydeder."""
    scraper = GalleryScraper()
    items = await scraper.scrape()

    count = 0
    for item in items:
        existing = await session.execute(select(Gallery).where(Gallery.source_url == item["source_url"]).limit(1))
        gallery = existing.scalars().first()
        
        if not gallery:
            gallery = Gallery(
                title=item["title"],
                slug=item.get("slug"),
                cover_image_url=item.get("cover_image_url"),
                source_url=item.get("source_url"),
                publish_date=item.get("publish_date"),
            )
            session.add(gallery)
            await session.flush()
            count += 1
            
        # Fotograflari kontrol et
        if gallery.source_url:
            images_data = await scraper.scrape_detail(gallery.source_url)
            for img_data in images_data:
                # Eger foto yoksa ekle
                existing_img = await session.execute(
                    select(GalleryImage).where(
                        (GalleryImage.gallery_id == gallery.id) & 
                        (GalleryImage.image_url == img_data["image_url"])
                    ).limit(1)
                )
                if not existing_img.scalars().first():
                    gi = GalleryImage(
                        gallery_id=gallery.id,
                        image_url=img_data["image_url"],
                        description=img_data["description"]
                    )
                    session.add(gi)

    if count > 0:
        await session.commit()
    logger.info(f"Galeri: {count} yeni galeri eklendi.")
    return count
