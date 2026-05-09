"""Scrape Wikipedia for Aliaga knowledge and populate the database."""
import asyncio
import requests
import re
from datetime import date
from sqlalchemy import select
from app.database import async_session
from app.models.city import CityKnowledge

# The Wikipedia pages we want to scrape
WIKI_PAGES = [
    {"title": "Aliağa", "layer": "genel", "neighborhood": None},
    {"title": "Kyme", "layer": "tarih", "neighborhood": "Namurt"},
    {"title": "Aigai (Aiolis)", "layer": "tarih", "neighborhood": "Yukarı Semt"},
    {"title": "Gryneion", "layer": "tarih", "neighborhood": "Yeni Şakran"},
    {"title": "Çandarlı Körfezi", "layer": "coğrafya", "neighborhood": None},
    {"title": "Helvacı, İzmir", "layer": "mahalle", "neighborhood": "Helvacı"},
    {"title": "Yeni Şakran", "layer": "mahalle", "neighborhood": "Yeni Şakran"},
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
        "User-Agent": "AliagaAI/1.0 (https://github.com/duran/aliagaai; bot@example.com)"
    }
    response = requests.get(API_URL, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    pages = data.get("query", {}).get("pages", {})
    for page_id, page_data in pages.items():
        if page_id != "-1":
            return page_data.get("extract", "")
    return ""

def parse_extract(title: str, extract: str, layer: str, neighborhood: str) -> list[dict]:
    # Split the extract into sections based on == Heading ==
    lines = extract.split("\n")
    current_heading = "Genel Bilgi"
    buffer = []
    
    parsed_chunks = []
    
    def save_chunk():
        text = " ".join(buffer).strip()
        if len(text) > 50:
            parsed_chunks.append({
                "layer": layer,
                "title": f"{title} - {current_heading}",
                "neighborhood": neighborhood,
                "summary": text,
                "tags": ["wikipedia", title.lower(), layer],
                "source_url": f"https://tr.wikipedia.org/wiki/{title.replace(' ', '_')}",
                "last_verified_at": date.today()
            })
        buffer.clear()

    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Match == Heading == or === Subheading ===
        heading_match = re.match(r'^(={2,4})\s*(.+?)\s*\1$', line)
        if heading_match:
            save_chunk()
            current_heading = heading_match.group(2).strip()
        else:
            # It's a paragraph
            buffer.append(line)
            
            # If buffer gets too large (e.g. over 800 chars), save it so chunks aren't massive
            if sum(len(s) for s in buffer) > 800:
                save_chunk()
                
    save_chunk() # Save the last buffer
    return parsed_chunks

async def main():
    print("=== Wikipedia Scraping Started ===")
    
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
        # Get existing titles to avoid exact duplicates
        existing = (await session.execute(select(CityKnowledge.title))).scalars().all()
        existing_titles = set(existing)
        
        inserted_count = 0
        for data in all_knowledge_data:
            # Append a number if duplicate title exists in this scrape session
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
