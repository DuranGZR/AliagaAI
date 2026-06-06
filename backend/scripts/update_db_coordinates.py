import asyncio
from sqlalchemy import text
from app.database import async_session
from loguru import logger

# Mapping of search terms (lowercased) to corrected coordinates (lat, lon)
# Ordered by specificity (specific terms first)
COORDINATE_UPDATES = [
    ("güzelhisar barajı", (38.7953, 27.1206)),
    ("güzelhisar baraj gölü", (38.7953, 27.1206)),
    ("agapark", (38.8250, 26.9650)),
    ("ağapark", (38.8250, 26.9650)),
    ("kyme", (38.7600, 26.9360)),
    ("gryneion", (38.8744, 27.0692)),
    ("myrina", (38.8453, 26.9844)),
    ("yeni şakran sahili", (38.8870, 27.0600)),
    ("yeni şakran plajı", (38.8870, 27.0600)),
    ("şakran sahili", (38.8870, 27.0600)),
    ("kuş cenneti", (38.8040, 26.9695)),
    ("çaltıdere göleti", (38.8040, 26.9695)),
    ("çaltıdere delta", (38.8040, 26.9695)),
    ("uçansu şelalesi", (38.7408, 27.1679)),
    ("suuçuran şelalesi", (38.7408, 27.1679)),
    ("köstem koyu", (38.8589, 27.0088)),
    ("karanlık koy", (38.8950, 27.0500)),
    ("şakran bölgeler parkı", (38.8817, 27.0640)),
    ("kent parkı", (38.7908, 26.9759)),
    ("avcı ramadan", (38.8043, 26.9662)),
    ("gençlik merkezi", (38.8028, 26.9665)),
    ("karakuzu", (38.7610, 27.1080)),
    ("çamlık", (38.7998, 26.9790)),
    ("sanat evi", (38.7985, 26.9715)),
    ("asem", (38.7985, 26.9715)),
    ("kent kitaplığı", (38.7985, 26.9658)),
    ("kent arşivi", (38.7985, 26.9658)),
    ("ön plajlar", (38.8315, 26.9697)),
    ("plajlar bölgesi", (38.8315, 26.9697)),
    ("aigai", (38.8338, 27.1934)),
    ("güzelhisar", (38.7762, 27.0177))
]

async def update_coordinates():
    async with async_session() as session:
        # Update places
        result_places = await session.execute(text("SELECT id, name, latitude, longitude FROM places"))
        places = result_places.fetchall()
        
        updated_places_count = 0
        for pid, name, lat, lon in places:
            name_lower = name.lower()
            for key, (new_lat, new_lon) in COORDINATE_UPDATES:
                if key in name_lower:
                    # Only update if different
                    if lat != new_lat or lon != new_lon:
                        await session.execute(
                            text("UPDATE places SET latitude = :lat, longitude = :lon, updated_at = NOW() WHERE id = :id"),
                            {"lat": new_lat, "lon": new_lon, "id": pid}
                        )
                        logger.info(f"Updated Place '{name}' (ID: {pid}) from ({lat}, {lon}) to ({new_lat}, {new_lon})")
                        updated_places_count += 1
                    break
        
        # Update institutions (like Gençlik Merkezi or Kent Parkı or Güzelhisar or others)
        result_insts = await session.execute(text("SELECT id, name, latitude, longitude FROM institutions"))
        insts = result_insts.fetchall()
        
        updated_insts_count = 0
        for iid, name, lat, lon in insts:
            name_lower = name.lower()
            for key, (new_lat, new_lon) in COORDINATE_UPDATES:
                if key in name_lower:
                    if lat != new_lat or lon != new_lon:
                        await session.execute(
                            text("UPDATE institutions SET latitude = :lat, longitude = :lon, updated_at = NOW() WHERE id = :id"),
                            {"lat": new_lat, "lon": new_lon, "id": iid}
                        )
                        logger.info(f"Updated Institution '{name}' (ID: {iid}) from ({lat}, {lon}) to ({new_lat}, {new_lon})")
                        updated_insts_count += 1
                    break

        await session.commit()
        logger.info(f"Database update complete: {updated_places_count} places and {updated_insts_count} institutions updated.")

        # Re-sync document chunks (RAG vectors) for the updated places/institutions
        try:
            logger.info("Syncing updated document chunks for RAG database...")
            from app.services.chunk_indexer import sync_all_document_chunks
            results = await sync_all_document_chunks(session, source_types=["place", "institution"])
            for st, counts in results.items():
                if counts.get("indexed", 0) > 0 or counts.get("unchanged", 0) > 0:
                    logger.info(f"  {st}: indexed={counts['indexed']}, unchanged={counts['unchanged']}")
            await session.commit()
            logger.info("RAG vector sync complete!")
        except Exception as e:
            logger.error(f"Error syncing document chunks: {e}")

if __name__ == "__main__":
    asyncio.run(update_coordinates())
