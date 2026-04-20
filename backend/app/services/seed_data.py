"""
AliağaAI — Seed data yükleyici.

Sabit ve nadiren değişen verileri veritabanına yükler:
  - Acil telefonlar
  - Semt pazarları
  - Mekanlar (restoran, kafe, turistik)
  - Kurumlar (kamu, sağlık, eğitim, spor, kültür, kütüphane vb.)
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.city import EmergencyContact, StreetMarket, PostalCode, TaxiStand
from app.models.places import Place, Institution


# ─────────────────────────────────────────────
# ACİL TELEFONLAR
# ─────────────────────────────────────────────
EMERGENCY_CONTACTS = [
    {"name": "Polis İmdat", "phone": "155", "category": "acil", "priority": 1},
    {"name": "Ambulans / Acil Yardım", "phone": "112", "category": "acil", "priority": 0},
    {"name": "İtfaiye", "phone": "110", "category": "acil", "priority": 2},
    {"name": "Jandarma", "phone": "156", "category": "acil", "priority": 3},
    {"name": "İZSU Arıza", "phone": "185", "category": "altyapi", "priority": 10},
    {"name": "GDZ Elektrik Arıza", "phone": "186", "category": "altyapi", "priority": 11},
    {"name": "Cenaze Hizmetleri (Belediye)", "phone": "188", "category": "belediye", "priority": 20},
    {"name": "Aliağa Belediyesi", "phone": "0232 399 00 00", "category": "belediye", "priority": 21},
    {"name": "Aliağa İZSU Şube Müdürlüğü", "phone": "0232 293 79 07", "category": "altyapi", "priority": 12},
    {"name": "Aliağa Devlet Hastanesi", "phone": "0232 616 10 10", "category": "saglik", "priority": 30},
    {"name": "ALO 153 (Belediye Çözüm Merkezi)", "phone": "153", "category": "belediye", "priority": 22},
]

# ─────────────────────────────────────────────
# SEMT PAZARLARI
# ─────────────────────────────────────────────
STREET_MARKETS = [
    {
        "name": "Çarşamba Pazarı",
        "day_of_week": "carsamba",
        "neighborhood": "Yeni Mahalle",
        "address": "Cengiz Topel Caddesi, Yeni Mahalle",
        "description": "Aliağa'nın en büyük semt pazarı. Her çarşamba kurulur.",
    },
    {
        "name": "Yeni Şakran Pazarı",
        "day_of_week": "cuma",
        "neighborhood": "Yeni Şakran",
        "address": "İnönü Caddesi / Atatürk Caddesi",
        "description": "Cuma günleri Yeni Şakran'da kurulan semt pazarı.",
    },
    {
        "name": "Helvacı Pazarı",
        "day_of_week": "cuma",
        "neighborhood": "Helvacı",
        "address": "Mimar Sinan Mahallesi / Fatih Mahallesi",
        "description": "Cuma günleri Helvacı beldesinde kurulan pazar.",
    },
    {
        "name": "Kapalı Pazar (Cumartesi Pazarı)",
        "day_of_week": "cumartesi",
        "neighborhood": "Atatürk Mahallesi",
        "address": "Beyazıt Caddesi No:6, Atatürk Mahallesi",
        "description": "Cumartesi günleri kapalı alanda kurulan pazar.",
    },
]

# ─────────────────────────────────────────────
# MEKANLAR (Restoran, Kafe, Turistik)
# ─────────────────────────────────────────────
PLACES = [
    # Restoranlar
    {
        "name": "Aliağa Balıkevi",
        "category": "restoran",
        "subcategory": "balik",
        "description": "Aliağa'nın en bilinen balık restoranı. Taze deniz ürünleri ve güzel manzarası ile ünlüdür.",
        "tags": ["deniz ürünleri", "balık", "manzaralı"],
    },
    {
        "name": "İzzet Usta Et & Balık",
        "category": "restoran",
        "subcategory": "balik",
        "description": "Et ve balık çeşitleriyle tanınan, Aliağa'nın köklü restoranlarından.",
        "tags": ["et", "balık", "aile dostu"],
    },
    {
        "name": "Deniz'in Mutfağı",
        "category": "restoran",
        "subcategory": "ev_yemekleri",
        "description": "Ev yemekleri ve deniz ürünleri sunan samimi bir mekan.",
        "tags": ["ev yemekleri", "deniz ürünleri", "samimi"],
    },
    {
        "name": "Chef Âlâ Ocakbaşı",
        "category": "restoran",
        "subcategory": "kebap",
        "description": "Ocakbaşı ve ızgara et çeşitleriyle bilinen restoran.",
        "tags": ["ocakbaşı", "ızgara", "kebap"],
    },
    {
        "name": "Pasha Mangalbaşı",
        "category": "restoran",
        "subcategory": "kebap",
        "description": "Mangal ve ızgara çeşitleriyle Aliağa'da sevilen bir mekan.",
        "tags": ["mangal", "ızgara", "aile dostu"],
    },
    {
        "name": "Azim Pide",
        "category": "restoran",
        "subcategory": "pide",
        "description": "Karadeniz pidesi ve lahmacun çeşitleriyle bilinen pide salonu.",
        "tags": ["pide", "lahmacun", "hızlı servis"],
    },
    {
        "name": "Konyalı Mirzaoğlu",
        "category": "restoran",
        "subcategory": "etli_ekmek",
        "description": "Konya mutfağının lezzetlerini sunan, etli ekmek ve fırın kebabı ile ünlü restoran.",
        "tags": ["etli ekmek", "konya mutfağı"],
    },
    # Kafeler
    {
        "name": "Seyir Cafe & Restaurant",
        "category": "kafe",
        "subcategory": "kafe",
        "description": "Deniz manzaralı, sakin bir ortamda kahve ve yemek keyfi sunan kafe-restoran.",
        "tags": ["deniz manzaralı", "sakin", "kahve", "aile dostu"],
    },
    # Turistik Yerler
    {
        "name": "Aigai Antik Kenti",
        "category": "turistik",
        "subcategory": "antik_kent",
        "description": "Aiolis bölgesinin en önemli antik kentlerinden biri. MÖ 7. yüzyıla tarihlenen kalıntıları ile Aliağa'nın en değerli tarihi mekanı.",
        "tags": ["antik kent", "tarih", "arkeoloji", "gezilecek yer"],
    },
    {
        "name": "Kyme Antik Kenti",
        "category": "turistik",
        "subcategory": "antik_kent",
        "description": "Aliağa Namurt Limanı yakınında bulunan, Batı Anadolu'nun en büyük Aiol şehri.",
        "tags": ["antik kent", "tarih", "arkeoloji"],
    },
    {
        "name": "Gryneion Apollon Tapınağı",
        "category": "turistik",
        "subcategory": "antik_kent",
        "description": "Yeni Şakran'da bulunan, Apollon'a adanmış kehanet merkezi ve kutsal alan.",
        "tags": ["antik kent", "tapınak", "apollon", "tarih"],
    },
    {
        "name": "Aliağa Arkeoloji Müzesi",
        "category": "turistik",
        "subcategory": "muze",
        "description": "Bölgede yapılan kazılardan elde edilen eserlerin sergilendiği müze.",
        "tags": ["müze", "arkeoloji", "tarih", "kültür"],
    },
    {
        "name": "Yeni Şakran Sahili",
        "category": "turistik",
        "subcategory": "sahil",
        "description": "Aliağa'nın en popüler plajı. Yaz aylarında yoğun ilgi görür.",
        "tags": ["sahil", "plaj", "deniz", "yüzme"],
    },
    {
        "name": "Sahil Parkı",
        "category": "turistik",
        "subcategory": "park",
        "description": "Aliağa sahil bandı boyunca uzanan yürüyüş ve dinlenme alanı.",
        "tags": ["park", "yürüyüş", "sahil", "piknik"],
    },
]

# ─────────────────────────────────────────────
# KURUMLAR VE TESİSLER
# ─────────────────────────────────────────────
INSTITUTIONS = [
    # Kamu
    {"name": "Aliağa Kaymakamlığı", "category": "kamu", "phone": "0232 616 10 01"},
    {"name": "Aliağa Nüfus Müdürlüğü", "category": "kamu", "phone": "0232 616 46 44"},
    {"name": "Aliağa Tapu Müdürlüğü", "category": "kamu"},
    {"name": "Aliağa Vergi Dairesi", "category": "kamu"},
    {"name": "SGK Aliağa Merkez Müdürlüğü", "category": "kamu"},
    # Sağlık
    {"name": "Aliağa Devlet Hastanesi", "category": "saglik", "phone": "0232 616 10 10", "subcategory": "hastane"},
    # Eğitim
    {"name": "Aliağa Mesleki ve Teknik Anadolu Lisesi", "category": "egitim", "subcategory": "lise"},
    {"name": "Aliağa Anadolu Lisesi", "category": "egitim", "subcategory": "lise"},
    # Kargo
    {"name": "Yurtiçi Kargo Aliağa Şubesi", "category": "kargo"},
    {"name": "Aras Kargo Aliağa Şubesi", "category": "kargo"},
    {"name": "MNG Kargo Aliağa Şubesi", "category": "kargo"},
    {"name": "PTT Aliağa Şubesi", "category": "kargo", "phone": "0232 616 12 22"},
    {"name": "Sürat Kargo Aliağa Şubesi", "category": "kargo"},
    # Noter
    {"name": "Aliağa 1. Noterliği", "category": "noter"},
    {"name": "Aliağa 2. Noterliği", "category": "noter"},
    # Araç Muayene
    {
        "name": "TÜVTÜRK Aliağa Araç Muayene İstasyonu",
        "category": "arac_muayene",
        "address": "Samurlu Mahallesi 1248 Sokak No:4 Yeni Sanayi Sitesi, Aliağa",
        "description": "Randevulu araç muayene hizmeti. Pazartesi – Cumartesi 08:00 – 18:00.",
    },
    # Spor
    {
        "name": "Aliağa Gençlik Merkezi (AGM)",
        "category": "spor",
        "description": "Yarı olimpik havuz, fitness salonu, pilates, spinning, 3 sinema salonu, kafeterya ve çocuk oyun alanı barındıran çok amaçlı gençlik merkezi.",
        "address": "Atatürk Mahallesi, Aliağa",
    },
    {
        "name": "Aliağa Spor ve Yaşam Merkezi",
        "category": "spor",
        "description": "Yarı olimpik havuz, karate, güreş, dans salonları, okçuluk, futbol ve basketbol sahaları, amfitiyatro bulunan spor kompleksi.",
        "address": "Örnekkent Mahallesi, Aliağa",
    },
    # Kültür
    {
        "name": "ASEV (Aliağa Sanat Evi)",
        "category": "kultur",
        "description": "Aliağa Belediyesi'ne bağlı kültür ve sanat merkezi. Sergi, atölye ve etkinliklere ev sahipliği yapar.",
    },
    {
        "name": "Zeytinli Park Açıkhava Etkinlik Alanı",
        "category": "kultur",
        "description": "Konser, tiyatro ve açık hava etkinliklerine ev sahipliği yapan belediye etkinlik alanı.",
    },
    # Kütüphaneler
    {
        "name": "Aliağa Kent Kitaplığı",
        "category": "kutuphane",
        "description": "Aliağa Belediyesi'ne bağlı merkez kütüphane.",
    },
    {
        "name": "Aziz Sancar Kütüphanesi",
        "category": "kutuphane",
        "description": "Spor ve Yaşam Merkezi içinde yer alan kütüphane.",
    },
    {
        "name": "Nadir Nadi Kütüphanesi",
        "category": "kutuphane",
        "description": "Aliağa Gençlik Merkezi (AGM) içinde yer alan kütüphane.",
    },
]

# ─────────────────────────────────────────────
# TAKSİ DURAKLARI
# ─────────────────────────────────────────────
TAXI_STANDS = [
    {
        "name": "Merkez Taksi Durağı",
        "address": "Aliağa ilçe merkezi",
        "is_24h": True,
    },
]

# ─────────────────────────────────────────────
# POSTA KODLARI
# ─────────────────────────────────────────────
POSTAL_CODES = [
    {"neighborhood": "Atatürk Mahallesi", "postal_code": "35800"},
    {"neighborhood": "Cumhuriyet Mahallesi", "postal_code": "35800"},
    {"neighborhood": "Yeni Mahalle", "postal_code": "35800"},
    {"neighborhood": "Kültür Mahallesi", "postal_code": "35800"},
    {"neighborhood": "Güzelhisar Mahallesi", "postal_code": "35800"},
    {"neighborhood": "Yeni Şakran", "postal_code": "35801"},
    {"neighborhood": "Helvacı", "postal_code": "35820"},
    {"neighborhood": "Samurlu", "postal_code": "35800"},
    {"neighborhood": "Çakmaklı", "postal_code": "35800"},
    {"neighborhood": "Bozköy", "postal_code": "35800"},
    {"neighborhood": "Kalabak", "postal_code": "35800"},
    {"neighborhood": "Horozgediği", "postal_code": "35800"},
]


async def _insert_if_empty(session: AsyncSession, model, data_list: list[dict]):
    """Tablo boşsa verileri yükler, doluysa atlar."""
    result = await session.execute(select(model).limit(1))
    if result.scalars().first() is not None:
        return 0  # zaten dolu

    count = 0
    for item in data_list:
        session.add(model(**item))
        count += 1
    await session.flush()
    return count


async def seed_all(session: AsyncSession) -> dict[str, int]:
    """
    Tüm seed verileri yükler. Zaten veri olan tablolara dokunmaz.
    Dönen dict, tablo adı → eklenen satır sayısı eşlemesidir.
    """
    results = {}

    results["emergency_contacts"] = await _insert_if_empty(
        session, EmergencyContact, EMERGENCY_CONTACTS
    )
    results["street_markets"] = await _insert_if_empty(
        session, StreetMarket, STREET_MARKETS
    )
    results["places"] = await _insert_if_empty(session, Place, PLACES)
    results["institutions"] = await _insert_if_empty(
        session, Institution, INSTITUTIONS
    )
    results["taxi_stands"] = await _insert_if_empty(session, TaxiStand, TAXI_STANDS)
    results["postal_codes"] = await _insert_if_empty(session, PostalCode, POSTAL_CODES)

    # RAG İçin Şehir Bilgilerini (Tarihçe vb.) İndir ve Vektörleştir
    try:
        from app.models.city import DocumentChunk
        from loguru import logger
        chunk_check = await session.execute(select(DocumentChunk).where(DocumentChunk.source_type == "city_info").limit(1))
        if chunk_check.scalars().first() is None:
            logger.info("Şehir bilgileri (city_info) RAG veritabanı için yükleniyor...")
            from app.services.scraper_city_info import scrape_and_save_city_info
            from app.services.embedding import generate_embedding
            # Bu işlem sayfa sayısına göre biraz zaman alabilir
            results["city_info_chunks"] = await scrape_and_save_city_info(session, embedding_fn=generate_embedding)
    except Exception as e:
        from loguru import logger
        logger.error(f"Şehir bilgisi RAG verileri yüklenirken hata oluştu: {e}")

    await session.commit()
    return results
