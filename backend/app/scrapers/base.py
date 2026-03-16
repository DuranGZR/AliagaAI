"""
Base Scraper - Tüm scraper'ların temel sınıfı
"""

import httpx
from bs4 import BeautifulSoup
from typing import Optional
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class BaseScraper:
    """Temel scraper sınıfı"""
    
    BASE_URL = settings.belediye_base_url
    
    def __init__(self):
        self.client = httpx.Client(
            timeout=settings.scrape_timeout,
            headers={
                "User-Agent": settings.user_agent,
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
            },
            follow_redirects=True
        )
    
    def fetch(self, path: str) -> Optional[BeautifulSoup]:
        """
        URL'den HTML çek ve BeautifulSoup olarak döndür.
        
        Args:
            path: URL path'i (örn: "/kent-rehberi/nobetci-eczane")
            
        Returns:
            BeautifulSoup objesi veya None (hata durumunda)
        """
        url = f"{self.BASE_URL}{path}"
        
        try:
            logger.info(f"Fetching: {url}")
            response = self.client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            logger.info(f"Successfully fetched: {url}")
            return soup
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error for {url}: {e.response.status_code}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {e}")
            return None
    
    def clean_text(self, text: Optional[str]) -> str:
        """
        Metni temizle (fazla boşlukları kaldır).
        
        Args:
            text: Temizlenecek metin
            
        Returns:
            Temizlenmiş metin
        """
        if not text:
            return ""
        return " ".join(text.split()).strip()
    
    def extract_phone(self, text: str) -> Optional[str]:
        """
        Metinden telefon numarası çıkar.
        
        Args:
            text: Telefon içerebilecek metin
            
        Returns:
            Telefon numarası veya None
        """
        import re
        # Türk telefon formatları
        patterns = [
            r'0\d{3}\s?\d{3}\s?\d{2}\s?\d{2}',  # 0232 616 12 34
            r'\+90\s?\d{3}\s?\d{3}\s?\d{2}\s?\d{2}',  # +90 232 616 12 34
            r'\d{3}\s?\d{3}\s?\d{2}\s?\d{2}',  # 232 616 12 34
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group().strip()
        
        return None
    
    def close(self):
        """HTTP client'ı kapat"""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
