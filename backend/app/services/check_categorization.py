import asyncio
import re
from sqlalchemy import select
from app.database import async_session
from app.models.places import Place, Institution

def normalize_text(value: str) -> str:
    if not value:
        return ""
    val = value.lower()
    # Basic tr normalization
    replacements = {
        'ı': 'i', 'ğ': 'g', 'ş': 's', 'ç': 'c', 'ö': 'o', 'ü': 'u',
        'İ': 'i', 'Ğ': 'g', 'Ş': 's', 'Ç': 'c', 'Ö': 'o', 'Ü': 'u'
    }
    for k, v in replacements.items():
        val = val.replace(k, v)
    return val

def category_of_place_explore(name, category, subcategory, description, tags):
    text = normalize_text(
        " ".join([
            name or "",
            category or "",
            subcategory or "",
            description or "",
            " ".join(tags or [])
        ])
    )
    if "restoran" in text or "kafe" in text or "cafe" in text or "gastronomi" in text:
        return "food"
    if "sahil" in text or "plaj" in text or "deniz" in text:
        return "coast"
    if "park" in text or "yesil" in text:
        return "park"
    if "antik" in text or "tarih" in text or "aigai" in text or "muze" in text:
        return "history"
    return "culture"

async def main():
    async with async_session() as session:
        places = (await session.execute(select(Place))).scalars().all()
        institutions = (await session.execute(select(Institution))).scalars().all()
        
        print("Checking classification for places with 'hastane' in name:")
        for p in places:
            if "hastane" in p.name.lower():
                cat = category_of_place_explore(p.name, p.category, p.subcategory, p.description, p.tags)
                print(f"  Place ID: {p.id}, Name: {p.name}, DB Cat: {p.category}, Frontend Cat: {cat}")
                # check which word triggered it if it is history
                text = normalize_text(" ".join([p.name or "", p.category or "", p.subcategory or "", p.description or "", " ".join(p.tags or [])]))
                triggers = [word for word in ["antik", "tarih", "aigai", "muze"] if word in text]
                print(f"    Triggers: {triggers}")
                
        print("\nChecking classification for institutions with 'hastane' in name:")
        for p in institutions:
            if "hastane" in p.name.lower():
                # Institutions don't have tags in the same way, but let's see
                cat = category_of_place_explore(p.name, p.category, p.subcategory, p.description, [])
                print(f"  Inst ID: {p.id}, Name: {p.name}, DB Cat: {p.category}, Frontend Cat: {cat}")
                text = normalize_text(" ".join([p.name or "", p.category or "", p.subcategory or "", p.description or ""]))
                triggers = [word for word in ["antik", "tarih", "aigai", "muze"] if word in text]
                print(f"    Triggers: {triggers}")

if __name__ == "__main__":
    asyncio.run(main())
