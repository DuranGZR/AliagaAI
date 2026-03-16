"""
Dinamik Veri Scraperları v2
Haberler, Duyurular, Etkinlikler, Projeler
Doğru CSS selector'lar ile
"""

from typing import List, Dict, Any, Optional
import logging
import re
from datetime import datetime, date

from .base import BaseScraper
from app.models import News, Announcement, Event, Project
from app.database import SessionLocal

logger = logging.getLogger(__name__)


class DynamicScraper(BaseScraper):
    """Haberler, Duyurular, Etkinlikler, Projeler için scraper"""
    
    def scrape_news(self, pages: int = 2) -> int:
        """Haberleri çek - .list .item a yapısı"""
        db = SessionLocal()
        count = 0
        
        try:
            for page_num in range(1, pages + 1):
                url = f"/haberler?sayfa={page_num}" if page_num > 1 else "/haberler"
                soup = self.fetch(url)
                if not soup:
                    continue
                
                # Doğru selector: .list .item a
                items = soup.select(".list .item a")
                
                if not items:
                    # Alternatif: a[href*='/haber/']
                    items = soup.select("a[href*='/haber/']")
                
                logger.info(f"News page {page_num}: Found {len(items)} items")
                
                for item in items:
                    try:
                        # Link
                        link = item.get("href", "")
                        if not link or "/haber/" not in link:
                            continue
                        if not link.startswith("http"):
                            link = f"{self.BASE_URL}{link}"
                        
                        # Duplicate kontrolü
                        existing = db.query(News).filter(News.source_url == link).first()
                        if existing:
                            continue
                        
                        # Başlık - divs içinde
                        title = None
                        divs = item.find_all("div", recursive=False)
                        
                        # Resimli yapı: divs[1] content, divs[0] image
                        # Title genelde 2. veya 3. div'de
                        for div in divs[1:4] if len(divs) > 1 else divs[:3]:
                            text = self.clean_text(div.get_text())
                            if text and len(text) > 5:
                                title = text
                                break
                        
                        if not title:
                            continue
                        
                        # Tarih - div:nth-child(2) div:nth-child(3)
                        pub_date = None
                        date_elem = item.select_one("div:nth-child(2) div:nth-child(3)")
                        if date_elem:
                            date_text = date_elem.get_text().strip()
                            pub_date = self._parse_turkish_date(date_text)
                        
                        # Resim
                        img_elem = item.select_one("img")
                        img_url = img_elem.get("src") if img_elem else None
                        if img_url and not img_url.startswith("http"):
                            img_url = f"{self.BASE_URL}{img_url}"
                        
                        record = News(
                            title=title[:500],
                            published_date=pub_date or date.today(),
                            image_url=img_url,
                            source_url=link
                        )
                        db.add(record)
                        count += 1
                        
                    except Exception as e:
                        logger.error(f"News item error: {e}")
                        continue
            
            db.commit()
            logger.info(f"News: {count} new records saved")
        except Exception as e:
            logger.error(f"News scraper error: {e}")
            db.rollback()
        finally:
            db.close()
        
        return count
    
    def scrape_announcements(self, pages: int = 2) -> int:
        """Duyuruları çek - .list .item a yapısı"""
        db = SessionLocal()
        count = 0
        
        try:
            for page_num in range(1, pages + 1):
                url = f"/duyurular?sayfa={page_num}" if page_num > 1 else "/duyurular"
                soup = self.fetch(url)
                if not soup:
                    continue
                
                # Doğru selector
                items = soup.select(".list .item a")
                if not items:
                    items = soup.select("a[href*='/duyuru/']")
                
                logger.info(f"Announcements page {page_num}: Found {len(items)} items")
                
                for item in items:
                    try:
                        link = item.get("href", "")
                        if not link or "/duyuru/" not in link:
                            continue
                        if not link.startswith("http"):
                            link = f"{self.BASE_URL}{link}"
                        
                        # Duplicate kontrolü
                        existing = db.query(Announcement).filter(Announcement.source_url == link).first()
                        if existing:
                            continue
                        
                        # Başlık - divs içinde
                        title = None
                        divs = item.find_all("div", recursive=False)
                        
                        for div in divs[:4]:
                            text = self.clean_text(div.get_text())
                            if text and len(text) > 5:
                                title = text
                                break
                        
                        if not title:
                            continue
                        
                        # Tarih
                        pub_date = None
                        date_elem = item.select_one("div:nth-child(1) div:nth-child(3), div:nth-child(2) div:nth-child(3)")
                        if date_elem:
                            date_text = date_elem.get_text().strip()
                            pub_date = self._parse_turkish_date(date_text)
                        
                        # Tip belirleme
                        ann_type = "duyuru"
                        title_lower = title.lower()
                        if "ihale" in title_lower:
                            ann_type = "ihale"
                        elif "ilan" in title_lower:
                            ann_type = "ilan"
                        
                        record = Announcement(
                            title=title[:500],
                            type=ann_type,
                            published_date=pub_date or date.today(),
                            source_url=link
                        )
                        db.add(record)
                        count += 1
                        
                    except Exception as e:
                        logger.error(f"Announcement item error: {e}")
                        continue
            
            db.commit()
            logger.info(f"Announcements: {count} new records saved")
        except Exception as e:
            logger.error(f"Announcements scraper error: {e}")
            db.rollback()
        finally:
            db.close()
        
        return count
    
    def scrape_events(self) -> int:
        """Etkinlikleri çek (şu an boş olabilir)"""
        db = SessionLocal()
        count = 0
        
        try:
            soup = self.fetch("/etkinlikler")
            if not soup:
                return 0
            
            items = soup.select(".list .item a, a[href*='/etkinlik/']")
            logger.info(f"Events: Found {len(items)} items")
            
            for item in items:
                try:
                    link = item.get("href", "")
                    if not link:
                        continue
                    if not link.startswith("http"):
                        link = f"{self.BASE_URL}{link}"
                    
                    # Duplicate kontrolü
                    existing = db.query(Event).filter(Event.source_url == link).first()
                    if existing:
                        continue
                    
                    # Başlık
                    title_elem = item.select_one("div div")
                    title = self.clean_text(title_elem.get_text()) if title_elem else None
                    
                    if not title:
                        continue
                    
                    # Tarih
                    event_date = None
                    date_elem = item.select_one("div:nth-child(2) div:nth-child(3)")
                    if date_elem:
                        date_text = date_elem.get_text().strip()
                        event_date = self._parse_turkish_date(date_text)
                    
                    # Kategori belirleme
                    category = "genel"
                    title_lower = title.lower()
                    if "konser" in title_lower:
                        category = "konser"
                    elif "tiyatro" in title_lower:
                        category = "tiyatro"
                    elif "festival" in title_lower:
                        category = "festival"
                    
                    # Resim
                    img_elem = item.select_one("img")
                    img_url = img_elem.get("src") if img_elem else None
                    if img_url and not img_url.startswith("http"):
                        img_url = f"{self.BASE_URL}{img_url}"
                    
                    record = Event(
                        title=title[:500],
                        event_date=event_date or date.today(),
                        category=category,
                        image_url=img_url,
                        source_url=link
                    )
                    db.add(record)
                    count += 1
                    
                except Exception as e:
                    logger.error(f"Event item error: {e}")
                    continue
            
            db.commit()
            logger.info(f"Events: {count} new records saved")
        except Exception as e:
            logger.error(f"Events scraper error: {e}")
            db.rollback()
        finally:
            db.close()
        
        return count
    
    def scrape_projects(self) -> int:
        """Belediye projelerini çek - .piitem a yapısı"""
        db = SessionLocal()
        count = 0
        
        project_pages = [
            ("/projelerimiz/tamamlanan-projeler", "tamamlanan"),
            ("/projelerimiz/devam-eden-projeler", "devam_eden"),
        ]
        
        try:
            for path, status in project_pages:
                soup = self.fetch(path)
                if not soup:
                    continue
                
                # Doğru selector: .piitem a
                items = soup.select(".piitem a")
                if not items:
                    items = soup.select(f"a[href*='{path}/']")
                
                logger.info(f"Projects ({status}): Found {len(items)} items")
                
                for item in items:
                    try:
                        link = item.get("href", "")
                        if not link:
                            continue
                        if not link.startswith("http"):
                            link = f"{self.BASE_URL}{link}"
                        
                        # Duplicate kontrolü
                        existing = db.query(Project).filter(Project.source_url == link).first()
                        if existing:
                            continue
                        
                        # Başlık - iç içe div'ler
                        name = None
                        title_elem = item.select_one("div div div")
                        if title_elem:
                            name = self.clean_text(title_elem.get_text())
                        if not name:
                            # Alternatif: tüm text
                            name = self.clean_text(item.get_text())
                        
                        if not name or len(name) < 3:
                            continue
                        
                        # Resim
                        img_elem = item.select_one("img")
                        img_url = img_elem.get("src") if img_elem else None
                        if img_url and not img_url.startswith("http"):
                            img_url = f"{self.BASE_URL}{img_url}"
                        
                        # Kategori belirleme
                        category = "genel"
                        name_lower = name.lower()
                        if "park" in name_lower:
                            category = "park"
                        elif "yol" in name_lower or "asfalt" in name_lower:
                            category = "altyapi"
                        elif "sosyal" in name_lower:
                            category = "sosyal"
                        elif "spor" in name_lower:
                            category = "spor"
                        
                        record = Project(
                            name=name[:500],
                            status=status,
                            category=category,
                            image_url=img_url,
                            source_url=link
                        )
                        db.add(record)
                        count += 1
                        
                    except Exception as e:
                        logger.error(f"Project item error: {e}")
                        continue
            
            db.commit()
            logger.info(f"Projects: {count} new records saved")
        except Exception as e:
            logger.error(f"Projects scraper error: {e}")
            db.rollback()
        finally:
            db.close()
        
        return count
    
    def _parse_turkish_date(self, date_text: str) -> Optional[date]:
        """Türkçe tarih formatını parse et (örn: '15 Ocak 2026')"""
        months = {
            'ocak': 1, 'şubat': 2, 'mart': 3, 'nisan': 4,
            'mayıs': 5, 'haziran': 6, 'temmuz': 7, 'ağustos': 8,
            'eylül': 9, 'ekim': 10, 'kasım': 11, 'aralık': 12
        }
        
        try:
            # "15 Ocak 2026" formatı
            parts = date_text.lower().split()
            if len(parts) >= 3:
                day = int(parts[0])
                month = months.get(parts[1], 1)
                year = int(parts[2])
                return date(year, month, day)
        except:
            pass
        
        try:
            # "15.01.2026" formatı
            return datetime.strptime(date_text.strip(), "%d.%m.%Y").date()
        except:
            pass
        
        return None
    
    def run_all(self) -> Dict[str, int]:
        """Tüm dinamik verileri çek"""
        results = {}
        
        print("Dinamik veriler çekiliyor...")
        
        results["news"] = self.scrape_news(pages=2)
        results["announcements"] = self.scrape_announcements(pages=2)
        results["events"] = self.scrape_events()
        results["projects"] = self.scrape_projects()
        
        total = sum(results.values())
        print(f"\nTOPLAM: {total} yeni kayıt")
        
        return results
