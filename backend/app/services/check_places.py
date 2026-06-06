import asyncio
from sqlalchemy import select
from app.database import async_session
from app.models.places import Place, Institution

async def main():
    async with async_session() as session:
        # Check Place counts by category
        places = (await session.execute(select(Place))).scalars().all()
        institutions = (await session.execute(select(Institution))).scalars().all()
        
        print(f"Total Places: {len(places)}")
        print(f"Total Institutions: {len(institutions)}")
        
        # Let's count by category
        place_cats = {}
        for p in places:
            place_cats[p.category] = place_cats.get(p.category, 0) + 1
        print("\nPlace categories:")
        for cat, cnt in sorted(place_cats.items(), key=lambda x: -x[1]):
            print(f"  {cat}: {cnt}")
            
        inst_cats = {}
        for p in institutions:
            inst_cats[p.category] = inst_cats.get(p.category, 0) + 1
        print("\nInstitution categories:")
        for cat, cnt in sorted(inst_cats.items(), key=lambda x: -x[1]):
            print(f"  {cat}: {cnt}")
            
        # Check specifically for hospital / hastane
        print("\nState of 'Devlet Hastanesi':")
        for p in places:
            if "hastane" in p.name.lower() or "devlet" in p.name.lower():
                print(f"  Place ID: {p.id}, Name: {p.name}, Cat: {p.category}, Lat: {p.latitude}, Lon: {p.longitude}, Desc: {p.description}")
        for p in institutions:
            if "hastane" in p.name.lower() or "devlet" in p.name.lower():
                print(f"  Inst ID: {p.id}, Name: {p.name}, Cat: {p.category}, Lat: {p.latitude}, Lon: {p.longitude}, Desc: {p.description}")

        # Check for places with coordinates outside Aliağa (Aliağa bounding box is roughly lat: 38.70 to 38.95, lon: 26.85 to 27.15)
        print("\nPlaces potentially outside Aliağa boundaries (Lat < 38.70 or Lat > 38.95 or Lon < 26.85 or Lon > 27.15):")
        outside_count = 0
        for p in places:
            if p.latitude and p.longitude:
                if not (38.70 <= p.latitude <= 38.98 and 26.85 <= p.longitude <= 27.15):
                    outside_count += 1
                    if outside_count <= 20:
                        print(f"  Place ID: {p.id}, Name: {p.name}, Cat: {p.category}, Lat: {p.latitude}, Lon: {p.longitude}, Address: {p.address}")
        print(f"Total outside places: {outside_count}")

if __name__ == "__main__":
    asyncio.run(main())
