"""
Institutions Scraper - Kamu Kuruluşları
Kamu kuruluşları, sağlık, okullar, muhtarlıklar vb. çeker.
"""

from typing import List, Dict, Any
import logging

from .base import BaseScraper
from app.models import Institution
from app.database import SessionLocal

logger = logging.getLogger(__name__)


class InstitutionsScraper(BaseScraper):
    """Kamu kuruluşları scraper'ı"""
    
    PATHS = {
        "acil": "/kent-rehberi/acil-telefonlar",
        "kamu": "/kent-rehberi/kamu-kuruluslari",
        "saglik": "/kent-rehberi/saglik-kuruluslari",
        "okul": "/kent-rehberi/okullar",
        "muhtar": "/kent-rehberi/muhtarliklarimiz",
        "kutuphane": "/kent-rehberi/kutuphaneler",
        "otel": "/kent-rehberi/oteller",
    }
    
    def scrape_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Belirli bir kategoriyi çek.
        
        Args:
            category: Kategori adı (acil, kamu, saglik, vb.)
            
        Returns:
            Kurum bilgileri listesi
        """
        if category not in self.PATHS:
            logger.error(f"Unknown category: {category}")
            return []
        
        path = self.PATHS[category]
        soup = self.fetch(path)
        
        if not soup:
            logger.error(f"Failed to fetch {category} page")
            return []
        
        institutions = []
        
        # Tablo formatı dene
        table = soup.select_one("table")
        if table:
            institutions = self._parse_table(table, category, path)
        else:
            # Liste/kart formatı dene
            institutions = self._parse_list(soup, category, path)
        
        logger.info(f"Scraped {len(institutions)} institutions for {category}")
        return institutions
    
    def _parse_table(self, table, category: str, source_url: str) -> List[Dict[str, Any]]:
        """Tablo formatındaki veriyi parse et"""
        institutions = []
        
        rows = table.select("tr")
        headers = []
        
        # Header'ları bul
        header_row = table.select_one("thead tr, tr:first-child")
        if header_row:
            headers = [self.clean_text(th.get_text()).lower() 
                      for th in header_row.select("th, td")]
        
        # Data row'ları parse et
        for row in rows[1:] if headers else rows:
            cols = row.select("td")
            if len(cols) < 2:
                continue
            
            institution = {
                "type": category,
                "source_url": f"{self.BASE_URL}{source_url}"
            }
            
            # Sütunları işle
            if len(cols) >= 1:
                institution["name"] = self.clean_text(cols[0].get_text())
            if len(cols) >= 2:
                # Telefon veya adres olabilir
                text = cols[1].get_text()
                if self.extract_phone(text):
                    institution["phone"] = self.extract_phone(text)
                else:
                    institution["address"] = self.clean_text(text)
            if len(cols) >= 3:
                institution["phone"] = self.clean_text(cols[2].get_text())
            
            if institution.get("name"):
                institutions.append(institution)
        
        return institutions
    
    def _parse_list(self, soup, category: str, source_url: str) -> List[Dict[str, Any]]:
        """Liste/kart formatındaki veriyi parse et"""
        institutions = []
        
        # Olası container'lar
        content = soup.select_one(".page-content, .content, main, .col-md-9")
        if not content:
            content = soup
        
        # Olası item selector'lar
        selectors = [
            ".card",
            ".list-group-item",
            ".rehber-item",
            "article",
            ".item"
        ]
        
        items = []
        for selector in selectors:
            items = content.select(selector)
            if items:
                break
        
        for item in items:
            try:
                name_elem = item.select_one("h4, h5, h3, .title, strong")
                name = self.clean_text(name_elem.get_text()) if name_elem else None
                
                if not name:
                    continue
                
                # Adres ve telefon ara
                text = item.get_text()
                phone = self.extract_phone(text)
                
                address_elem = item.select_one(".address, p")
                address = self.clean_text(address_elem.get_text()) if address_elem else None
                
                # Harita linki
                maps_elem = item.select_one("a[href*='maps']")
                maps_link = maps_elem.get("href") if maps_elem else None
                
                institutions.append({
                    "type": category,
                    "name": name,
                    "address": address,
                    "phone": phone,
                    "maps_link": maps_link,
                    "source_url": f"{self.BASE_URL}{source_url}"
                })
                
            except Exception as e:
                logger.warning(f"Error parsing item: {e}")
                continue
        
        return institutions
    
    def scrape_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Tüm kategorileri çek.
        
        Returns:
            Kategori -> kurumlar listesi dict
        """
        results = {}
        
        for category in self.PATHS:
            try:
                results[category] = self.scrape_category(category)
            except Exception as e:
                logger.error(f"Error scraping {category}: {e}")
                results[category] = []
        
        return results
    
    def save_to_db(self, data: Dict[str, List[Dict[str, Any]]]) -> int:
        """
        Tüm kurumları veritabanına kaydet.
        
        Args:
            data: Kategori -> kurumlar listesi
            
        Returns:
            Toplam kaydedilen kurum sayısı
        """
        db = SessionLocal()
        total = 0
        
        try:
            for category, institutions in data.items():
                # Bu kategorinin eski kayıtlarını sil
                db.query(Institution).filter(
                    Institution.type == category
                ).delete()
                
                # Yeni kayıtları ekle
                for inst in institutions:
                    record = Institution(
                        type=category,
                        name=inst["name"],
                        address=inst.get("address"),
                        phone=inst.get("phone"),
                        maps_link=inst.get("maps_link"),
                        source_url=inst.get("source_url")
                    )
                    db.add(record)
                    total += 1
            
            db.commit()
            logger.info(f"Saved {total} institutions to database")
            return total
            
        except Exception as e:
            logger.error(f"Database error: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    def run(self) -> int:
        """Tam scrape döngüsü çalıştır"""
        logger.info("Starting institutions scrape...")
        data = self.scrape_all()
        count = self.save_to_db(data)
        logger.info(f"Institutions scrape complete. Saved {count} records.")
        return count
