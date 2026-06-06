import asyncio
from sqlalchemy import text
from app.database import async_session
from loguru import logger

async def clean_outside_data():
    async with async_session() as session:
        # We will delete places outside Aliağa bounding box:
        # Latitude between 38.68 and 38.95, Longitude between 26.90 and 27.22
        # (This is to remove the ~1,000 nodes from Foça, Dikili, Menemen, Çiğli, etc. imported via OSM)
        
        logger.info("Cleaning up places outside Aliağa boundaries from database...")
        
        # Count before deletion
        result_places_count = await session.execute(text("""
            SELECT COUNT(*) FROM places 
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL 
              AND (latitude < 38.68 OR latitude > 38.95 OR longitude < 26.90 OR longitude > 27.22)
        """))
        places_to_delete = result_places_count.scalar()
        
        result_insts_count = await session.execute(text("""
            SELECT COUNT(*) FROM institutions 
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL 
              AND (latitude < 38.68 OR latitude > 38.95 OR longitude < 26.90 OR longitude > 27.22)
        """))
        insts_to_delete = result_insts_count.scalar()
        
        logger.info(f"Found {places_to_delete} places and {insts_to_delete} institutions to delete.")
        
        # Delete places
        if places_to_delete > 0:
            await session.execute(text("""
                DELETE FROM places 
                WHERE latitude IS NOT NULL AND longitude IS NOT NULL 
                  AND (latitude < 38.68 OR latitude > 38.95 OR longitude < 26.90 OR longitude > 27.22)
            """))
            logger.info("Deleted outside places.")
            
        # Delete institutions
        if insts_to_delete > 0:
            await session.execute(text("""
                DELETE FROM institutions 
                WHERE latitude IS NOT NULL AND longitude IS NOT NULL 
                  AND (latitude < 38.68 OR latitude > 38.95 OR longitude < 26.90 OR longitude > 27.22)
            """))
            logger.info("Deleted outside institutions.")
            
        await session.commit()
        
        # Re-sync document chunks (RAG vectors) to remove deleted items from search vector database
        try:
            logger.info("Syncing document chunks for RAG database after deletion...")
            from app.services.chunk_indexer import sync_all_document_chunks
            results = await sync_all_document_chunks(session, source_types=["place", "institution"])
            for st, counts in results.items():
                if counts.get("indexed", 0) > 0 or counts.get("unchanged", 0) > 0 or counts.get("deleted", 0) > 0:
                    logger.info(f"  {st}: indexed={counts.get('indexed', 0)}, unchanged={counts.get('unchanged', 0)}, deleted={counts.get('deleted', 0)}")
            await session.commit()
            logger.info("RAG vector sync complete after cleanup!")
        except Exception as e:
            logger.error(f"Error syncing document chunks after deletion: {e}")
            
if __name__ == "__main__":
    asyncio.run(clean_outside_data())
