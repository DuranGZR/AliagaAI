"""Enrich places with AI-generated descriptions and tags."""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import select
from loguru import logger

from app.database import async_session, init_db, close_db
from app.models.places import Place
from app.services.llm import get_json_response
from app.services.chunk_indexer import sync_all_document_chunks


def is_low_quality_description(val: str | None) -> bool:
    if not val:
        return True
    val = val.lower()
    val = val.translate(str.maketrans("çğıöşü", "cgiosu"))
    markers = [
        "osm kaynak",
        "kategori:",
        "alt kategori:",
        "calisma saatleri:",
        "sehir rehberinde",
        "ilce rehberinde",
        "kayitli noktadir",
        "kayitli gercek bir noktadir",
        "kayitli kurum bilgisidir",
        "kesif noktasi",
        "resmi/acik veri",
        "saha rehberi",
    ]
    return len(val) < 75 or any(m in val for m in markers)


async def enrich_single_place(place: Place, semaphore: asyncio.Semaphore) -> bool:
    async with semaphore:
        prompt = (
            f"Mekan Adı: {place.name}\n"
            f"Kategori: {place.category or 'Bilinmiyor'}\n"
            f"Alt Kategori: {place.subcategory or 'Bilinmiyor'}\n"
            f"Adres: {place.address or 'Aliağa / İzmir'}"
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "Sen Aliağa şehir rehberinin profesyonel editörüsün. Görevin, sana verilen mekan "
                    "bilgilerine dayanarak, o mekana özel, gerçekçi, sıcak, davetkar ve 1-2 cümlelik "
                    "(en fazla 160 karakter) Türkçe bir tanıtım açıklaması ve mekanı tanımlayan 3-5 adet "
                    "Türkçe arama etiketi üretmektir. Üretilen açıklama asla genelgeçer/jenerik olmamalı, "
                    "mekanın ismiyle doğrudan bağlantılı olmalıdır.\n\n"
                    "Çıktıyı kesinlikle şu JSON formatında vermelisin:\n"
                    "{\n"
                    "  \"description\": \"tanıtım açıklaması\",\n"
                    "  \"tags\": [\"etiket1\", \"etiket2\", \"etiket3\"]\n"
                    "}"
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        try:
            # 0.3 sıcaklık ile daha yaratıcı ama tutarlı yanıtlar alalım
            data = await get_json_response(messages, temperature=0.3, max_tokens=256)
            desc = data.get("description")
            tags = data.get("tags")

            if desc and isinstance(desc, str) and tags and isinstance(tags, list):
                place.description = desc.strip()
                # Uniq ve temiz etiketler
                place.tags = list(set([str(t).strip().lower() for t in tags if str(t).strip()]))
                logger.info(f"✔ Başarıyla zenginleştirildi: {place.name} -> {place.description[:50]}...")
                return True
        except Exception as exc:
            logger.error(f"❌ {place.name} zenginleştirilirken LLM hatası: {exc}")
        return False


async def main() -> None:
    logger.info("Mekan zenginleştirme süreci başlatılıyor...")
    await init_db()

    categories_to_enrich = ["restoran", "kafe", "turistik", "park", "spor_park", "kultur", "plaj", "sahil"]
    semaphore = asyncio.Semaphore(5)  # Eşzamanlı istek sınırlandırıcı (Rate Limit koruması)

    async with async_session() as session:
        # Koordinatı olan ve açıklaması olmayan/düşük kaliteli olan mekanları çek
        stmt = select(Place).where(
            Place.is_active == True,
            Place.category.in_(categories_to_enrich),
            Place.latitude.isnot(None),
            Place.longitude.isnot(None)
        )
        result = await session.execute(stmt)
        all_places = result.scalars().all()

        places_to_enrich = [p for p in all_places if is_low_quality_description(p.description)]
        logger.info(f"Toplam koordinatlı mekan sayısı: {len(all_places)}")
        logger.info(f"Zenginleştirilecek düşük kaliteli/boş mekan sayısı: {len(places_to_enrich)}")

        if not places_to_enrich:
            logger.info("Zenginleştirilecek mekan bulunamadı. Süreç sonlandırılıyor.")
            await close_db()
            return

        # Sadece ilk 150 tanesini bu turda işleyelim (API limitlerini aşmamak için)
        batch = places_to_enrich[:150]
        logger.info(f"Bu turda {len(batch)} mekan işlenecek.")

        tasks = [enrich_single_place(p, semaphore) for p in batch]
        results = await asyncio.gather(*tasks)

        enriched_count = sum(1 for r in results if r)
        logger.info(f"{enriched_count} adet mekan başarıyla güncellendi.")

        if enriched_count > 0:
            await session.commit()
            logger.info("Değişiklikler veritabanına kaydedildi.")
            
            logger.info("RAG Chunks senkronize ediliyor...")
            await sync_all_document_chunks(session, source_types=["place"])
            logger.info("RAG Chunks senkronizasyonu tamamlandı.")
        else:
            await session.rollback()
            logger.info("Hiçbir değişiklik yapılmadı.")

    await close_db()
    logger.info("Zenginleştirme süreci tamamlandı.")


if __name__ == "__main__":
    asyncio.run(main())
