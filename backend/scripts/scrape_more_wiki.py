"""Scrape Wikipedia for additional Aliaga knowledge (neighborhoods, industries) and populate the database."""
import asyncio
import requests
import re
from datetime import date
from sqlalchemy import select
from app.database import async_session
from app.models.city import CityKnowledge

# The Wikipedia pages we want to scrape
WIKI_PAGES = [
    {"title": "Petkim", "layer": "sanayi", "neighborhood": "Siteler"},
    {"title": "TÜPRAŞ", "layer": "sanayi", "neighborhood": "Siteler"},
    {"title": "Bozköy, Aliağa", "layer": "mahalle", "neighborhood": "Bozköy"},
    {"title": "Çakmaklı, Aliağa", "layer": "mahalle", "neighborhood": "Çakmaklı"},
    {"title": "Çaltıdere, Aliağa", "layer": "mahalle", "neighborhood": "Çaltıdere"},
    {"title": "Çoraklar, Aliağa", "layer": "mahalle", "neighborhood": "Çoraklar"},
    {"title": "Güzelhisar, Aliağa", "layer": "mahalle", "neighborhood": "Güzelhisar"},
    {"title": "Hacıömerli, Aliağa", "layer": "mahalle", "neighborhood": "Hacıömerli"},
    {"title": "Kalabak, Aliağa", "layer": "mahalle", "neighborhood": "Kalabak"},
    {"title": "Kapaklı, Aliağa", "layer": "mahalle", "neighborhood": "Kapaklı"},
    {"title": "Karaköy, Aliağa", "layer": "mahalle", "neighborhood": "Karaköy"},
    {"title": "Karakuzu, Aliağa", "layer": "mahalle", "neighborhood": "Karakuzu"},
    {"title": "Samurlu, Aliağa", "layer": "mahalle", "neighborhood": "Samurlu"},
    {"title": "Şehitkemal, Aliağa", "layer": "mahalle", "neighborhood": "Şehitkemal"},
    {"title": "Uzunhasanlar, Aliağa", "layer": "mahalle", "neighborhood": "Uzunhasanlar"},
    {"title": "Yüksekköy, Aliağa", "layer": "mahalle", "neighborhood": "Yüksekköy"},
    {"title": "Aliağa Gençlik Merkezi", "layer": "kurumlar", "neighborhood": "Atatürk"},
]

API_URL = "https://tr.wikipedia.org/w/api.php"

def fetch_wikipedia_extract(title: str) -> str:
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": 1,
        "titles": title,
        "format": "json",
        "redirects": 1
    }
    headers = {
        "User-Agent": "AliagaAI/1.1 (https://github.com/duran/aliagaai; bot@example.com)"
    }
    response = requests.get(API_URL, params=params, headers=headers)
    if response.status_code != 200:
        return ""
    data = response.json()
    pages = data.get("query", {}).get("pages", {})
    for page_id, page_data in pages.items():
        if page_id != "-1":
            return page_data.get("extract", "")
    return ""

def parse_extract(title: str, extract: str, layer: str, neighborhood: str) -> list[dict]:
    lines = extract.split("\n")
    current_heading = "Genel Bilgi"
    buffer = []
    
    parsed_chunks = []
    
    def save_chunk():
        text = " ".join(buffer).strip()
        # Clean up empty sections like "Nüfus" that only have tables in HTML but nothing in text
        if len(text) > 40 and not text.isspace():
            parsed_chunks.append({
                "layer": layer,
                "title": f"{title} - {current_heading}",
                "neighborhood": neighborhood,
                "summary": text,
                "tags": ["wikipedia", title.split(',')[0].lower().strip(), layer],
                "source_url": f"https://tr.wikipedia.org/wiki/{title.replace(' ', '_')}",
                "last_verified_at": date.today()
            })
        buffer.clear()

    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        heading_match = re.match(r'^(={2,4})\s*(.+?)\s*\1$', line)
        if heading_match:
            save_chunk()
            current_heading = heading_match.group(2).strip()
        else:
            buffer.append(line)
            if sum(len(s) for s in buffer) > 600:
                save_chunk()
                
    save_chunk()
    return parsed_chunks

async def main():
    print("=== Additional Wikipedia Scraping Started ===")
    
    all_knowledge_data = []
    
    for page in WIKI_PAGES:
        print(f"Fetching: {page['title']}...")
        extract = fetch_wikipedia_extract(page["title"])
        if not extract:
            print(f"  Warning: No content found for {page['title']}")
            continue
            
        chunks = parse_extract(page["title"], extract, page["layer"], page["neighborhood"])
        print(f"  -> Extracted {len(chunks)} chunks.")
        all_knowledge_data.extend(chunks)

    print(f"\nTotal extracted chunks: {len(all_knowledge_data)}")
    
    async with async_session() as session:
        print("\n=== Saving to Database ===")
        existing = (await session.execute(select(CityKnowledge.title))).scalars().all()
        existing_titles = set(existing)
        
        inserted_count = 0
        for data in all_knowledge_data:
            base_title = data["title"]
            title = base_title
            counter = 1
            while title in existing_titles:
                title = f"{base_title} (Bölüm {counter})"
                counter += 1
                
            data["title"] = title
            existing_titles.add(title)
            
            session.add(CityKnowledge(**data))
            inserted_count += 1
            
        await session.commit()
        print(f"Inserted {inserted_count} new CityKnowledge records.")
        
        if inserted_count > 0:
            print("\n=== Syncing Vector DB (document_chunks) ===")
            from app.services.chunk_indexer import sync_all_document_chunks
            results = await sync_all_document_chunks(
                session, 
                source_types=["city_knowledge"]
            )
            
            ck_result = results.get("city_knowledge", {})
            print(f"Vector sync complete. Indexed: {ck_result.get('indexed', 0)}, Unchanged: {ck_result.get('unchanged', 0)}")
            await session.commit()

if __name__ == "__main__":
    asyncio.run(main())
