"""
Test script - Scraper'ları test et
"""
import sys
sys.path.insert(0, '.')

from app.database import init_db
from app.scrapers import PharmacyScraper, InstitutionsScraper, TourismScraper

print("=" * 50)
print("AliağaAI Scraper Test")
print("=" * 50)

# Database oluştur
print("\n1. Database oluşturuluyor...")
init_db()
print("   ✅ Database hazır")

# Pharmacy test
print("\n2. Nöbetçi Eczane test ediliyor...")
try:
    with PharmacyScraper() as scraper:
        pharmacies = scraper.scrape()
        print(f"   ✅ {len(pharmacies)} eczane bulundu")
        if pharmacies:
            for p in pharmacies[:3]:
                print(f"      - {p.get('name', 'N/A')}")
except Exception as e:
    print(f"   ❌ Hata: {e}")

# Institutions test
print("\n3. Kamu Kuruluşları test ediliyor...")
try:
    with InstitutionsScraper() as scraper:
        data = scraper.scrape_category("acil")
        print(f"   ✅ Acil telefonlar: {len(data)} kayıt")
        if data:
            for item in data[:3]:
                print(f"      - {item.get('name', 'N/A')}: {item.get('phone', 'N/A')}")
except Exception as e:
    print(f"   ❌ Hata: {e}")

# Tourism test  
print("\n4. Turistik Bilgiler test ediliyor...")
try:
    with TourismScraper() as scraper:
        info = scraper.scrape_topic("tarih")
        if info and info.get("content"):
            print(f"   ✅ Tarih bilgisi: {len(info['content'])} karakter")
            print(f"      Başlık: {info.get('title', 'N/A')}")
        else:
            print("   ⚠️ İçerik bulunamadı")
except Exception as e:
    print(f"   ❌ Hata: {e}")

print("\n" + "=" * 50)
print("Test tamamlandı!")
print("=" * 50)
