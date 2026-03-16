"""
Tourism Scraper - Turistik Yerler ve Bilgiler
Tarih, kültür, gastronomi, antik kentler vb. bilgileri çeker.
"""

from typing import Dict, Any
import logging

from .base import BaseScraper
from app.models import CityInfo
from app.database import SessionLocal

logger = logging.getLogger(__name__)


class TourismScraper(BaseScraper):
    """Turistik bilgiler scraper'ı"""
    
    PATHS = {
        "tarih": "/aliaga/tarihce",
        "antik_kentler": "/aliaga/antik-kentler",
        "gastronomi": "/aliaga/gastronomi",
        "turizm": "/aliaga/aliagada-turizm",
        "gezilecek_yerler": "/aliaga/aliagada-turizm/gezilecek-onemli-yerler",
        "gezi_rotalari": "/aliaga/aliaga-da-gezi-rotalari",
        "helvaci_kilimi": "/aliaga/helvaci-kilimi",
        "cografya": "/aliaga/cografyasi",
        "ekonomi": "/aliaga/ekonomi",
        "kultur": "/aliaga/kultur",
        "ulasim": "/aliaga/aliaga-ya-nasil-gelinir",
    }
    
    def scrape_topic(self, topic: str) -> Dict[str, Any]:
        """
        Belirli bir konuyu çek.
        
        Args:
            topic: Konu adı
            
        Returns:
            Konu bilgileri
        """
        if topic not in self.PATHS:
            logger.error(f"Unknown topic: {topic}")
            return {}
        
        path = self.PATHS[topic]
        soup = self.fetch(path)
        
        if not soup:
            logger.error(f"Failed to fetch {topic} page")
            return {}
        
        # Sayfa başlığı
        title_elem = soup.select_one("h1, .page-title, .entry-title, .baslik")
        title = self.clean_text(title_elem.get_text()) if title_elem else topic
        
        # Ana içerik alanı: .sayfa-text (belediye sitesi yapısı)
        content_selectors = [
            ".sayfa-text",
            ".sayfa-icerik",
            ".page-content",
            ".entry-content", 
            ".content",
            "article",
            ".col-md-9",
        ]
        
        content_area = None
        for selector in content_selectors:
            content_area = soup.select_one(selector)
            if content_area:
                logger.info(f"Found content area with selector: {selector}")
                break
        
        if not content_area:
            logger.warning(f"Could not find content area for {topic}")
            # Son çare: body'den al
            content_area = soup.select_one("body")
        
        # Script ve style etiketlerini kaldır
        for script in content_area.select("script, style, nav, footer, .sidebar, .menu"):
            script.decompose()
        
        # Metin içeriği - paragrafları topla
        paragraphs = content_area.find_all("p")
        text_content = "\n\n".join(
            self.clean_text(p.get_text()) 
            for p in paragraphs 
            if self.clean_text(p.get_text())
        )
        
        # Eğer paragraf yoksa tüm metni al
        if not text_content:
            text_content = self.clean_text(content_area.get_text())
        
        # Görseller
        images = [
            img.get("src") for img in content_area.select("img")
            if img.get("src") and not img.get("src").endswith(".svg")
        ]
        
        # Alt başlıklar
        headings = [
            self.clean_text(h.get_text()) 
            for h in content_area.select("h2, h3, h4, strong")
            if self.clean_text(h.get_text())
        ]
        
        result = {
            "topic": topic,
            "title": title,
            "content": text_content[:5000],  # Max 5000 karakter
            "headings": headings[:10],  # Max 10 başlık
            "images": images[:5],  # Max 5 görsel
            "source_url": f"{self.BASE_URL}{path}"
        }
        
        logger.info(f"Scraped {topic}: {len(text_content)} chars, {len(headings)} headings")
        return result
    
    def scrape_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Tüm konuları çek.
        
        Returns:
            Konu -> bilgiler dict
        """
        results = {}
        
        for topic in self.PATHS:
            try:
                results[topic] = self.scrape_topic(topic)
            except Exception as e:
                logger.error(f"Error scraping {topic}: {e}")
                results[topic] = {}
        
        return results
    
    def save_to_db(self, data: Dict[str, Dict[str, Any]]) -> int:
        """
        Tüm bilgileri veritabanına kaydet.
        
        Args:
            data: Konu -> bilgiler
            
        Returns:
            Kaydedilen kayıt sayısı
        """
        db = SessionLocal()
        total = 0
        
        try:
            for topic, info in data.items():
                if not info or not info.get("content"):
                    continue
                
                # Bu konunun eski kaydını sil
                db.query(CityInfo).filter(
                    CityInfo.topic == topic
                ).delete()
                
                # Yeni kayıt ekle
                record = CityInfo(
                    category="turizm",
                    topic=topic,
                    title=info.get("title", topic),
                    content=info.get("content"),
                    source_url=info.get("source_url")
                )
                db.add(record)
                total += 1
            
            db.commit()
            logger.info(f"Saved {total} city info entries")
            return total
            
        except Exception as e:
            logger.error(f"Database error: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    def run(self) -> int:
        """Tam scrape döngüsü çalıştır"""
        logger.info("Starting tourism scrape...")
        data = self.scrape_all()
        count = self.save_to_db(data)
        logger.info(f"Tourism scrape complete. Saved {count} records.")
        return count
