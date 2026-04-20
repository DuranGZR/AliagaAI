"""
AliağaAI — Temel scraper sınıfı.

Tüm sayfa scraperları bu sınıftan türer.
HTTP istekleri, HTML parse etme ve hata yönetimi burada merkezileştirilir.
"""
from abc import ABC, abstractmethod
from typing import Any

import httpx
from bs4 import BeautifulSoup
from loguru import logger

from app.core.config import settings


class BaseScraper(ABC):
    """Tüm scraperların miras aldığı temel sınıf."""

    BASE_URL: str = "https://aliaga.bel.tr"

    def __init__(self):
        self.timeout = settings.SCRAPE_TIMEOUT
        self.headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "tr-TR,tr;q=0.9",
        }

    async def _fetch_page(self, url: str) -> BeautifulSoup | None:
        """Bir sayfayı indirir ve BeautifulSoup nesnesi döner."""
        full_url = url if url.startswith("http") else f"{self.BASE_URL}{url}"
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                headers=self.headers,
                follow_redirects=True,
            ) as client:
                resp = await client.get(full_url)
                resp.raise_for_status()
                return BeautifulSoup(resp.text, "lxml")
        except httpx.HTTPError as e:
            logger.error(f"Scraper HTTP hatası: {full_url} → {e}")
            return None
        except Exception as e:
            logger.error(f"Scraper genel hata: {full_url} → {e}")
            return None

    @abstractmethod
    async def scrape(self, **kwargs) -> list[dict[str, Any]]:
        """Alt sınıflar bu metodu implement eder."""
        ...

    @staticmethod
    def clean_text(text: str | None) -> str:
        """HTML metnini temizler: strip, çoklu boşlukları azalt."""
        if not text:
            return ""
        import re
        text = text.strip()
        text = re.sub(r"\s+", " ", text)
        return text
