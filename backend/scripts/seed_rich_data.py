"""Seed rich data into new tables + city_knowledge + sync all chunks."""
import asyncio
from datetime import date, time
from sqlalchemy import select, text
from app.database import async_session
from app.models.city import CityKnowledge
from app.models.knowledge_layers import (
    TransportRoute, TransportStop, PoiCatalog,
    MunicipalService, DistrictStat,
)

BATCH = "seed-v2-20260428"
SRC = "https://www.aliaga.bel.tr/"
IZMIR_OPEN = "https://acikveri.bizizmir.com"
VERIFIED = date(2026, 4, 28)

CITY_KNOWLEDGE_DATA = [
    {"layer": "gezi", "title": "Aigai Antik Kenti", "neighborhood": "Yukarı Semt",
     "summary": "Aigai (Nemrutkale), Aliağa'nın en önemli arkeolojik alanlarından biridir. MÖ 7. yüzyıla tarihlenen Aiol kolonisi olup agora, tiyatro ve surları ile dikkat çeker. Aigai, antik dönemde Aiolis bölgesinin önemli şehirlerinden biriydi.",
     "tags": ["antik kent", "tarih", "gezi", "arkeoloji"], "source_url": SRC + "aliaga/antik-kentler"},
    {"layer": "gezi", "title": "Kyme Antik Kenti", "neighborhood": "Namurt",
     "summary": "Kyme, Batı Anadolu'nun en büyük Aiol şehridir. Aliağa Namurt Limanı yakınında bulunan kalıntıları ile MÖ 11. yüzyıla kadar uzanan derin bir tarihe sahiptir. Liman kenti olarak ticaretin merkezi olmuştur.",
     "tags": ["antik kent", "tarih", "arkeoloji", "liman"], "source_url": SRC + "aliaga/antik-kentler"},
    {"layer": "gezi", "title": "Gryneion Apollon Tapınağı", "neighborhood": "Yeni Şakran",
     "summary": "Yeni Şakran'da bulunan Gryneion, Apollon'a adanmış bir kehanet merkezi ve kutsal alandır. Antik çağda önemli bir hac ve kehanet noktasıydı.",
     "tags": ["antik kent", "tapınak", "apollon", "tarih"], "source_url": SRC + "aliaga/antik-kentler"},
    {"layer": "gezi", "title": "Yeni Şakran Sahili", "neighborhood": "Yeni Şakran",
     "summary": "Yeni Şakran sahil bandı, Aliağa'nın en popüler plajıdır. Yaz aylarında yoğun ilgi görür. Yüzme, güneşlenme ve su sporları yapılabilir. Sahil boyunca kafe ve restoranlar bulunur.",
     "tags": ["sahil", "plaj", "gezi", "deniz"], "source_url": SRC + "aliaga/turizm"},
    {"layer": "gezi", "title": "Aliağa Arkeoloji Müzesi", "neighborhood": "Atatürk Mahallesi",
     "summary": "Bölgede yapılan kazılardan elde edilen eserlerin sergilendiği müze. Aigai, Kyme ve Gryneion'dan çıkarılan heykeller, seramikler ve sikkeleri barındırır.",
     "tags": ["müze", "arkeoloji", "tarih", "kültür"], "source_url": SRC + "aliaga/turizm"},
    {"layer": "gezi", "title": "Sahil Parkı ve Yürüyüş Yolu", "neighborhood": "Atatürk Mahallesi",
     "summary": "Aliağa sahil bandı boyunca uzanan 5 km'lik yürüyüş ve bisiklet yolu. Dinlenme alanları, çocuk parkları ve spor aletleri bulunur. Akşamları özellikle popülerdir.",
     "tags": ["park", "yürüyüş", "sahil", "spor"], "source_url": SRC + "aliaga/turizm"},
    {"layer": "ulasim", "title": "İZBAN ile Aliağa'ya Ulaşım",
     "summary": "İZBAN banliyö hattı, Aliağa'yı İzmir merkeze bağlayan temel toplu taşıma aracıdır. Aliağa istasyonu hattın kuzey terminalidir. Çiğli, Hilal, Halkapınar, Bayraklı ve Cumaovası gibi duraklarda İZBAN hizmetleri mevcuttur. Sefer aralıkları hafta içi yaklaşık 10-15 dakika, hafta sonu 20-30 dakikadır. İlk sefer sabah 05:30, son sefer gece 00:00 civarındadır.",
     "tags": ["ulaşım", "izban", "toplu taşıma", "tren", "banliyö"], "source_url": "https://www.izban.com.tr"},
    {"layer": "ulasim", "title": "Aliağa'ya Karayolu Ulaşımı",
     "summary": "Aliağa'ya İzmir'den D550 karayolu veya Kuzey Ege Otoyolu (O-32) üzerinden ulaşılır. İzmir merkeze uzaklık yaklaşık 55 km olup araçla 45-60 dakika sürer. Ankara'dan yaklaşık 580 km, İstanbul'dan ise 560 km mesafededir.",
     "tags": ["ulaşım", "karayolu", "otoyol", "mesafe"], "source_url": SRC + "aliaga/aliaga-ya-nasil-gelinir"},
    {"layer": "ulasim", "title": "Aliağa Feribot Seferleri (Midilli)",
     "summary": "Aliağa Aliaport limanından Yunanistan'ın Midilli (Lesbos) adasına yaz sezonunda feribot seferleri düzenlenmektedir. Sefer süresi yaklaşık 1 saat 30 dakikadır. Turyol ve Jalem Tur gibi firmalar hizmet vermektedir.",
     "tags": ["ulaşım", "feribot", "vapur", "midilli", "deniz"], "source_url": SRC + "aliaga/feribot"},
    {"layer": "ulasim", "title": "Aliağa ESHOT Otobüs Hatları",
     "summary": "Aliağa'ya İzmir merkezden ESHOT 880 ve 885 numaralı otobüs hatları ile ulaşım sağlanabilir. Ayrıca ilçe içi minibüs ve dolmuş hatları Helvacı, Yeni Şakran ve diğer beldelere ulaşım imkanı sunar.",
     "tags": ["ulaşım", "otobüs", "eshot", "toplu taşıma"], "source_url": "https://www.eshot.gov.tr"},
    {"layer": "gastronomi", "title": "Aliağa Gastronomi ve Yeme-İçme",
     "summary": "Aliağa'da deniz ürünleri ön planda yer alır. Balık restoranları, ocakbaşı mekanları, pide salonları ve kafeler bulunur. Öne çıkan mekanlar: Aliağa Balıkevi, İzzet Usta Et & Balık, Seyir Cafe, Azim Pide ve Pasha Mangalbaşı.",
     "tags": ["gastronomi", "yeme içme", "restoran", "balık"], "source_url": SRC + "aliaga/gastronomi"},
    {"layer": "kurumlar", "title": "Aliağa Belediyesi ve Kamu Kurumları",
     "summary": "Aliağa Belediyesi ilçe genelinde belediye hizmetleri sunar. Kaymakamlık, Nüfus Müdürlüğü, Tapu Müdürlüğü, Vergi Dairesi, SGK Müdürlüğü ve noter gibi kamu kurumları mevcuttur. Belediye telefonu: 0232 399 00 00.",
     "tags": ["kurum", "belediye", "kamu"], "source_url": SRC},
    {"layer": "kurumlar", "title": "Aliağa Sağlık ve Eğitim Kurumları",
     "summary": "Aliağa Devlet Hastanesi (Tel: 0232 616 10 10) ilçenin ana sağlık tesisidir. Eğitim kurumları arasında Aliağa Anadolu Lisesi, Mesleki ve Teknik Anadolu Lisesi bulunur. Ayrıca Aliağa Gençlik Merkezi yarı olimpik havuz, fitness ve sinema salonları sunar.",
     "tags": ["sağlık", "eğitim", "hastane", "okul"], "source_url": SRC},
    {"layer": "gezi", "title": "Aliağa Genel Tanıtım ve Coğrafya",
     "summary": "Aliağa, İzmir'in kuzeyinde Ege Denizi kıyısında bir ilçedir. Nüfusu yaklaşık 100.000'dir. Türkiye'nin en büyük petrol rafinerisi (TÜPRAŞ) ve demir-çelik gemi söküm tesisleri burada yer alır. Antik kentleri, sahilleri ve modern sanayi altyapısıyla dikkat çeker.",
     "tags": ["tanıtım", "coğrafya", "genel bilgi", "sanayi"], "source_url": SRC + "aliaga/ilce-tanitimi"},
    {"layer": "gezi", "title": "Aliağa Tarihçesi",
     "summary": "Aliağa tarihi MÖ 3000 yıllarına kadar uzanır. Aiol göçleriyle kurulan Aigai, Kyme ve Gryneion antik kentleri bölgenin en eski yerleşimleridir. Osmanlı döneminde küçük bir köy olan Aliağa, Cumhuriyet sonrası sanayi yatırımlarıyla hızla büyümüştür. 1867 tarihli belgelerle resmi kayıtlara geçmiştir.",
     "tags": ["tarih", "tarihçe", "antik", "osmanlı"], "source_url": SRC + "aliaga/tarihce"},
    {"layer": "kurumlar", "title": "Aliağa Spor ve Kültür Tesisleri",
     "summary": "Aliağa Gençlik Merkezi (AGM): yarı olimpik havuz, fitness, pilates, spinning, 3 sinema salonu, kafeterya. Aliağa Spor ve Yaşam Merkezi: yarı olimpik havuz, karate, güreş, dans, okçuluk, futbol ve basketbol sahaları. ASEV (Aliağa Sanat Evi): sergi, atölye, kültürel etkinlikler.",
     "tags": ["spor", "kültür", "havuz", "sinema"], "source_url": SRC + "aliaga/spor-tesisleri"},
    {"layer": "ulasim", "title": "Aliağa İçi Ulaşım ve Mahalleler",
     "summary": "Aliağa merkez mahalleleri: Atatürk, Cumhuriyet, Yeni, Kültür, Güzelhisar ve Örnekent. Beldeler: Yeni Şakran, Helvacı, Samurlu, Çakmaklı, Bozköy, Kalabak ve Horozgediği. Mahalleler arası dolmuş ve minibüs hatları mevcuttur.",
     "tags": ["mahalle", "ilçe", "ulaşım", "coğrafya"], "source_url": SRC + "aliaga/mahalleler"},
]

TRANSPORT_ROUTES_DATA = [
    {"mode": "izban", "hat_no": "Aliağa-Cumaovası", "guzergah": "Aliağa → Menemen → Çiğli → Karşıyaka → Hilal → Halkapınar → Şirinyer → Gaziemir → Cumaovası. İZBAN banliyö tren hattı İzmir toplu taşıma.", "source_url": "https://www.izban.com.tr", "quality_score": 0.9, "ingestion_batch_id": BATCH},
    {"mode": "eshot", "hat_no": "880", "guzergah": "Aliağa Merkez → Menemen → Bornova → İzmir Merkez. ESHOT belediye otobüsü.", "source_url": "https://www.eshot.gov.tr", "quality_score": 0.8, "ingestion_batch_id": BATCH},
    {"mode": "eshot", "hat_no": "885", "guzergah": "Aliağa → Çandarlı → Dikili yönü ESHOT belediye otobüsü.", "source_url": "https://www.eshot.gov.tr", "quality_score": 0.8, "ingestion_batch_id": BATCH},
    {"mode": "vapur", "hat_no": "Aliağa-Midilli", "guzergah": "Aliaport Limanı → Midilli (Mytilene) Limanı. Yaz sezonu feribot seferi yaklaşık 1.5 saat.", "source_url": SRC + "aliaga/feribot", "quality_score": 0.8, "ingestion_batch_id": BATCH},
]

TRANSPORT_STOPS_DATA = [
    {"stop_id": "IZB-ALIAGA", "ad": "Aliağa İstasyonu", "ilce": "Aliağa", "mahalle": "Atatürk", "mode": "izban", "source_url": "https://www.izban.com.tr", "quality_score": 0.9, "ingestion_batch_id": BATCH},
    {"stop_id": "IZB-MENEMEN", "ad": "Menemen İstasyonu", "ilce": "Menemen", "mode": "izban", "source_url": "https://www.izban.com.tr", "quality_score": 0.9, "ingestion_batch_id": BATCH},
    {"stop_id": "IZB-CIGLI", "ad": "Çiğli İstasyonu", "ilce": "Çiğli", "mode": "izban", "source_url": "https://www.izban.com.tr", "quality_score": 0.9, "ingestion_batch_id": BATCH},
    {"stop_id": "IZB-KARSIYAKA", "ad": "Karşıyaka İstasyonu", "ilce": "Karşıyaka", "mode": "izban", "source_url": "https://www.izban.com.tr", "quality_score": 0.9, "ingestion_batch_id": BATCH},
    {"stop_id": "IZB-HILAL", "ad": "Hilal İstasyonu", "ilce": "Konak", "mode": "izban", "source_url": "https://www.izban.com.tr", "quality_score": 0.9, "ingestion_batch_id": BATCH},
    {"stop_id": "IZB-HALKAPINAR", "ad": "Halkapınar İstasyonu", "ilce": "Konak", "mode": "izban", "source_url": "https://www.izban.com.tr", "quality_score": 0.9, "ingestion_batch_id": BATCH},
    {"stop_id": "IZB-BAYRAKLI", "ad": "Bayraklı İstasyonu", "ilce": "Bayraklı", "mode": "izban", "source_url": "https://www.izban.com.tr", "quality_score": 0.9, "ingestion_batch_id": BATCH},
    {"stop_id": "FRY-ALIAPORT", "ad": "Aliaport Feribot İskelesi", "ilce": "Aliağa", "mahalle": "Atatürk", "mode": "vapur", "source_url": SRC, "quality_score": 0.8, "ingestion_batch_id": BATCH},
]

POI_DATA = [
    {"kategori": "Antik Kent", "ad": "Aigai Antik Kenti", "aciklama": "MÖ 7. yüzyıla tarihlenen Aiol antik kenti. Agora, tiyatro kalıntıları.", "mahalle": "Yukarı Semt", "source_url": SRC, "quality_score": 0.9, "ingestion_batch_id": BATCH},
    {"kategori": "Antik Kent", "ad": "Kyme Antik Kenti", "aciklama": "Batı Anadolu'nun en büyük Aiol şehri. Namurt Limanı yakınında.", "mahalle": "Namurt", "source_url": SRC, "quality_score": 0.9, "ingestion_batch_id": BATCH},
    {"kategori": "Antik Kent", "ad": "Gryneion Apollon Tapınağı", "aciklama": "Apollon'a adanmış kehanet merkezi ve kutsal alan.", "mahalle": "Yeni Şakran", "source_url": SRC, "quality_score": 0.9, "ingestion_batch_id": BATCH},
    {"kategori": "Müze", "ad": "Aliağa Arkeoloji Müzesi", "aciklama": "Kazılardan elde edilen eserlerin sergilendiği müze.", "mahalle": "Atatürk", "source_url": SRC, "quality_score": 0.85, "ingestion_batch_id": BATCH},
    {"kategori": "Sahil", "ad": "Yeni Şakran Sahili", "aciklama": "Aliağa'nın en popüler plajı. Yaz aylarında yoğun.", "mahalle": "Yeni Şakran", "source_url": SRC, "quality_score": 0.85, "ingestion_batch_id": BATCH},
    {"kategori": "Park", "ad": "Sahil Parkı", "aciklama": "5 km sahil bandı yürüyüş ve bisiklet yolu.", "mahalle": "Atatürk", "source_url": SRC, "quality_score": 0.85, "ingestion_batch_id": BATCH},
    {"kategori": "Spor", "ad": "Aliağa Gençlik Merkezi", "aciklama": "Yarı olimpik havuz, fitness, sinema, kafeterya.", "mahalle": "Atatürk", "source_url": SRC, "quality_score": 0.85, "ingestion_batch_id": BATCH},
    {"kategori": "Spor", "ad": "Spor ve Yaşam Merkezi", "aciklama": "Havuz, karate, güreş, okçuluk, futbol ve basketbol.", "mahalle": "Örnekent", "source_url": SRC, "quality_score": 0.85, "ingestion_batch_id": BATCH},
    {"kategori": "Kültür", "ad": "ASEV Aliağa Sanat Evi", "aciklama": "Sergi, atölye ve kültürel etkinliklere ev sahipliği.", "source_url": SRC, "quality_score": 0.8, "ingestion_batch_id": BATCH},
    {"kategori": "Kültür", "ad": "Zeytinli Park Açıkhava Alanı", "aciklama": "Konser, tiyatro ve açık hava etkinlikleri.", "source_url": SRC, "quality_score": 0.8, "ingestion_batch_id": BATCH},
]

MUNICIPAL_DATA = [
    {"hizmet_tipi": "Belediye Hizmetleri", "birim": "Aliağa Belediyesi", "calisma_saatleri": "08:30-17:30", "iletisim": "0232 399 00 00", "source_url": SRC, "quality_score": 0.9, "ingestion_batch_id": BATCH},
    {"hizmet_tipi": "Çözüm Merkezi", "birim": "ALO 153", "calisma_saatleri": "7/24", "iletisim": "153", "source_url": SRC, "quality_score": 0.9, "ingestion_batch_id": BATCH},
    {"hizmet_tipi": "Su İdaresi", "birim": "İZSU Aliağa Şube", "calisma_saatleri": "08:00-17:00", "iletisim": "0232 293 79 07", "source_url": "https://www.izsu.gov.tr", "quality_score": 0.85, "ingestion_batch_id": BATCH},
    {"hizmet_tipi": "Elektrik Arıza", "birim": "GDZ Elektrik", "calisma_saatleri": "7/24", "iletisim": "186", "source_url": "https://www.gdzelektrik.com.tr", "quality_score": 0.85, "ingestion_batch_id": BATCH},
    {"hizmet_tipi": "Cenaze Hizmetleri", "birim": "Belediye Cenaze", "calisma_saatleri": "7/24", "iletisim": "188", "source_url": SRC, "quality_score": 0.8, "ingestion_batch_id": BATCH},
]

DISTRICT_DATA = [
    {"yil": 2024, "metrik_adi": "Nüfus", "metrik_degeri": 100000, "birim": "kişi", "district": "Aliağa", "source_url": "https://www.tuik.gov.tr", "quality_score": 0.9, "ingestion_batch_id": BATCH},
    {"yil": 2024, "metrik_adi": "Yüzölçümü", "metrik_degeri": 301, "birim": "km²", "district": "Aliağa", "source_url": SRC, "quality_score": 0.9, "ingestion_batch_id": BATCH},
    {"yil": 2024, "metrik_adi": "Rakım", "metrik_degeri": 5, "birim": "metre", "district": "Aliağa", "source_url": SRC, "quality_score": 0.9, "ingestion_batch_id": BATCH},
    {"yil": 2024, "metrik_adi": "Mahalle Sayısı", "metrik_degeri": 24, "birim": "adet", "district": "Aliağa", "source_url": SRC, "quality_score": 0.85, "ingestion_batch_id": BATCH},
]

async def _insert_if_empty(session, model, data, verified=VERIFIED):
    result = await session.execute(select(model).limit(1))
    if result.scalars().first() is not None:
        print(f"  {model.__tablename__}: already has data, skipping")
        return 0
    count = 0
    for item in data:
        if "last_verified_at" not in item:
            item["last_verified_at"] = verified
        session.add(model(**item))
        count += 1
    await session.flush()
    print(f"  {model.__tablename__}: inserted {count} rows")
    return count

async def _sync_city_knowledge(session, data):
    existing = (await session.execute(select(CityKnowledge))).scalars().all()
    existing_map = {((r.layer or "").lower(), (r.title or "").lower()): r for r in existing}
    seen = set()
    changes = 0
    for item in data:
        item.setdefault("last_verified_at", VERIFIED)
        key = ((item.get("layer") or "").lower(), (item.get("title") or "").lower())
        seen.add(key)
        ex = existing_map.get(key)
        if ex is None:
            session.add(CityKnowledge(**item))
            changes += 1
        else:
            for f in ("neighborhood", "summary", "tags", "source_url", "last_verified_at"):
                if getattr(ex, f) != item.get(f):
                    setattr(ex, f, item.get(f))
                    changes += 1
    for key, stale in existing_map.items():
        if key not in seen:
            await session.delete(stale)
            changes += 1
    await session.flush()
    print(f"  city_knowledge: {changes} changes")
    return changes

async def main():
    async with async_session() as session:
        print("=== Seeding rich data ===")
        await _sync_city_knowledge(session, CITY_KNOWLEDGE_DATA)
        await _insert_if_empty(session, TransportRoute, TRANSPORT_ROUTES_DATA)
        await _insert_if_empty(session, TransportStop, TRANSPORT_STOPS_DATA)
        await _insert_if_empty(session, PoiCatalog, POI_DATA)
        await _insert_if_empty(session, MunicipalService, MUNICIPAL_DATA)
        await _insert_if_empty(session, DistrictStat, DISTRICT_DATA)
        await session.commit()
        print("\n=== Syncing document chunks ===")

        from app.services.chunk_indexer import sync_all_document_chunks
        results = await sync_all_document_chunks(session, source_types=[
            "city_knowledge", "transport_route", "transport_stop",
            "poi_catalog", "municipal_service", "district_stat",
            "izban_schedule", "ferry_schedule",
            "place", "institution", "news", "project",
        ])
        for st, counts in results.items():
            if counts.get("indexed", 0) > 0 or counts.get("unchanged", 0) > 0:
                print(f"  {st}: indexed={counts['indexed']}, unchanged={counts['unchanged']}")
        await session.commit()

        # Final count
        result = await session.execute(text(
            "SELECT source_type, COUNT(*) FROM document_chunks GROUP BY source_type ORDER BY COUNT(*) DESC"
        ))
        print("\n=== FINAL CHUNK COUNTS ===")
        total = 0
        for row in result:
            print(f"  {row[0]}: {row[1]}")
            total += row[1]
        print(f"  TOTAL: {total}")

asyncio.run(main())
