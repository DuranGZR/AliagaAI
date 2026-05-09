import asyncio
from sqlalchemy import select
from app.database import async_session
from app.models.places import Place, Institution

async def show_data():
    async with async_session() as session:
        print("\n--- Yeni Eklenen Eczaneler (OpenStreetMap Verisi) ---")
        institutions = await session.execute(select(Institution).where(Institution.subcategory == 'pharmacy').limit(10))
        for i in institutions.scalars().all():
            print(f"- {i.name} | Adres: {i.address}")
        
        print("\n--- Yeni Eklenen Bankalar (OpenStreetMap Verisi) ---")
        places = await session.execute(select(Place).where(Place.subcategory == 'bank').limit(10))
        for p in places.scalars().all():
            print(f"- {p.name} | Adres: {p.address}")

if __name__ == "__main__":
    asyncio.run(show_data())
