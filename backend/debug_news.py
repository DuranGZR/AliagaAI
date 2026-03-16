"""Deep debug for news title extraction"""
from app.scrapers.base import BaseScraper

scraper = BaseScraper()
soup = scraper.fetch('/haberler')

if soup:
    items = soup.select(".list .item a")
    print(f"Found {len(items)} items")
    
    for i, item in enumerate(items[:3]):  # ilk 3 haber
        print(f"\n=== ITEM {i+1} ===")
        link = item.get("href", "")
        print(f"Link: {link}")
        print(f"Contains /haber/: {'/haber/' in link}")
        
        # Title denemeleri
        t1 = item.select_one("div:nth-child(2) div:first-child")
        print(f"div:nth-child(2) div:first-child: {t1.get_text()[:50] if t1 else 'NONE'}")
        
        t2 = item.select_one("div div")
        print(f"div div: {t2.get_text()[:50] if t2 else 'NONE'}")
        
        # Tum children
        divs = item.select("div")
        print(f"Total divs: {len(divs)}")
        for j, div in enumerate(divs[:5]):
            print(f"  div[{j}]: {div.get_text()[:30]}...")
