import asyncio
import httpx
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger
import urllib.parse

from app.models.places import Place, Institution
from app.database import async_session
from app.services.chunk_indexer import sync_all_document_chunks
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Aliağa'yı kapsayan sınırları Overpass QL ile çekmek için Bounding Box:
# (Güney Enlem, Batı Boylam, Kuzey Enlem, Doğu Boylam)
# Aliağa kabaca: 38.70, 26.85, 38.95, 27.15

OVERPASS_QUERY = """
[out:json][timeout:60];
// Aliağa ilçe sınırları içindeki tüm isimlendirilmiş yerler
area["name"="Aliağa"]["admin_level"="6"]->.searchArea;
(
  node["name"]["amenity"](area.searchArea);
  way["name"]["amenity"](area.searchArea);
  node["name"]["shop"](area.searchArea);
  way["name"]["shop"](area.searchArea);
  node["name"]["tourism"](area.searchArea);
  way["name"]["tourism"](area.searchArea);
  node["name"]["leisure"](area.searchArea);
  way["name"]["leisure"](area.searchArea);
  node["name"]["historic"](area.searchArea);
  way["name"]["historic"](area.searchArea);
  node["name"]["healthcare"](area.searchArea);
  way["name"]["healthcare"](area.searchArea);
);
out center;
"""

def determine_category(tags):
    amenity = tags.get("amenity")
    shop = tags.get("shop")
    tourism = tags.get("tourism")
    leisure = tags.get("leisure")
    historic = tags.get("historic")
    healthcare = tags.get("healthcare")
    
    if amenity in ["restaurant", "cafe", "fast_food", "bar", "pub", "ice_cream"]:
        return "place", "restoran" if amenity in ["restaurant", "fast_food"] else "kafe", amenity
    if amenity in ["hospital", "clinic", "doctors", "dentist", "pharmacy"]:
        return "institution", "saglik", amenity
    if amenity in ["school", "kindergarten", "college", "university", "library"]:
        return "institution", "egitim", amenity
    if amenity in ["police", "fire_station", "townhall", "courthouse", "post_office", "prison"]:
        return "institution", "kamu", amenity
    if amenity in ["bank", "atm"]:
        return "place", "finans", amenity
    if amenity in ["place_of_worship"]:
        return "institution", "ibadethane", tags.get("religion", "dini_tesis")
    if amenity in ["fuel", "parking", "car_wash", "taxi"]:
        return "place", "ulasim", amenity
    
    if shop:
        cat = "market" if shop in ["supermarket", "convenience", "bakery", "butcher"] else "magaza"
        return "place", cat, shop
        
    if tourism:
        cat = "konaklama" if tourism in ["hotel", "motel", "hostel", "guest_house"] else "turistik"
        return "place", cat, tourism
        
    if leisure in ["park", "pitch", "sports_centre", "stadium", "fitness_centre"]:
        return "institution" if leisure in ["sports_centre", "stadium"] else "place", "spor_park", leisure
        
    if historic:
        return "place", "tarihi_yer", historic
        
    if healthcare:
        return "institution", "saglik", healthcare
        
    return "place", "diger", "bilinmeyen"

async def fetch_osm_data():
    logger.info("Overpass API'den devasa Aliağa verisi çekiliyor. (Bu işlem 10-30 saniye sürebilir)...")
    headers = {"User-Agent": "AliagaAIBot/1.0"}
    async with httpx.AsyncClient(timeout=60.0, headers=headers) as client:
        response = await client.post(OVERPASS_URL, data={"data": OVERPASS_QUERY})
        response.raise_for_status()
        return response.json()

async def sync_osm_places():
    data = await fetch_osm_data()
    elements = data.get("elements", [])
    logger.info(f"Overpass API'den toplam {len(elements)} adet isimlendirilmiş yer (mekan/kurum) bulundu!")
    
    places_added = 0
    institutions_added = 0
    
    async with async_session() as session:
        # Var olan isimleri çekelim ki duplicate olmasın (Büyük-küçük harf duyarsız kontrol için)
        existing_places = await session.execute(select(Place.name))
        existing_places_set = {n.lower() for n in existing_places.scalars().all()}
        
        existing_insts = await session.execute(select(Institution.name))
        existing_insts_set = {n.lower() for n in existing_insts.scalars().all()}

        for el in elements:
            tags = el.get("tags", {})
            name = tags.get("name")
            if not name:
                continue
                
            lat = el.get("lat") or el.get("center", {}).get("lat")
            lon = el.get("lon") or el.get("center", {}).get("lon")
            
            table_type, category, subcat = determine_category(tags)
            
            phone = tags.get("phone") or tags.get("contact:phone")
            website = tags.get("website") or tags.get("contact:website")
            opening_hours = tags.get("opening_hours")
            
            # Adres oluşturma
            street = tags.get("addr:street", "")
            housenumber = tags.get("addr:housenumber", "")
            city = tags.get("addr:city", "Aliağa")
            address = f"{street} {housenumber}, {city}".strip(", ")
            if not address or address == "Aliağa":
                address = None
                
            description_parts = []
            if opening_hours:
                description_parts.append(f"Çalışma Saatleri: {opening_hours}")
            if tags.get("cuisine"):
                description_parts.append(f"Mutfak/Tür: {tags.get('cuisine')}")
            description = " | ".join(description_parts) if description_parts else None

            if table_type == "place":
                if name.lower() not in existing_places_set:
                    place = Place(
                        name=name,
                        category=category,
                        subcategory=subcat,
                        address=address,
                        phone=phone,
                        website=website,
                        latitude=lat,
                        longitude=lon,
                        description=description
                    )
                    session.add(place)
                    existing_places_set.add(name.lower())
                    places_added += 1
            else:
                if name.lower() not in existing_insts_set:
                    inst = Institution(
                        name=name,
                        category=category,
                        subcategory=subcat,
                        address=address,
                        phone=phone,
                        website=website,
                        latitude=lat,
                        longitude=lon,
                        description=description
                    )
                    session.add(inst)
                    existing_insts_set.add(name.lower())
                    institutions_added += 1
                    
        await session.commit()
        logger.info(f"Veritabanına eklendi: {places_added} yeni mekan, {institutions_added} yeni kurum.")
        
        if places_added > 0 or institutions_added > 0:
            logger.info("Yeni eklenen yüzlerce veri için RAG Vektörleri oluşturuluyor...")
            await sync_all_document_chunks(session, source_types=["place", "institution"])
            logger.info("Vektör eşitlemesi tamamlandı!")

if __name__ == "__main__":
    asyncio.run(sync_osm_places())
