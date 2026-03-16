"""
Aliağa Comprehensive Scraper
Tüm Aliağa bölümü sayfalarını çeker (17 sayfa)
"""

from typing import List, Dict, Any
import logging
import re

from .base import BaseScraper
from app.models import CityInfo, AntiqueCity, Gastronomy, Neighborhood
from app.database import SessionLocal

logger = logging.getLogger(__name__)


class AliagaScraper(BaseScraper):
    """Aliağa bölümü - Genel şehir bilgileri scraper'ı"""
    
    # Tüm sayfalar ve kategorileri
    PAGES = {
        # Kategori: tarih
        "tarihce": {"path": "/aliaga/tarihce", "category": "tarih"},
        "aliaga_adinin_oykusu": {"path": "/aliaga/aliaga-adinin-oykusu", "category": "tarih"},
        
        # Kategori: cografya
        "cografyasi": {"path": "/aliaga/cografyasi", "category": "cografya"},
        "nufus_demografi": {"path": "/aliaga/nufus-ve-demografi", "category": "cografya"},
        
        # Kategori: ekonomi
        "ekonomi": {"path": "/aliaga/ekonomi", "category": "ekonomi"},
        
        # Kategori: kultur
        "kultur": {"path": "/aliaga/kultur", "category": "kultur"},
        "helvaci_kilimi": {"path": "/aliaga/helvaci-kilimi", "category": "kultur"},
        
        # Kategori: egitim
        "egitim": {"path": "/aliaga/egitim", "category": "egitim"},
        
        # Kategori: saglik
        "saglik": {"path": "/aliaga/saglik", "category": "saglik"},
        
        # Kategori: turizm
        "turizm": {"path": "/aliaga/aliagada-turizm", "category": "turizm"},
        "antik_kentler": {"path": "/aliaga/antik-kentler", "category": "turizm"},
        "gezi_rotalari": {"path": "/aliaga/aliaga-da-gezi-rotalari", "category": "turizm"},
        "gezilecek_yerler": {"path": "/aliaga/aliagada-turizm/gezilecek-onemli-yerler", "category": "turizm"},
        
        # Kategori: gastronomi
        "gastronomi": {"path": "/aliaga/gastronomi", "category": "gastronomi"},
        
        # Kategori: ulasim
        "ulasim": {"path": "/aliaga/aliaga-ya-nasil-gelinir", "category": "ulasim"},
        
        # Kategori: idari
        "idari_sosyal": {"path": "/aliaga/idari-ve-sosyal-durum", "category": "idari"},
        
        # Mahalleler (ayrı tablo)
        "mahalleler": {"path": "/aliaga/mahallelerimiz", "category": "mahalle"},
    }
    
    def scrape_page(self, topic: str, info: Dict) -> Dict[str, Any]:
        """Tek bir sayfayı çek"""
        path = info["path"]
        category = info["category"]
        
        soup = self.fetch(path)
        if not soup:
            logger.error(f"Failed to fetch {topic}")
            return {}
        
        # Sayfa başlığı
        title_elem = soup.select_one("h1, .page-title, .baslik, .sayfa-baslik")
        title = self.clean_text(title_elem.get_text()) if title_elem else topic.replace("_", " ").title()
        
        # İçerik alanı
        content_area = None
        for selector in [".sayfa-text", ".sayfa-icerik", ".page-content", ".content", "article"]:
            content_area = soup.select_one(selector)
            if content_area:
                break
        
        if not content_area:
            content_area = soup.select_one("body")
        
        # Gereksiz elementleri kaldır
        for elem in content_area.select("script, style, nav, footer, .sidebar, .menu, .breadcrumb"):
            elem.decompose()
        
        # Paragrafları çek
        paragraphs = content_area.find_all("p")
        content = "\n\n".join(
            self.clean_text(p.get_text()) 
            for p in paragraphs 
            if self.clean_text(p.get_text())
        )
        
        # Eğer paragraf yoksa tüm metni al
        if not content:
            content = self.clean_text(content_area.get_text())
        
        # Özet oluştur (ilk 200 karakter)
        summary = content[:200] + "..." if len(content) > 200 else content
        
        # Etiketler çıkar
        tags = self._extract_tags(content, category)
        
        # Alt başlıklar
        headings = [
            self.clean_text(h.get_text()) 
            for h in content_area.select("h2, h3, h4, strong")
            if self.clean_text(h.get_text())
        ]
        
        result = {
            "category": category,
            "topic": topic,
            "title": title,
            "content": content[:10000],  # Max 10K karakter
            "summary": summary,
            "tags": tags[:10],  # Max 10 etiket
            "headings": headings[:10],
            "source_url": f"{self.BASE_URL}{path}"
        }
        
        logger.info(f"Scraped {topic}: {len(content)} chars, {len(tags)} tags")
        return result
    
    def _extract_tags(self, content: str, category: str) -> List[str]:
        """İçerikten anahtar kelimeler çıkar"""
        tags = [category]
        
        # Önemli kelimeler
        keywords = {
            "tarih": ["antik", "bizans", "osmanlı", "cumhuriyet", "kyme", "myrina", "gryneion"],
            "turizm": ["gezi", "plaj", "deniz", "doğa", "bisiklet", "yürüyüş", "kamp"],
            "gastronomi": ["yemek", "ot", "zeytinyağı", "balık", "pita", "tatlı"],
            "kultur": ["kilim", "el sanatı", "festival", "etkinlik", "müze"],
            "ekonomi": ["liman", "sanayi", "ticaret", "rafineri", "tersane"],
        }
        
        content_lower = content.lower()
        for key_list in keywords.get(category, []):
            if key_list in content_lower:
                tags.append(key_list)
        
        # Yer adları
        places = ["şakran", "helvacı", "bozköy", "çakmaklı", "yenişakran", "horozgediği"]
        for place in places:
            if place in content_lower:
                tags.append(place)
        
        return list(set(tags))
    
    def scrape_all(self) -> Dict[str, Dict]:
        """Tüm sayfaları çek"""
        results = {}
        
        for topic, info in self.PAGES.items():
            try:
                results[topic] = self.scrape_page(topic, info)
            except Exception as e:
                logger.error(f"Error scraping {topic}: {e}")
                results[topic] = {}
        
        return results
    
    def save_to_db(self, data: Dict[str, Dict]) -> int:
        """Verileri veritabanına kaydet"""
        db = SessionLocal()
        total = 0
        
        try:
            for topic, info in data.items():
                if not info or not info.get("content"):
                    continue
                
                # Mahalle verisi ayrı tabloya
                if info.get("category") == "mahalle":
                    continue  # NeighborhoodScraper'da işlenecek
                
                # Mevcut kaydı güncelle veya yeni ekle
                existing = db.query(CityInfo).filter(
                    CityInfo.topic == topic
                ).first()
                
                if existing:
                    existing.title = info.get("title")
                    existing.content = info.get("content")
                    existing.summary = info.get("summary")
                    existing.tags = info.get("tags", [])
                    existing.source_url = info.get("source_url")
                else:
                    record = CityInfo(
                        category=info["category"],
                        topic=topic,
                        title=info.get("title"),
                        content=info.get("content"),
                        summary=info.get("summary"),
                        tags=info.get("tags", []),
                        source_url=info.get("source_url")
                    )
                    db.add(record)
                
                total += 1
            
            db.commit()
            logger.info(f"Saved {total} city info records")
            return total
            
        except Exception as e:
            logger.error(f"Database error: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    def run(self) -> int:
        """Tam scrape döngüsü"""
        logger.info("Starting Aliaga comprehensive scrape...")
        data = self.scrape_all()
        count = self.save_to_db(data)
        logger.info(f"Aliaga scrape complete. Saved {count} records.")
        return count
