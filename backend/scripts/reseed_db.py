import asyncio
import os
import sys

from sqlalchemy import text
from app.database import async_session
from app.services.seed_data import seed_all
from app.services.chunk_indexer import sync_all_document_chunks

async def reseed_database():
    async with async_session() as session:
        print("Tablolar temizleniyor...")
        await session.execute(text("TRUNCATE TABLE places, institutions, street_markets, emergency_contacts, taxi_stands, postal_codes RESTART IDENTITY CASCADE"))
        await session.commit()
        
        print("Devasa veri seti yükleniyor...")
        results = await seed_all(session)
        print("Yükleme sonuçları:", results)
        
        print("RAG Vektörleri güncelleniyor...")
        chunk_sync = await sync_all_document_chunks(
            session,
            source_types=[
                "news", "event", "announcement", "project", "job",
                "place", "institution", "outage", "obituary",
                "city_knowledge", "transport_route", "transport_stop",
                "poi_catalog", "municipal_service", "district_stat",
                "izban_schedule", "ferry_schedule",
            ],
        )
        print("Chunk senkronizasyon tamamlandı.")
        
if __name__ == "__main__":
    asyncio.run(reseed_database())
