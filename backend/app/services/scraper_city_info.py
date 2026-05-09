"""
AliağaAI — Şehir bilgisi scraper'ı.

aliaga.bel.tr'nin 14 statik sayfasından (tarihçe, turizm, gastronomi vb.)
metin çeker ve pgvector document_chunks tablosuna chunk olarak kaydeder.
"""
from typing import Any

from loguru import logger
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.chunking import chunk_text, content_hash
from app.services.scraper_base import BaseScraper

# pgvector opsiyonel
try:
    from app.models.city import DocumentChunk
    HAS_CHUNKS = DocumentChunk is not None
except (ImportError, AttributeError):
    HAS_CHUNKS = False


# 14 şehir bilgisi sayfası
CITY_INFO_PAGES = [
    {"url": "/aliaga/tarihce", "title": "Aliağa Tarihçesi"},
    {"url": "/aliaga/antik-kentler", "title": "Aliağa Antik Kentler"},
    {"url": "/aliaga/turizm", "title": "Aliağa Turizm"},
    {"url": "/aliaga/gastronomi", "title": "Aliağa Gastronomi"},
    {"url": "/aliaga/cografyasi", "title": "Aliağa Coğrafyası"},
    {"url": "/aliaga/nufus-ve-demografi", "title": "Aliağa Nüfus ve Demografi"},
    {"url": "/aliaga/egitim", "title": "Aliağa Eğitim"},
    {"url": "/aliaga/kultur", "title": "Aliağa Kültür"},
    {"url": "/aliaga/saglik", "title": "Aliağa Sağlık"},
    {"url": "/aliaga/ekonomi", "title": "Aliağa Ekonomi"},
    {"url": "/aliaga/mahallelerimiz", "title": "Aliağa Mahalleleri"},
    {"url": "/aliaga/aliaga-da-gezi-rotalari", "title": "Aliağa Gezi Rotaları"},
    {"url": "/aliaga/helvaci-kilimi", "title": "Helvacı Kilimi"},
    {"url": "/aliaga/aliaga-ya-nasil-gelinir", "title": "Aliağa'ya Nasıl Gelinir"},
]


class CityInfoScraper(BaseScraper):
    """Statik şehir bilgi sayfalarını çeker."""

    async def scrape(self, **kwargs) -> list[dict[str, Any]]:
        """Tüm şehir bilgisi sayfalarını çeker."""
        results = []
        for page in CITY_INFO_PAGES:
            soup = await self._fetch_page(page["url"])
            if not soup:
                logger.warning(f"Sayfa çekilemedi: {page['url']}")
                continue

            # Gereksiz kısımları HTML'den tamamen kopar
            for el in soup.select("script, style, nav, footer, header, .breadcrumb, .social-share, iframe, ul.menu, #menu"):
                el.decompose()

            # Yeni ve daha sağlam hedef: Tüm p etiketlerini veya büyük div içindeki metinleri topla
            text_blocks = []
            paragraphs = soup.find_all("p")
            if paragraphs:
                for p in paragraphs:
                    p_text = self.clean_text(p.get_text(separator=' '))
                    if len(p_text) > 40:  # Navigasyon parçalarını vs ele
                        text_blocks.append(p_text)
                text = " ".join(text_blocks)
            else:
                text = ""

            # Eğer p tagleri kullanmamışlarsa (sadece text nodes ise), body'den çek
            if len(text) < 50 and soup.body:
                text = self.clean_text(soup.body.get_text(separator=' '))

            if len(text) < 50:
                logger.warning(f"Çok kısa içerik ({len(text)} karakter): {page['url']}")
                continue

            results.append({
                "title": page["title"],
                "url": page["url"],
                "content": text,
            })
            logger.debug(f"Sayfa çekildi: {page['title']} ({len(text)} karakter)")

        logger.info(f"Şehir bilgisi: {len(results)}/{len(CITY_INFO_PAGES)} sayfa çekildi.")
        return results


async def scrape_and_save_city_info(
    session: AsyncSession,
    embedding_fn=None,
) -> int:
    """
    Şehir bilgisi sayfalarını çeker, chunk'lar ve DB'ye kaydeder.

    embedding_fn: async def(text: str) -> list[float] — None ise embedding atlanır.
    """
    if not HAS_CHUNKS:
        logger.warning("DocumentChunk modeli mevcut değil (pgvector yüklü değil). Atlanıyor.")
        return 0

    scraper = CityInfoScraper()
    pages = await scraper.scrape()

    # Eski city_info chunk'larını sil
    await session.execute(
        delete(DocumentChunk).where(DocumentChunk.source_type == "city_info")
    )

    total_chunks = 0
    for page in pages:
        chunks = chunk_text(
            page["content"],
            chunk_size=settings.CHUNK_SIZE,
            overlap=settings.CHUNK_OVERLAP,
            min_length=settings.CHUNK_MIN_LENGTH,
        )
        page_hash = content_hash(page["content"])
        for i, chunk_content in enumerate(chunks):
            if not embedding_fn:
                continue
            try:
                embedding = await embedding_fn(chunk_content)
            except Exception as e:
                logger.warning(f"Embedding hatası (city_info chunk atlandı): {e}")
                continue

            doc = DocumentChunk(
                source_type="city_info",
                source_id=None,
                chunk_index=i,
                content=chunk_content,
                embedding=embedding,
                metadata_json={
                    "title": page["title"],
                    "url": page["url"],
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "content_hash": page_hash,
                    "embedding_model": settings.EMBEDDING_MODEL,
                },
            )
            session.add(doc)
            total_chunks += 1

    if total_chunks > 0:
        await session.flush()
    logger.info(f"Şehir bilgisi: {total_chunks} chunk oluşturuldu ({len(pages)} sayfa).")
    return total_chunks
