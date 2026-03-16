"""
Comprehensive Scraper v3
Tüm kategoriler için tek scraper - 40+ sayfa
"""

from typing import List, Dict, Any, Optional
import logging
import re
from datetime import date

from .base import BaseScraper
from app.models import (
    History, Geography, Economy, Culture, EducationInfo, HealthInfo, Transport,
    AntiqueCity, TourismSpot, Gastronomy, HikingRoute,
    EmergencyPhone, PublicInstitution, HealthFacility, School, Hotel, Library,
    Neighborhood, MunicipalService, PharmacyDuty
)
from app.database import SessionLocal

logger = logging.getLogger(__name__)


class ComprehensiveScraper(BaseScraper):
    """Tüm Aliağa verilerini çeken ana scraper"""
    
    # =========================================================================
    # ŞEHİR BİLGİSİ SAYFALARI
    # =========================================================================
    
    def scrape_history(self) -> int:
        """Tarihçe bilgilerini çek"""
        db = SessionLocal()
        count = 0
        
        pages = [
            ("/aliaga/tarihce", "Genel Tarih", "Cumhuriyet"),
            ("/aliaga/aliaga-adinin-oykusu", "Aliağa Adının Öyküsü", "Antik Çağ"),
        ]
        
        try:
            # Önce mevcut kayıtları sil
            db.query(History).delete()
            
            for path, title, period in pages:
                soup = self.fetch(path)
                if not soup:
                    continue
                
                content = self._extract_content(soup)
                if content:
                    record = History(
                        period=period,
                        title=title,
                        content=content,
                        source_url=f"{self.BASE_URL}{path}"
                    )
                    db.add(record)
                    count += 1
            
            db.commit()
            logger.info(f"History: {count} records saved")
        except Exception as e:
            logger.error(f"History error: {e}")
            db.rollback()
        finally:
            db.close()
        
        return count
    
    def scrape_geography(self) -> int:
        """Coğrafya bilgilerini çek"""
        db = SessionLocal()
        count = 0
        
        pages = [
            ("/aliaga/cografyasi", "Coğrafya", "konum"),
            ("/aliaga/nufus-ve-demografi", "Nüfus ve Demografi", "nufus"),
        ]
        
        try:
            db.query(Geography).delete()
            
            for path, title, topic in pages:
                soup = self.fetch(path)
                if not soup:
                    continue
                
                content = self._extract_content(soup)
                if content:
                    record = Geography(
                        topic=topic,
                        title=title,
                        content=content,
                        source_url=f"{self.BASE_URL}{path}"
                    )
                    db.add(record)
                    count += 1
            
            db.commit()
            logger.info(f"Geography: {count} records saved")
        except Exception as e:
            logger.error(f"Geography error: {e}")
            db.rollback()
        finally:
            db.close()
        
        return count
    
    def scrape_economy(self) -> int:
        """Ekonomi bilgilerini çek"""
        db = SessionLocal()
        count = 0
        
        try:
            db.query(Economy).delete()
            
            soup = self.fetch("/aliaga/ekonomi")
            if soup:
                content = self._extract_content(soup)
                if content:
                    record = Economy(
                        sector="genel",
                        title="Aliağa Ekonomisi",
                        content=content,
                        source_url=f"{self.BASE_URL}/aliaga/ekonomi"
                    )
                    db.add(record)
                    count += 1
            
            db.commit()
            logger.info(f"Economy: {count} records saved")
        except Exception as e:
            logger.error(f"Economy error: {e}")
            db.rollback()
        finally:
            db.close()
        
        return count
    
    def scrape_culture(self) -> int:
        """Kültür bilgilerini çek"""
        db = SessionLocal()
        count = 0
        
        pages = [
            ("/aliaga/kultur", "Aliağa Kültürü", "genel"),
            ("/aliaga/helvaci-kilimi", "Helvacı Kilimi", "el_sanati"),
        ]
        
        try:
            db.query(Culture).delete()
            
            for path, title, type_ in pages:
                soup = self.fetch(path)
                if not soup:
                    continue
                
                content = self._extract_content(soup)
                if content:
                    record = Culture(
                        type=type_,
                        title=title,
                        content=content,
                        source_url=f"{self.BASE_URL}{path}"
                    )
                    db.add(record)
                    count += 1
            
            db.commit()
            logger.info(f"Culture: {count} records saved")
        except Exception as e:
            logger.error(f"Culture error: {e}")
            db.rollback()
        finally:
            db.close()
        
        return count
    
    def scrape_education_info(self) -> int:
        """Eğitim bilgilerini çek"""
        db = SessionLocal()
        count = 0
        
        try:
            db.query(EducationInfo).delete()
            
            soup = self.fetch("/aliaga/egitim")
            if soup:
                content = self._extract_content(soup)
                if content:
                    record = EducationInfo(
                        title="Aliağa'da Eğitim",
                        content=content,
                        source_url=f"{self.BASE_URL}/aliaga/egitim"
                    )
                    db.add(record)
                    count += 1
            
            db.commit()
            logger.info(f"EducationInfo: {count} records saved")
        except Exception as e:
            logger.error(f"EducationInfo error: {e}")
            db.rollback()
        finally:
            db.close()
        
        return count
    
    def scrape_health_info(self) -> int:
        """Sağlık bilgilerini çek"""
        db = SessionLocal()
        count = 0
        
        try:
            db.query(HealthInfo).delete()
            
            soup = self.fetch("/aliaga/saglik")
            if soup:
                content = self._extract_content(soup)
                if content:
                    record = HealthInfo(
                        title="Aliağa'da Sağlık",
                        content=content,
                        source_url=f"{self.BASE_URL}/aliaga/saglik"
                    )
                    db.add(record)
                    count += 1
            
            db.commit()
            logger.info(f"HealthInfo: {count} records saved")
        except Exception as e:
            logger.error(f"HealthInfo error: {e}")
            db.rollback()
        finally:
            db.close()
        
        return count
    
    def scrape_transport(self) -> int:
        """Ulaşım bilgilerini çek"""
        db = SessionLocal()
        count = 0
        
        try:
            db.query(Transport).delete()
            
            soup = self.fetch("/aliaga/aliaga-ya-nasil-gelinir")
            if soup:
                content = self._extract_content(soup)
                if content:
                    record = Transport(
                        type="genel",
                        title="Aliağa'ya Nasıl Gelinir",
                        content=content,
                        how_to_get=content[:2000],
                        source_url=f"{self.BASE_URL}/aliaga/aliaga-ya-nasil-gelinir"
                    )
                    db.add(record)
                    count += 1
            
            db.commit()
            logger.info(f"Transport: {count} records saved")
        except Exception as e:
            logger.error(f"Transport error: {e}")
            db.rollback()
        finally:
            db.close()
        
        return count
    
    # =========================================================================
    # TURİZM
    # =========================================================================
    
    def scrape_gastronomy(self) -> int:
        """Gastronomi bilgilerini çek ve parse et"""
        db = SessionLocal()
        count = 0
        
        try:
            db.query(Gastronomy).delete()
            
            soup = self.fetch("/aliaga/gastronomi")
            if not soup:
                return 0
            
            content = self._extract_content(soup)
            
            # Ana gastronomi kaydı
            record = Gastronomy(
                name="Aliağa Mutfağı",
                type="genel",
                description=content,
                origin="Aliağa",
                source_url=f"{self.BASE_URL}/aliaga/gastronomi"
            )
            db.add(record)
            count += 1
            
            # Bilinen yemekleri ayrı kaydet
            foods = [
                ("Şevket-i Bostan", "yemek", "Şifalı ot yemeği", "Aliağa"),
                ("Şakran Usulü Mercan", "yemek", "Deniz ürünü", "Şakran"),
                ("Pita Böreği", "yemek", "Boşnak geleneği", "Aliağa"),
                ("Zeytinyağlılar", "yemek", "Ege mutfağı", "Aliağa"),
            ]
            
            for name, type_, desc, origin in foods:
                if name.lower() in content.lower():
                    record = Gastronomy(
                        name=name,
                        type=type_,
                        description=desc,
                        origin=origin,
                        source_url=f"{self.BASE_URL}/aliaga/gastronomi"
                    )
                    db.add(record)
                    count += 1
            
            db.commit()
            logger.info(f"Gastronomy: {count} records saved")
        except Exception as e:
            logger.error(f"Gastronomy error: {e}")
            db.rollback()
        finally:
            db.close()
        
        return count
    
    def scrape_antique_cities(self) -> int:
        """Antik kentleri çek ve parse et"""
        db = SessionLocal()
        count = 0
        
        try:
            db.query(AntiqueCity).delete()
            
            soup = self.fetch("/aliaga/antik-kentler")
            if not soup:
                return 0
            
            content = self._extract_content(soup)
            
            # Bilinen antik kentler
            cities = [
                ("Kyme", "MÖ 11. yüzyıl", "Nemrut Limanı yakınları"),
                ("Myrina", "MÖ 12. yüzyıl", "Aliağa merkez"),
                ("Gryneion", "MÖ 8. yüzyıl", "Yenişakran"),
                ("Tisna", "Antik Çağ", "Bozköy"),
                ("Aigai", "Antik Çağ", "Nemrut Kalesi"),
            ]
            
            for name, period, location in cities:
                record = AntiqueCity(
                    name=name,
                    period=period,
                    location=location,
                    description=f"{name} antik kenti - {content[:500]}...",
                    source_url=f"{self.BASE_URL}/aliaga/antik-kentler"
                )
                db.add(record)
                count += 1
            
            db.commit()
            logger.info(f"AntiqueCities: {count} records saved")
        except Exception as e:
            logger.error(f"AntiqueCities error: {e}")
            db.rollback()
        finally:
            db.close()
        
        return count
    
    def scrape_hiking_routes(self) -> int:
        """Gezi rotalarını çek"""
        db = SessionLocal()
        count = 0
        
        try:
            db.query(HikingRoute).delete()
            
            soup = self.fetch("/aliaga/aliaga-da-gezi-rotalari")
            if not soup:
                return 0
            
            content = self._extract_content(soup)
            
            record = HikingRoute(
                name="Aliağa Gezi Rotaları",
                type="genel",
                description=content,
                source_url=f"{self.BASE_URL}/aliaga/aliaga-da-gezi-rotalari"
            )
            db.add(record)
            count += 1
            
            db.commit()
            logger.info(f"HikingRoutes: {count} records saved")
        except Exception as e:
            logger.error(f"HikingRoutes error: {e}")
            db.rollback()
        finally:
            db.close()
        
        return count
    
    # =========================================================================
    # KURUMLAR
    # =========================================================================
    
    def scrape_emergency_phones(self) -> int:
        """Acil telefonları çek"""
        db = SessionLocal()
        count = 0
        
        try:
            db.query(EmergencyPhone).delete()
            
            soup = self.fetch("/kent-rehberi/acil-telefonlar")
            if not soup:
                return 0
            
            # Tablo varsa
            table = soup.select_one("table")
            if table:
                rows = table.select("tr")
                for row in rows[1:]:  # Skip header
                    cols = row.select("td")
                    if len(cols) >= 2:
                        name = self.clean_text(cols[0].get_text())
                        phone = self.clean_text(cols[1].get_text())
                        
                        if name and phone:
                            record = EmergencyPhone(name=name, phone=phone)
                            db.add(record)
                            count += 1
            
            db.commit()
            logger.info(f"EmergencyPhones: {count} records saved")
        except Exception as e:
            logger.error(f"EmergencyPhones error: {e}")
            db.rollback()
        finally:
            db.close()
        
        return count
    
    def scrape_public_institutions(self) -> int:
        """Kamu kuruluşlarını çek"""
        db = SessionLocal()
        count = 0
        
        try:
            db.query(PublicInstitution).delete()
            
            soup = self.fetch("/kent-rehberi/kamu-kuruluslari")
            if not soup:
                return 0
            
            table = soup.select_one("table")
            if table:
                rows = table.select("tr")
                for row in rows[1:]:
                    cols = row.select("td")
                    if len(cols) >= 1:
                        name = self.clean_text(cols[0].get_text())
                        phone = self.clean_text(cols[1].get_text()) if len(cols) > 1 else None
                        
                        if name:
                            record = PublicInstitution(
                                name=name,
                                phone=phone,
                                source_url=f"{self.BASE_URL}/kent-rehberi/kamu-kuruluslari"
                            )
                            db.add(record)
                            count += 1
            
            db.commit()
            logger.info(f"PublicInstitutions: {count} records saved")
        except Exception as e:
            logger.error(f"PublicInstitutions error: {e}")
            db.rollback()
        finally:
            db.close()
        
        return count
    
    def scrape_health_facilities(self) -> int:
        """Sağlık kuruluşlarını çek"""
        db = SessionLocal()
        count = 0
        
        try:
            db.query(HealthFacility).delete()
            
            soup = self.fetch("/kent-rehberi/saglik-kuruluslari")
            if not soup:
                return 0
            
            table = soup.select_one("table")
            if table:
                rows = table.select("tr")
                for row in rows[1:]:
                    cols = row.select("td")
                    if len(cols) >= 1:
                        name = self.clean_text(cols[0].get_text())
                        phone = self.clean_text(cols[1].get_text()) if len(cols) > 1 else None
                        
                        if name:
                            record = HealthFacility(
                                name=name,
                                type="hastane" if "hastane" in name.lower() else "saglik_merkezi",
                                phone=phone,
                                source_url=f"{self.BASE_URL}/kent-rehberi/saglik-kuruluslari"
                            )
                            db.add(record)
                            count += 1
            
            db.commit()
            logger.info(f"HealthFacilities: {count} records saved")
        except Exception as e:
            logger.error(f"HealthFacilities error: {e}")
            db.rollback()
        finally:
            db.close()
        
        return count
    
    def scrape_schools(self) -> int:
        """Okulları çek"""
        db = SessionLocal()
        count = 0
        
        try:
            db.query(School).delete()
            
            soup = self.fetch("/kent-rehberi/okullar")
            if not soup:
                return 0
            
            table = soup.select_one("table")
            if table:
                rows = table.select("tr")
                for row in rows[1:]:
                    cols = row.select("td")
                    if len(cols) >= 1:
                        name = self.clean_text(cols[0].get_text())
                        
                        # Seviye belirle
                        level = "genel"
                        if "ilkokul" in name.lower():
                            level = "ilkokul"
                        elif "ortaokul" in name.lower():
                            level = "ortaokul"
                        elif "lise" in name.lower():
                            level = "lise"
                        
                        if name:
                            record = School(
                                name=name,
                                level=level,
                                source_url=f"{self.BASE_URL}/kent-rehberi/okullar"
                            )
                            db.add(record)
                            count += 1
            
            db.commit()
            logger.info(f"Schools: {count} records saved")
        except Exception as e:
            logger.error(f"Schools error: {e}")
            db.rollback()
        finally:
            db.close()
        
        return count
    
    def scrape_hotels(self) -> int:
        """Otelleri çek - Card yapısı"""
        db = SessionLocal()
        count = 0
        
        try:
            db.query(Hotel).delete()
            
            soup = self.fetch("/kent-rehberi/oteller")
            if not soup:
                return 0
            
            # Card yapısı: .item .cs-item-cont
            items = soup.select(".item")
            
            for item in items:
                cont = item.select_one(".cs-item-cont")
                if not cont:
                    continue
                
                name_elem = cont.select_one("h3 a")
                name = self.clean_text(name_elem.get_text()) if name_elem else None
                
                if not name:
                    continue
                
                # Yıldız sayısı
                stars = 0
                stars_elem = cont.select_one("span")
                if stars_elem:
                    stars_text = stars_elem.get_text()
                    for i in range(5, 0, -1):
                        if str(i) in stars_text:
                            stars = i
                            break
                
                # Adres
                address_elem = cont.select_one("p")
                address = self.clean_text(address_elem.get_text()) if address_elem else None
                
                # Website
                website_elem = cont.select_one("a[target='_blank']")
                website = website_elem.get("href") if website_elem else None
                
                record = Hotel(
                    name=name,
                    stars=stars,
                    address=address,
                    website=website,
                    source_url=f"{self.BASE_URL}/kent-rehberi/oteller"
                )
                db.add(record)
                count += 1
            
            db.commit()
            logger.info(f"Hotels: {count} records saved")
        except Exception as e:
            logger.error(f"Hotels error: {e}")
            db.rollback()
        finally:
            db.close()
        
        return count
    
    def scrape_libraries(self) -> int:
        """Kütüphaneleri çek"""
        db = SessionLocal()
        count = 0
        
        try:
            db.query(Library).delete()
            
            soup = self.fetch("/kent-rehberi/kutuphaneler")
            if not soup:
                return 0
            
            table = soup.select_one("table")
            if table:
                rows = table.select("tr")
                for row in rows[1:]:
                    cols = row.select("td")
                    if len(cols) >= 1:
                        name = self.clean_text(cols[0].get_text())
                        
                        if name:
                            record = Library(
                                name=name,
                                source_url=f"{self.BASE_URL}/kent-rehberi/kutuphaneler"
                            )
                            db.add(record)
                            count += 1
            
            db.commit()
            logger.info(f"Libraries: {count} records saved")
        except Exception as e:
            logger.error(f"Libraries error: {e}")
            db.rollback()
        finally:
            db.close()
        
        return count
    
    # =========================================================================
    # YEREL
    # =========================================================================
    
    def scrape_neighborhoods(self) -> int:
        """Mahalleleri çek - Çoklu tablo"""
        db = SessionLocal()
        count = 0
        
        try:
            db.query(Neighborhood).delete()
            
            soup = self.fetch("/kent-rehberi/muhtarliklarimiz")
            if not soup:
                return 0
            
            # Tüm tabloları bul (Merkez, Helvacı, Şakran, Kırsal)
            tables = soup.select("table")
            
            for table in tables:
                rows = table.select("tr")
                for row in rows:
                    # Header satırını atla
                    if row.select("th"):
                        continue
                    
                    cols = row.select("td")
                    if len(cols) >= 1:
                        name = self.clean_text(cols[0].get_text())
                        muhtar = self.clean_text(cols[1].get_text()) if len(cols) > 1 else None
                        phone = self.clean_text(cols[2].get_text()) if len(cols) > 2 else None
                        address = self.clean_text(cols[3].get_text()) if len(cols) > 3 else None
                        
                        if name and name.lower() not in ['mahalle', 'köy', 'muhtar']:
                            record = Neighborhood(
                                name=name,
                                muhtar_name=muhtar,
                                phone=phone,
                                address=address,
                                source_url=f"{self.BASE_URL}/kent-rehberi/muhtarliklarimiz"
                            )
                            db.add(record)
                            count += 1
            
            db.commit()
            logger.info(f"Neighborhoods: {count} records saved")
        except Exception as e:
            logger.error(f"Neighborhoods error: {e}")
            db.rollback()
        finally:
            db.close()
        
        return count
    
    def scrape_municipal_services(self) -> int:
        """Belediye hizmetlerini çek"""
        db = SessionLocal()
        count = 0
        
        services = [
            ("/hizmetlerimiz/iste-aliaga", "İş'te Aliağa", "is"),
            ("/hizmetlerimiz/aliaga-kent-kitapligi", "Kent Kitaplığı", "kutuphane"),
            ("/hizmetlerimiz/aziz-sancar-kutuphanesi", "Aziz Sancar Kütüphanesi", "kutuphane"),
            ("/hizmetlerimiz/nadir-nadi-kutuphanesi", "Nadir Nadi Kütüphanesi", "kutuphane"),
            ("/hizmetlerimiz/santranc-kulubu", "Santranç Kulübü", "spor"),
            ("/hizmetlerimiz/nikah-islemleri", "Nikah İşlemleri", "sosyal"),
            ("/hizmetlerimiz/sifir-atik", "Sıfır Atık", "cevre"),
            ("/hizmetlerimiz/sosyal-market", "Sosyal Market", "sosyal"),
            ("/hizmetlerimiz/cop-ekspres", "Çöp Ekspres", "cevre"),
            ("/hizmetlerimiz/milletin-ekibi", "Milletin Ekibi", "sosyal"),
            ("/hizmetlerimiz/kultur-gezileri-ve-sehitlik-ziyaretleri", "Kültür Gezileri", "kultur"),
            ("/hizmetlerimiz/aliaga-sanat-evi-asev", "ASEV", "kultur"),
        ]
        
        try:
            db.query(MunicipalService).delete()
            
            for path, name, category in services:
                soup = self.fetch(path)
                if not soup:
                    continue
                
                content = self._extract_content(soup)
                if content:
                    record = MunicipalService(
                        name=name,
                        category=category,
                        description=content[:3000],
                        source_url=f"{self.BASE_URL}{path}"
                    )
                    db.add(record)
                    count += 1
            
            db.commit()
            logger.info(f"MunicipalServices: {count} records saved")
        except Exception as e:
            logger.error(f"MunicipalServices error: {e}")
            db.rollback()
        finally:
            db.close()
        
        return count
    
    def scrape_pharmacy_duties(self) -> int:
        """Nöbetçi eczaneleri çek"""
        db = SessionLocal()
        count = 0
        
        try:
            # Bugünkü kayıtları sil
            db.query(PharmacyDuty).filter(PharmacyDuty.duty_date == date.today()).delete()
            
            soup = self.fetch("/kent-rehberi/nobetci-eczane")
            if not soup:
                return 0
            
            items = soup.select(".nobetci .liste .item")
            if not items:
                items = soup.select(".liste .item") or soup.select(".item")
            
            for item in items:
                name_elem = item.select_one(".title .tbaslik, .tbaslik, .title")
                name = self.clean_text(name_elem.get_text()) if name_elem else None
                
                if not name:
                    continue
                
                # Adres ve telefon
                address = None
                phone = None
                arows = item.select(".detay .isol .arow")
                for i, arow in enumerate(arows):
                    val_elem = arow.select_one(".val")
                    if val_elem:
                        text = self.clean_text(val_elem.get_text())
                        if i == 0:
                            address = text
                        elif i == 1:
                            phone = text
                
                # Maps link
                maps_elem = item.select_one(".detay .isag a, a[href*='maps']")
                maps_link = maps_elem.get("href") if maps_elem else None
                
                record = PharmacyDuty(
                    name=name,
                    address=address,
                    phone=phone,
                    maps_link=maps_link,
                    duty_date=date.today()
                )
                db.add(record)
                count += 1
            
            db.commit()
            logger.info(f"PharmacyDuties: {count} records saved")
        except Exception as e:
            logger.error(f"PharmacyDuties error: {e}")
            db.rollback()
        finally:
            db.close()
        
        return count
    
    # =========================================================================
    # HELPER
    # =========================================================================
    
    def _extract_content(self, soup) -> Optional[str]:
        """Sayfa içeriğini çıkar"""
        content_area = None
        for selector in [".sayfa-text", ".sayfa-icerik", ".page-content", ".content", "article"]:
            content_area = soup.select_one(selector)
            if content_area:
                break
        
        if not content_area:
            return None
        
        # Gereksiz elementleri kaldır
        for elem in content_area.select("script, style, nav, footer, .sidebar, .menu"):
            elem.decompose()
        
        paragraphs = content_area.find_all("p")
        content = "\n\n".join(
            self.clean_text(p.get_text()) 
            for p in paragraphs 
            if self.clean_text(p.get_text())
        )
        
        if not content:
            content = self.clean_text(content_area.get_text())
        
        return content[:10000] if content else None
    
    # =========================================================================
    # RUN ALL
    # =========================================================================
    
    def run_all(self) -> Dict[str, int]:
        """Tüm scraperları çalıştır"""
        results = {}
        
        print("Scraping başlıyor...")
        
        # Şehir bilgisi
        results["history"] = self.scrape_history()
        results["geography"] = self.scrape_geography()
        results["economy"] = self.scrape_economy()
        results["culture"] = self.scrape_culture()
        results["education_info"] = self.scrape_education_info()
        results["health_info"] = self.scrape_health_info()
        results["transport"] = self.scrape_transport()
        
        # Turizm
        results["antique_cities"] = self.scrape_antique_cities()
        results["gastronomy"] = self.scrape_gastronomy()
        results["hiking_routes"] = self.scrape_hiking_routes()
        
        # Kurumlar
        results["emergency_phones"] = self.scrape_emergency_phones()
        results["public_institutions"] = self.scrape_public_institutions()
        results["health_facilities"] = self.scrape_health_facilities()
        results["schools"] = self.scrape_schools()
        results["hotels"] = self.scrape_hotels()
        results["libraries"] = self.scrape_libraries()
        
        # Yerel
        results["neighborhoods"] = self.scrape_neighborhoods()
        results["municipal_services"] = self.scrape_municipal_services()
        results["pharmacy_duties"] = self.scrape_pharmacy_duties()
        
        total = sum(results.values())
        print(f"\nTOPLAM: {total} kayıt")
        
        return results
