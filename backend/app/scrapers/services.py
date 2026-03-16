"""
Hizmetlerimiz Scraper
Belediye hizmetlerini çeker (12 sayfa)
"""

from typing import List, Dict, Any
import logging

from .base import BaseScraper
from app.models import Service
from app.database import SessionLocal

logger = logging.getLogger(__name__)


class ServicesScraper(BaseScraper):
    """Hizmetlerimiz bölümü scraper'ı"""
    
    PAGES = {
        "iste_aliaga": {
            "path": "/hizmetlerimiz/iste-aliaga",
            "category": "is",
            "name": "İş'te Aliağa - Kariyer Platformu"
        },
        "kent_kitapligi": {
            "path": "/hizmetlerimiz/aliaga-kent-kitapligi",
            "category": "kutuphane",
            "name": "Aliağa Kent Kitaplığı"
        },
        "aziz_sancar": {
            "path": "/hizmetlerimiz/aziz-sancar-kutuphanesi",
            "category": "kutuphane",
            "name": "Aziz Sancar Kütüphanesi"
        },
        "nadir_nadi": {
            "path": "/hizmetlerimiz/nadir-nadi-kutuphanesi",
            "category": "kutuphane",
            "name": "Nadir Nadi Kütüphanesi"
        },
        "santranc": {
            "path": "/hizmetlerimiz/santranc-kulubu",
            "category": "spor",
            "name": "Santranç Kulübü"
        },
        "nikah": {
            "path": "/hizmetlerimiz/nikah-islemleri",
            "category": "sosyal",
            "name": "Nikah İşlemleri"
        },
        "sifir_atik": {
            "path": "/hizmetlerimiz/sifir-atik",
            "category": "cevre",
            "name": "Sıfır Atık"
        },
        "sosyal_market": {
            "path": "/hizmetlerimiz/sosyal-market",
            "category": "sosyal",
            "name": "Sosyal Market"
        },
        "cop_ekspres": {
            "path": "/hizmetlerimiz/cop-ekspres",
            "category": "cevre",
            "name": "Çöp Ekspres"
        },
        "milletin_ekibi": {
            "path": "/hizmetlerimiz/milletin-ekibi",
            "category": "sosyal",
            "name": "Milletin Ekibi"
        },
        "kultur_gezileri": {
            "path": "/hizmetlerimiz/kultur-gezileri-ve-sehitlik-ziyaretleri",
            "category": "kultur",
            "name": "Kültür Gezileri ve Şehitlik Ziyaretleri"
        },
        "asev": {
            "path": "/hizmetlerimiz/aliaga-sanat-evi-asev",
            "category": "kultur",
            "name": "Aliağa Sanat Evi (ASEV)"
        },
    }
    
    def scrape_service(self, key: str, info: Dict) -> Dict[str, Any]:
        """Tek bir hizmeti çek"""
        path = info["path"]
        
        soup = self.fetch(path)
        if not soup:
            logger.error(f"Failed to fetch {key}")
            return {}
        
        # İçerik alanı
        content_area = None
        for selector in [".sayfa-text", ".sayfa-icerik", ".page-content", ".content"]:
            content_area = soup.select_one(selector)
            if content_area:
                break
        
        if not content_area:
            content_area = soup.select_one("body")
        
        # Gereksiz elementleri kaldır
        for elem in content_area.select("script, style, nav, footer, .sidebar"):
            elem.decompose()
        
        # Açıklama
        paragraphs = content_area.find_all("p")
        description = "\n\n".join(
            self.clean_text(p.get_text()) 
            for p in paragraphs 
            if self.clean_text(p.get_text())
        )
        
        if not description:
            description = self.clean_text(content_area.get_text())
        
        # Telefon ve adres ara
        text = content_area.get_text()
        phone = self.extract_phone(text)
        
        # Çalışma saatleri ara
        working_hours = None
        hours_patterns = [
            r'(\d{2}:\d{2})\s*[-–]\s*(\d{2}:\d{2})',
            r'saat[:\s]+(\d{2}:\d{2})',
        ]
        for pattern in hours_patterns:
            match = re.search(pattern, text, re.IGNORECASE) if 're' in dir() else None
            if match:
                working_hours = match.group(0)
                break
        
        result = {
            "name": info["name"],
            "category": info["category"],
            "description": description[:5000],
            "phone": phone,
            "working_hours": working_hours,
            "source_url": f"{self.BASE_URL}{path}"
        }
        
        logger.info(f"Scraped service: {info['name']}")
        return result
    
    def scrape_all(self) -> Dict[str, Dict]:
        """Tüm hizmetleri çek"""
        results = {}
        
        for key, info in self.PAGES.items():
            try:
                results[key] = self.scrape_service(key, info)
            except Exception as e:
                logger.error(f"Error scraping {key}: {e}")
                results[key] = {}
        
        return results
    
    def save_to_db(self, data: Dict[str, Dict]) -> int:
        """Verileri veritabanına kaydet"""
        db = SessionLocal()
        total = 0
        
        try:
            for key, info in data.items():
                if not info or not info.get("description"):
                    continue
                
                # Mevcut kaydı güncelle veya yeni ekle
                existing = db.query(Service).filter(
                    Service.name == info["name"]
                ).first()
                
                if existing:
                    existing.description = info.get("description")
                    existing.phone = info.get("phone")
                    existing.working_hours = info.get("working_hours")
                    existing.source_url = info.get("source_url")
                else:
                    record = Service(
                        name=info["name"],
                        category=info["category"],
                        description=info.get("description"),
                        phone=info.get("phone"),
                        working_hours=info.get("working_hours"),
                        source_url=info.get("source_url")
                    )
                    db.add(record)
                
                total += 1
            
            db.commit()
            logger.info(f"Saved {total} service records")
            return total
            
        except Exception as e:
            logger.error(f"Database error: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    def run(self) -> int:
        """Tam scrape döngüsü"""
        logger.info("Starting services scrape...")
        data = self.scrape_all()
        count = self.save_to_db(data)
        logger.info(f"Services scrape complete. Saved {count} records.")
        return count


# Import için
import re
