"""
Pharmacy Scraper - Nöbetçi Eczane
Günlük olarak nöbetçi eczane bilgilerini çeker.
"""

from datetime import date
from typing import List, Dict, Any
import logging

from .base import BaseScraper
from app.models import PharmacyDuty
from app.database import SessionLocal

logger = logging.getLogger(__name__)


class PharmacyScraper(BaseScraper):
    """Nöbetçi eczane scraper'ı"""
    
    PATH = "/kent-rehberi/nobetci-eczane"
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Nöbetçi eczaneleri çek.
        
        Returns:
            Eczane bilgilerinin listesi
        """
        soup = self.fetch(self.PATH)
        if not soup:
            logger.error("Failed to fetch pharmacy page")
            return []
        
        pharmacies = []
        
        # Belediye sitesindeki yapı: .nobetci .liste .item
        items = soup.select(".nobetci .liste .item")
        
        if not items:
            # Alternatif selector'lar dene
            items = soup.select(".liste .item") or soup.select(".item")
            logger.info(f"Using fallback selector, found {len(items)} items")
        else:
            logger.info(f"Found {len(items)} pharmacy items with primary selector")
        
        for item in items:
            try:
                pharmacy = self._parse_item(item)
                if pharmacy and pharmacy.get("name"):
                    pharmacies.append(pharmacy)
            except Exception as e:
                logger.warning(f"Error parsing pharmacy item: {e}")
                continue
        
        logger.info(f"Scraped {len(pharmacies)} pharmacies")
        return pharmacies
    
    def _parse_item(self, item) -> Dict[str, Any]:
        """
        Tek bir eczane öğesini parse et.
        Site yapısı:
        - .title .tbaslik = isim
        - .detay .isol .arow = adres/telefon satırları
        - .detay .isag a = harita linki
        """
        # İsim: .title .tbaslik
        name_elem = item.select_one(".title .tbaslik")
        if not name_elem:
            name_elem = item.select_one(".tbaslik, .title, h4, strong")
        name = self.clean_text(name_elem.get_text()) if name_elem else None
        
        # Adres ve Telefon: .detay .isol .arow içinde
        address = None
        phone = None
        
        arows = item.select(".detay .isol .arow")
        for i, arow in enumerate(arows):
            val_elem = arow.select_one(".val")
            if val_elem:
                text = self.clean_text(val_elem.get_text())
                if i == 0:  # İlk satır genellikle adres
                    address = text
                elif i == 1:  # İkinci satır genellikle telefon
                    phone = text
        
        # Telefon bulunamadıysa tüm metinde ara
        if not phone:
            phone = self.extract_phone(item.get_text())
        
        # Harita linki: .detay .isag a
        maps_elem = item.select_one(".detay .isag a")
        if not maps_elem:
            maps_elem = item.select_one("a[href*='maps'], a[href*='google']")
        maps_link = maps_elem.get("href") if maps_elem else None
        
        return {
            "name": name,
            "address": address,
            "phone": phone,
            "maps_link": maps_link,
            "duty_date": date.today()
        }
    
    def save_to_db(self, pharmacies: List[Dict[str, Any]]) -> int:
        """
        Eczaneleri veritabanına kaydet.
        
        Args:
            pharmacies: Eczane bilgileri listesi
            
        Returns:
            Kaydedilen eczane sayısı
        """
        if not pharmacies:
            logger.warning("No pharmacies to save")
            return 0
            
        db = SessionLocal()
        
        try:
            # Bugünkü eski kayıtları sil
            deleted = db.query(PharmacyDuty).filter(
                PharmacyDuty.duty_date == date.today()
            ).delete()
            
            if deleted:
                logger.info(f"Deleted {deleted} old pharmacy records")
            
            # Yeni kayıtları ekle
            for p in pharmacies:
                duty = PharmacyDuty(
                    name=p["name"],
                    address=p.get("address"),
                    phone=p.get("phone"),
                    maps_link=p.get("maps_link"),
                    duty_date=p["duty_date"]
                )
                db.add(duty)
            
            db.commit()
            logger.info(f"Saved {len(pharmacies)} pharmacies to database")
            return len(pharmacies)
            
        except Exception as e:
            logger.error(f"Database error: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    def run(self) -> int:
        """
        Tam scrape döngüsü çalıştır.
        
        Returns:
            Kaydedilen eczane sayısı
        """
        logger.info("Starting pharmacy scrape...")
        pharmacies = self.scrape()
        count = self.save_to_db(pharmacies)
        logger.info(f"Pharmacy scrape complete. Saved {count} records.")
        return count
