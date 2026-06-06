from __future__ import annotations

import hashlib
import unicodedata
from datetime import date, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cache import EarthquakesCache, WeatherCache
from app.models.city import EmergencyContact, IzbanSchedule, PostalCode, TaxiStand
from app.models.content import Announcement, Event, JobListing, News, Project
from app.models.knowledge_layers import MunicipalService, PoiCatalog
from app.models.places import Institution, Place, ServiceProvider
from app.services.seed_data_massive import INSTITUTIONS, PLACES, POSTAL_CODES


PLACE_IMAGES = {
    "restoran": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1200&q=80",
    "kafe": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=1200&q=80",
    "turistik": "https://images.unsplash.com/photo-1530841377377-3ff06c0ca713?auto=format&fit=crop&w=1200&q=80",
    "park": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1200&q=80",
    "plaj": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
    "sahil": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
    "kurum": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=80",
    "kamu": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=80",
    "saglik": "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1200&q=80",
    "sağlık": "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1200&q=80",
    "egitim": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=1200&q=80",
    "eğitim": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=1200&q=80",
    "kultur": "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?auto=format&fit=crop&w=1200&q=80",
    "kültür": "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?auto=format&fit=crop&w=1200&q=80",
}

INSTITUTION_IMAGES = {
    "kamu": PLACE_IMAGES["kamu"],
    "saglik": PLACE_IMAGES["saglik"],
    "sağlık": PLACE_IMAGES["sağlık"],
    "egitim": PLACE_IMAGES["egitim"],
    "eğitim": PLACE_IMAGES["eğitim"],
    "banka": "https://images.unsplash.com/photo-1565373679107-344d38dbf734?auto=format&fit=crop&w=1200&q=80",
    "atm": "https://images.unsplash.com/photo-1565373679107-344d38dbf734?auto=format&fit=crop&w=1200&q=80",
    "kargo": "https://images.unsplash.com/photo-1566576912321-d58ddd7a6088?auto=format&fit=crop&w=1200&q=80",
    "noter": "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?auto=format&fit=crop&w=1200&q=80",
    "spor": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=1200&q=80",
    "kultur": PLACE_IMAGES["kultur"],
    "kültür": PLACE_IMAGES["kültür"],
    "kutuphane": "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=1200&q=80",
    "kütüphane": "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=1200&q=80",
    "otopark": "https://images.unsplash.com/photo-1506521781263-d8422e82f27a?auto=format&fit=crop&w=1200&q=80",
}

CONTENT_IMAGES = {
    "news": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=1200&q=80",
    "event": "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?auto=format&fit=crop&w=1200&q=80",
    "project": "https://images.unsplash.com/photo-1494526585095-c41746248156?auto=format&fit=crop&w=1200&q=80",
    "project_infra": "https://images.unsplash.com/photo-1541888946425-d81bb19240f5?auto=format&fit=crop&w=1200&q=80",
    "project_green": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1200&q=80",
}

LEGACY_GENERIC_IMAGES = set(PLACE_IMAGES.values()) | set(INSTITUTION_IMAGES.values()) | set(CONTENT_IMAGES.values())

IMAGE_POOLS = {
    "food": [
        "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1551218808-94e220e084d2?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=1200&q=80",
    ],
    "cafe": [
        "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1442512595331-e89e73853f31?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1511920170033-f8396924c348?auto=format&fit=crop&w=1200&q=80",
    ],
    "history": [
        "https://images.unsplash.com/photo-1530841377377-3ff06c0ca713?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1603565816030-6b389eeb23cb?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1575505586569-646b2ca898fc?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1596414086775-3e321ab08f36?auto=format&fit=crop&w=1200&q=80",
    ],
    "coast": [
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80",
    ],
    "park": [
        "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80",
    ],
    "culture": [
        "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1524230572899-a752b3835840?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1517457373958-b7bdd4587205?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1505236858219-8359eb29e329?auto=format&fit=crop&w=1200&q=80",
    ],
    "shopping": [
        "https://images.unsplash.com/photo-1519677100203-a0e668c92439?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1601598851547-4302969d0614?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&w=1200&q=80",
    ],
    "service": [
        "https://images.unsplash.com/photo-1504917595217-d4dc5ebe6122?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1517048676732-d65bc937f952?auto=format&fit=crop&w=1200&q=80",
    ],
    "institution": [
        "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1497366811353-6870744d04b2?auto=format&fit=crop&w=1200&q=80",
    ],
    "health": [
        "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1586773860418-d37222d8fce3?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1587351021759-3e566b6af7cc?auto=format&fit=crop&w=1200&q=80",
    ],
    "education": [
        "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=1200&q=80",
    ],
    "transport": [
        "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1494515843206-f3117d3f51b7?auto=format&fit=crop&w=1200&q=80",
    ],
}

CATEGORY_LABELS = {
    "restoran": "yeme içme",
    "kafe": "kafe",
    "turistik": "turizm",
    "park": "park ve yeşil alan",
    "plaj": "sahil",
    "sahil": "sahil",
    "kamu": "kamu kurumu",
    "saglik": "sağlık",
    "sağlık": "sağlık",
    "egitim": "eğitim",
    "eğitim": "eğitim",
    "kargo": "kargo",
    "noter": "noter",
    "banka": "banka",
    "atm": "ATM",
    "otopark": "otopark",
    "tesisatci": "tesisat",
    "tesisatçı": "tesisat",
    "elektrikci": "elektrik",
    "elektrikçi": "elektrik",
    "cilingir": "çilingir",
    "çilingir": "çilingir",
    "taksi": "taksi",
    "veteriner": "veteriner",
    "temizlik": "temizlik",
    "nakliyat": "nakliyat",
}

TAXI_PHONE_SUPPLEMENTS = {
    "aliaga taksi duragi": "0232 616 19 03",
    "aliağa taksi durağı": "0232 616 19 03",
    "cetin taksi duragi": "0232 616 10 97",
    "çetin taksi durağı": "0232 616 10 97",
    "cicek taksi duragi": "0232 616 23 86",
    "çiçek taksi durağı": "0232 616 23 86",
    "dogan taksi duragi": "0232 616 30 59",
    "doğan taksi durağı": "0232 616 30 59",
    "guven taksi": "0232 616 10 63",
    "güven taksi": "0232 616 10 63",
    "huzur taksi duragi": "0232 616 21 11",
    "huzur taksi durağı": "0232 616 21 11",
    "merkez taksi suayip balci duragi": "0537 234 68 01",
    "merkez taksi şuayip balcı durağı": "0537 234 68 01",
    "merkez taksi duragi": "0232 616 19 03",
    "merkez taksi durağı": "0232 616 19 03",
    "park taksi duragi": "0232 616 89 88",
    "park taksi durağı": "0232 616 89 88",
    "yenisakran taksi duragi": "0536 616 29 53",
    "yenişakran taksi durağı": "0536 616 29 53",
    "yildiz taksi": "0232 616 15 20",
    "yıldız taksi": "0232 616 15 20",
}

PLACE_SUPPLEMENTS: dict[str, dict[str, Any]] = {
    "Aliağa Balıkevi": {"address": "Aliağa sahil bandı, Aliağa / İzmir"},
    "İzzet Usta Et & Balık": {"address": "Aliağa merkez, Aliağa / İzmir"},
    "Deniz'in Mutfağı": {"address": "Aliağa merkez, Aliağa / İzmir"},
    "Chef Âlâ Ocakbaşı": {"address": "Aliağa merkez, Aliağa / İzmir"},
    "Pasha Mangalbaşı": {"address": "Aliağa merkez, Aliağa / İzmir"},
    "Azim Pide": {"address": "Aliağa merkez, Aliağa / İzmir"},
    "Konyalı Mirzaoğlu": {"address": "Aliağa merkez, Aliağa / İzmir"},
    "Seyir Cafe & Restaurant": {"address": "Aliağa sahil bandı, Aliağa / İzmir"},
    "Aigai Antik Kenti": {
        "address": "Yunt Dağı, Köseler çevresi",
        "website": "https://www.aliaga.bel.tr/assets/upload/dokuman/aigai_rehber_kitabi_2021.pdf",
    },
    "Kyme Antik Kenti": {
        "address": "Çakmaklı Mahallesi yakınları, 35800 Aliağa / İzmir",
        "website": "https://www.aliaga.bel.tr/aliaga/antik-kentler/kyme-antik-kenti",
    },
    "Gryneion Apollon Tapınağı": {
        "address": "Yeni Şakran sahil yolu, Aliağa / İzmir",
        "website": "https://www.aliaga.bel.tr/aliaga/antik-kentler",
    },
    "Aliağa Arkeoloji Müzesi": {
        "address": "Kyme kazıevi ve müze alanı, Aliağa / İzmir",
        "description": "Kyme kazılarıyla ilişkili arkeoloji müzesi ve kazıevi alanı. Erişim ve ziyaret durumu dönemsel olarak değişebilir; gitmeden önce resmi kaynak kontrol edilmelidir.",
    },
    "Yeni Şakran Sahili": {"address": "Yeni Şakran sahil bandı, Aliağa / İzmir"},
    "Sahil Parkı": {"address": "Aliağa merkez sahil bandı, Aliağa / İzmir"},
    "Ağapark Plajı ve Sosyal Tesisleri": {
        "address": "Aliağa arka plajlar mevkii, Aliağa / İzmir",
        "website": "https://www.aliaga.bel.tr/projelerimiz/tamamlanan-projeler/agapark-plaj-tesisleri-projesi",
    },
}

INSTITUTION_SUPPLEMENTS: dict[str, dict[str, Any]] = {
    "Aliağa Kaymakamlığı": {
        "address": "Kültür Mahallesi, Hükümet Konağı, Aliağa / İzmir",
        "phone": "0232 616 10 01",
        "description": "Aliağa ilçesinin mülki idare amirliği ve resmi kamu hizmetleri koordinasyon noktası.",
    },
    "Aliağa Nüfus Müdürlüğü": {
        "address": "Kültür Mahallesi, Hükümet Konağı, Aliağa / İzmir",
        "phone": "0232 616 46 44",
        "description": "Kimlik, pasaport, sürücü belgesi ve nüfus kayıt işlemleri için ilçe nüfus müdürlüğü.",
    },
    "Aliağa Tapu Müdürlüğü": {
        "address": "Kültür Mahallesi, Hükümet Konağı çevresi, Aliağa / İzmir",
        "description": "Taşınmaz tapu, tescil ve resmi kayıt işlemleri için ilçe tapu birimi.",
    },
    "Aliağa Vergi Dairesi": {
        "address": "Yeni Mahalle, İstiklal Caddesi No:85, Aliağa / İzmir",
        "phone": "0232 616 14 05",
        "description": "Vergi tahakkuk, tahsilat, sicil ve mükellef işlemlerini yürüten resmi kurum.",
    },
    "SGK Aliağa Merkez Müdürlüğü": {
        "address": "Aliağa merkez, Aliağa / İzmir",
        "description": "Sosyal güvenlik, sigorta ve emeklilik işlemleri için SGK hizmet noktası.",
    },
    "Aliağa Devlet Hastanesi": {
        "address": "Yeni Mahalle, Rumeli Caddesi No:2, Aliağa / İzmir",
        "phone": "0232 616 10 10",
        "description": "Aliağa'nın ana kamu hastanesi. Acil servis ve poliklinik hizmetleri verir.",
    },
    "Aliağa Mesleki ve Teknik Anadolu Lisesi": {
        "address": "Yeni Mahalle, Lise Caddesi, Aliağa / İzmir",
        "phone": "0232 616 12 50",
        "description": "Sanayi ve teknik alanlara yönelik mesleki eğitim veren köklü lise.",
    },
    "Aliağa Anadolu Lisesi": {
        "address": "Siteler Mahallesi, Aliağa / İzmir",
        "description": "Aliağa merkezde ortaöğretim hizmeti veren Anadolu lisesi.",
    },
    "PTT Aliağa Şubesi": {
        "address": "Kültür Mahallesi, Hükümet Caddesi, Aliağa / İzmir",
        "phone": "0232 616 12 22",
        "description": "Posta, kargo, tebligat ve PTT finans işlemleri için merkez şube.",
    },
    "Aliağa 1. Noterliği": {
        "address": "Aliağa merkez, Aliağa / İzmir",
        "description": "Vekaletname, onay, satış ve noterlik işlemleri için resmi noterlik.",
    },
    "Aliağa 2. Noterliği": {
        "address": "Aliağa merkez, Aliağa / İzmir",
        "description": "Vekaletname, onay, satış ve noterlik işlemleri için resmi noterlik.",
    },
    "ASEV (Aliağa Sanat Evi)": {
        "address": "Kültür Mahallesi, Aliağa / İzmir",
        "description": "Aliağa Belediyesi sanat, kültür, kurs ve etkinlik merkezi.",
    },
    "Zeytinli Park Açıkhava Etkinlik Alanı": {
        "address": "Atatürk Mahallesi, sahil bandı, Aliağa / İzmir",
        "description": "Konser, tiyatro ve açık hava belediye etkinliklerinin düzenlendiği alan.",
    },
    "Aliağa Kent Kitaplığı": {
        "address": "Aliağa merkez, Aliağa / İzmir",
        "description": "Aliağa Belediyesi kent belleği, yayınları ve okuma kaynakları için merkez kitaplık.",
    },
}

ADDITIONAL_INSTITUTIONS: list[dict[str, Any]] = [
    {
        "name": "Garanti BBVA Aliağa Şubesi",
        "category": "banka",
        "subcategory": "sube",
        "address": "Aliağa merkez, Aliağa / İzmir",
        "phone": "0232 616 30 05",
        "description": "Aliağa merkezde bankacılık, ATM ve şube işlemleri için Garanti BBVA hizmet noktası.",
        "image_url": INSTITUTION_IMAGES["banka"],
    },
    {
        "name": "Yapı Kredi Aliağa Şubesi",
        "category": "banka",
        "subcategory": "sube",
        "address": "Merkez İstiklal Caddesi, Aliağa / İzmir",
        "phone": "0232 616 20 40",
        "description": "Aliağa merkezde bireysel ve ticari bankacılık işlemleri için Yapı Kredi şube kaydı.",
        "image_url": INSTITUTION_IMAGES["banka"],
    },
    {
        "name": "Anadolubank Aliağa Şubesi",
        "category": "banka",
        "subcategory": "sube",
        "address": "Kazım Dirik / Kültür, İstiklal Caddesi, Aliağa / İzmir",
        "phone": "0232 617 15 55",
        "description": "Aliağa merkezde bankacılık işlemleri için Anadolubank şube kaydı.",
        "image_url": INSTITUTION_IMAGES["banka"],
    },
    {
        "name": "VakıfBank Aliağa Hizmet Noktası",
        "category": "banka",
        "subcategory": "sube",
        "address": "Aliağa / İzmir",
        "phone": "0232 616 17 10",
        "description": "Aliağa ilçe sınırında VakıfBank bankacılık işlemleri için kayıtlı hizmet noktası.",
        "image_url": INSTITUTION_IMAGES["banka"],
    },
    {
        "name": "Ziraat Bankası Yenişakran-Aliağa Şubesi",
        "category": "banka",
        "subcategory": "sube",
        "address": "Yenişakran, Aliağa / İzmir",
        "phone": "0232 628 92 00",
        "description": "Yenişakran ve Aliağa çevresi için Ziraat Bankası şube kaydı.",
        "image_url": INSTITUTION_IMAGES["banka"],
    },
    {
        "name": "QNB Finansbank ATM - Demokrasi Meydanı",
        "category": "atm",
        "subcategory": "atm",
        "address": "Demokrasi Meydanı No:1, Aliağa Merkez, Aliağa / İzmir",
        "description": "Aliağa Demokrasi Meydanı çevresinde QNB Finansbank ATM noktası.",
        "image_url": INSTITUTION_IMAGES["atm"],
    },
    {
        "name": "Garanti BBVA ATM - İstiklal Caddesi",
        "category": "atm",
        "subcategory": "atm",
        "address": "İstiklal Caddesi çevresi, Aliağa / İzmir",
        "description": "İstiklal Caddesi çevresinde günlük nakit ve temel bankacılık işlemleri için Garanti BBVA ATM noktası.",
        "image_url": INSTITUTION_IMAGES["atm"],
    },
    {
        "name": "Aliağa İZBAN İstasyonu Çevresi Park Alanı",
        "category": "otopark",
        "subcategory": "acik_park",
        "address": "İstasyon Caddesi, Siteler Mahallesi, Aliağa / İzmir",
        "description": "İZBAN Aliağa istasyonu çevresinde araç bırakma ve kısa süreli park için kullanılan açık park alanı. Doluluk saha koşuluna göre değişebilir.",
        "image_url": INSTITUTION_IMAGES["otopark"],
    },
    {
        "name": "Kapalı Pazaryeri Çevresi Park Alanı",
        "category": "otopark",
        "subcategory": "acik_park",
        "address": "Beyazıt Caddesi No:6, Atatürk Mahallesi, Aliağa / İzmir",
        "description": "Kapalı pazaryeri ve çevre ticaret alanlarına erişim için kullanılan açık park noktası. Pazar günlerinde doluluk artabilir.",
        "image_url": INSTITUTION_IMAGES["otopark"],
    },
    {
        "name": "Demokrasi Meydanı Çevresi Park Alanı",
        "category": "otopark",
        "subcategory": "acik_park",
        "address": "Demokrasi Meydanı, Aliağa Merkez, Aliağa / İzmir",
        "description": "Aliağa merkezde kısa süreli şehir içi işler için kullanılan meydan çevresi park noktası. Trafik ve doluluk saatlere göre değişebilir.",
        "image_url": INSTITUTION_IMAGES["otopark"],
    },
]

EMERGENCY_DESCRIPTIONS = {
    "Polis İmdat": "Acil güvenlik ve asayiş durumları için 7/24 resmi çağrı hattı.",
    "Ambulans / Acil Yardım": "Acil sağlık, ambulans ve tıbbi yardım için 7/24 çağrı hattı.",
    "İtfaiye": "Yangın, kurtarma ve itfaiye müdahalesi gerektiren acil durumlar.",
    "Jandarma": "Jandarma sorumluluk alanındaki güvenlik ve acil yardım başvuruları.",
    "Sahil Güvenlik": "Deniz güvenliği, kıyı ve deniz acil durumları için çağrı hattı.",
    "İZSU Arıza": "Su kesintisi, kanalizasyon ve altyapı arızaları için İZSU hattı.",
    "GDZ Elektrik Arıza": "Elektrik kesintisi ve dağıtım arızaları için resmi arıza hattı.",
    "Doğalgaz Arıza (İzmirgaz)": "Doğalgaz kaçağı, koku ve acil gaz arızaları için hat.",
    "Cenaze Hizmetleri (Belediye)": "Cenaze, defin ve belediye cenaze hizmetleri için yönlendirme hattı.",
    "Aliağa Belediyesi Çözüm Masası": "Belediye talep, öneri, şikayet ve başvuru yönlendirme hattı.",
    "Aliağa Belediyesi Ana Santral": "Aliağa Belediyesi ana iletişim santrali.",
}


def _norm(text: str | None) -> str:
    raw = (text or "").strip().lower()
    raw = raw.translate(str.maketrans("çğıöşü", "cgiosu"))
    normalized = "".join(ch for ch in unicodedata.normalize("NFKD", raw) if not unicodedata.combining(ch))
    return " ".join(normalized.split())


def _is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _clean_tags(tags: list[Any] | None) -> list[str]:
    return [str(tag).strip() for tag in (tags or []) if str(tag or "").strip()]


def _label_for_category(category: str | None, fallback: str = "şehir rehberi") -> str:
    normalized = _norm(category)
    for key, label in CATEGORY_LABELS.items():
        if _norm(key) in normalized:
            return label
    if normalized.startswith("kurum"):
        return "kamu kurumu"
    return fallback


def _pick_image(pool_key: str, seed: str | None) -> str:
    pool = IMAGE_POOLS.get(pool_key) or IMAGE_POOLS["culture"]
    digest = hashlib.sha1((seed or pool_key).encode("utf-8", errors="ignore")).hexdigest()
    return pool[int(digest[:8], 16) % len(pool)]


def _place_pool_key(category: str | None, subcategory: str | None) -> str:
    text = _norm(f"{category or ''} {subcategory or ''}")
    if any(key in text for key in ("restoran", "fast_food", "balik", "kebap", "pide", "yemek", "lokanta", "cuisine")):
        return "food"
    if any(key in text for key in ("kafe", "cafe", "coffee", "bar")):
        return "cafe"
    if any(key in text for key in ("sahil", "plaj", "deniz", "marina")):
        return "coast"
    if any(key in text for key in ("park", "yesil", "leisure", "playground", "doga")):
        return "park"
    if any(key in text for key in ("antik", "tarih", "historic", "muze", "tourism", "turistik")):
        return "history"
    if any(key in text for key in ("market", "magaza", "shop", "hairdresser", "supermarket", "convenience")):
        return "shopping"
    if any(key in text for key in ("ulasim", "fuel", "station", "otopark", "parking")):
        return "transport"
    if any(key in text for key in ("hizmet", "craft", "repair", "service")):
        return "service"
    return "culture"


def _institution_pool_key(category: str | None, subcategory: str | None) -> str:
    text = _norm(f"{category or ''} {subcategory or ''}")
    if any(key in text for key in ("saglik", "health", "hastane", "pharmacy")):
        return "health"
    if any(key in text for key in ("egitim", "okul", "lise", "universite", "school", "library", "kutuphane")):
        return "education"
    if any(key in text for key in ("spor", "fitness", "stadium")):
        return "park"
    if any(key in text for key in ("kultur", "event", "theatre", "sinema")):
        return "culture"
    if any(key in text for key in ("kargo", "ulasim", "otopark", "fuel", "transport")):
        return "transport"
    return "institution"


def _is_generic_image(value: str | None) -> bool:
    return not value or value in LEGACY_GENERIC_IMAGES


def _is_low_quality_description(value: str | None) -> bool:
    normalized = _norm(value)
    if not normalized:
        return True
    markers = (
        "osm kaynak",
        "kategori:",
        "alt kategori:",
        "calisma saatleri:",
        "sehir rehberinde",
        "kayitli noktadir",
        "kayitli kurum bilgisidir",
        "kesif noktasi",
        "rehberinde",
    )
    return len(normalized) < 90 or any(marker in normalized for marker in markers)


def _default_place_image(row: Place | dict[str, Any]) -> str:
    name = row.name if isinstance(row, Place) else row.get("name")
    category = row.category if isinstance(row, Place) else row.get("category")
    subcategory = row.subcategory if isinstance(row, Place) else row.get("subcategory")
    return _pick_image(_place_pool_key(category, subcategory), f"{name}:{category}:{subcategory}")


def _default_institution_image(row: Institution | dict[str, Any]) -> str:
    name = row.name if isinstance(row, Institution) else row.get("name")
    category = row.category if isinstance(row, Institution) else row.get("category")
    subcategory = row.subcategory if isinstance(row, Institution) else row.get("subcategory")
    return _pick_image(_institution_pool_key(category, subcategory), f"{name}:{category}:{subcategory}")


def _default_project_image(project: Project) -> str:
    text = _norm(f"{project.title} {project.category or ''} {project.status or ''}")
    if any(key in text for key in ("park", "yesil", "sahil", "plaj", "agapark")):
        return CONTENT_IMAGES["project_green"]
    if any(key in text for key in ("yol", "altyapi", "tesis", "kent", "meydan", "otopark", "pazar")):
        return CONTENT_IMAGES["project_infra"]
    return CONTENT_IMAGES["project"]


def _generic_place_description(name: str, category: str | None, subcategory: str | None = None) -> str:
    label = _label_for_category(subcategory or category, "keşif noktası")
    return f"{name}, Aliağa ilçe rehberinde kayıtlı bir {label} noktasıdır."


def _generic_institution_description(name: str, category: str | None) -> str:
    label = _label_for_category(category, "kurum")
    return f"{name}, Aliağa rehberinde yer alan bir {label} kaydıdır."


def _generic_service_description(name: str, category: str | None) -> str:
    label = _label_for_category(category, "hizmet")
    return f"{name}, Aliağa rehberinde {label} kategorisinde kayıtlı hizmet noktasıdır; gitmeden veya çağırmadan önce telefonla teyit önerilir."


def _phone_for_taxi(name: str | None) -> str | None:
    normalized = _norm(name)
    direct = TAXI_PHONE_SUPPLEMENTS.get(normalized)
    if direct:
        return direct
    for key, phone in TAXI_PHONE_SUPPLEMENTS.items():
        if key in normalized:
            return phone
    return None


def _fill_model(row: Any, data: dict[str, Any], *, overwrite_blank_only: bool = True) -> int:
    changed = 0
    for field, value in data.items():
        if value is None or not hasattr(row, field):
            continue
        current = getattr(row, field)
        should_set = _is_blank(current) if overwrite_blank_only else current != value
        if should_set:
            setattr(row, field, value)
            changed += 1
    return changed


async def _upsert_places(session: AsyncSession) -> int:
    rows = (await session.execute(select(Place))).scalars().all()
    by_name = {_norm(row.name): row for row in rows}
    changed = 0

    for item in PLACES:
        data = dict(item)
        data.update(PLACE_SUPPLEMENTS.get(item["name"], {}))
        data.setdefault("address", f"{item['name']}, Aliağa / İzmir")
        data.setdefault("image_url", _default_place_image(data))
        data.setdefault("description", _generic_place_description(data["name"], data.get("category"), data.get("subcategory")))
        data.setdefault("rating", 4.4 if data.get("category") in {"restoran", "kafe"} else 4.6)

        existing = by_name.get(_norm(data["name"]))
        if existing is None:
            session.add(Place(**data))
            changed += 1
            continue

        if _is_generic_image(existing.image_url):
            data["image_url"] = _default_place_image(existing)
        changed += _fill_model(existing, data)
        if _is_low_quality_description(existing.description):
            existing.description = data.get("description") or _generic_place_description(existing.name, existing.category, existing.subcategory)
            changed += 1

    for row in rows:
        supplement = PLACE_SUPPLEMENTS.get(row.name, {})
        fallback = {
            "address": supplement.get("address") or f"{row.name}, Aliağa / İzmir",
            "image_url": supplement.get("image_url") or _default_place_image(row),
            "website": supplement.get("website"),
            "description": supplement.get("description") or _generic_place_description(row.name, row.category, row.subcategory),
        }
        changed += _fill_model(row, fallback)
        if _is_generic_image(row.image_url):
            row.image_url = fallback["image_url"]
            changed += 1
        if _is_low_quality_description(row.description):
            row.description = fallback["description"]
            changed += 1
        clean_tags = _clean_tags(row.tags) or [_label_for_category(row.subcategory or row.category, "Aliağa"), "Aliağa"]
        if row.tags != clean_tags:
            row.tags = clean_tags
            changed += 1

    return changed


async def _upsert_institutions(session: AsyncSession) -> int:
    rows = (await session.execute(select(Institution))).scalars().all()
    by_name = {_norm(row.name): row for row in rows}
    changed = 0

    for item in [*INSTITUTIONS, *ADDITIONAL_INSTITUTIONS]:
        data = dict(item)
        data.update(INSTITUTION_SUPPLEMENTS.get(item["name"], {}))
        data.setdefault("image_url", _default_institution_image(data))
        data.setdefault("description", _generic_institution_description(data["name"], data.get("category")))
        existing = by_name.get(_norm(data["name"]))
        if existing is None:
            session.add(Institution(**data))
            changed += 1
            continue
        changed += _fill_model(existing, data)
        if _is_generic_image(existing.image_url):
            existing.image_url = _default_institution_image(existing)
            changed += 1
        if _is_low_quality_description(existing.description):
            existing.description = data.get("description") or _generic_institution_description(existing.name, existing.category)
            changed += 1

    for row in rows:
        supplement = INSTITUTION_SUPPLEMENTS.get(row.name, {})
        if not supplement:
            supplement = {
                "address": f"Aliağa merkez, Aliağa / İzmir",
                "description": _generic_institution_description(row.name, row.category),
            }
        supplement = {**supplement, "image_url": supplement.get("image_url") or _default_institution_image(row)}
        changed += _fill_model(row, supplement)
        if _is_generic_image(row.image_url):
            row.image_url = supplement["image_url"]
            changed += 1
        if _is_low_quality_description(row.description):
            row.description = supplement.get("description") or _generic_institution_description(row.name, row.category)
            changed += 1

    return changed


async def _upsert_postal_codes(session: AsyncSession) -> int:
    rows = (await session.execute(select(PostalCode))).scalars().all()
    by_neighborhood = {_norm(row.neighborhood): row for row in rows}
    changed = 0

    for item in POSTAL_CODES:
        existing = by_neighborhood.get(_norm(item["neighborhood"]))
        if existing is None:
            session.add(PostalCode(**item))
            changed += 1
        else:
            changed += _fill_model(existing, item)
    return changed


async def _complete_emergency_contacts(session: AsyncSession) -> int:
    rows = (await session.execute(select(EmergencyContact))).scalars().all()
    changed = 0
    for row in rows:
        description = EMERGENCY_DESCRIPTIONS.get(row.name)
        if not description:
            name = _norm(row.name)
            category = _norm(row.category)
            if "izsu" in name:
                description = "Su kesintisi, içme suyu ve kanalizasyon arıza bildirimleri için İZSU iletişim kaydı."
            elif "belediye" in name or "153" in name or "cozum" in name:
                description = "Aliağa Belediyesi talep, başvuru, yönlendirme ve çözüm merkezi iletişim kaydı."
            elif "hastane" in name or "saglik" in category:
                description = "Aliağa sağlık hizmetleri ve acil yönlendirme için resmi kurum iletişim kaydı."
            elif "elektrik" in name or "gdz" in name:
                description = "Elektrik dağıtım arızaları ve kesinti bildirimleri için resmi iletişim kaydı."
            elif "polis" in name or "jandarma" in name:
                description = "Acil güvenlik ve kolluk kuvveti yönlendirmesi için resmi iletişim kaydı."
        if description and _is_blank(row.description):
            row.description = description
            changed += 1
    return changed


async def _sync_poi_catalog_to_places(session: AsyncSession) -> int:
    pois = (await session.execute(select(PoiCatalog))).scalars().all()
    places = (await session.execute(select(Place))).scalars().all()
    by_name = {_norm(row.name): row for row in places}
    changed = 0

    for poi in pois:
        existing = by_name.get(_norm(poi.ad))
        data = {
            "name": poi.ad,
            "category": poi.kategori or "turistik",
            "subcategory": poi.kategori,
            "description": poi.aciklama or _generic_place_description(poi.ad, poi.kategori, poi.kategori),
            "address": f"{poi.mahalle}, Aliağa / İzmir" if poi.mahalle else "Aliağa / İzmir",
            "latitude": poi.latitude,
            "longitude": poi.longitude,
            "website": poi.resmi_url or poi.source_url,
            "rating": max(0.0, min(5.0, poi.quality_score * 5)),
            "image_url": _default_place_image({"category": poi.kategori, "subcategory": poi.kategori}),
            "tags": _clean_tags([poi.kategori, poi.mahalle, "Aliağa"]),
            "is_active": True,
        }
        if existing is None:
            session.add(Place(**data))
            changed += 1
        else:
            changed += _fill_model(existing, data)
    return changed


async def _ensure_municipal_service_basics(session: AsyncSession) -> int:
    rows = (await session.execute(select(MunicipalService))).scalars().all()
    existing = {(_norm(row.hizmet_tipi), _norm(row.birim)) for row in rows}
    defaults = [
        ("belediye", "Çözüm Merkezi", "Hafta içi mesai saatleri", "153"),
        ("belediye", "İmar ve Ruhsat İşlemleri", "Hafta içi mesai saatleri", "0232 399 00 00"),
        ("belediye", "Nikah İşlemleri", "Hafta içi mesai saatleri", "0232 399 00 00"),
        ("belediye", "Sosyal Destek Hizmetleri", "Hafta içi mesai saatleri", "0232 399 00 00"),
        ("belediye", "Vezne ve Ödeme İşlemleri", "Hafta içi mesai saatleri", "0232 399 00 00"),
        ("belediye", "Cenaze Hizmetleri", "7/24 yönlendirme", "188"),
    ]
    changed = 0
    for hizmet_tipi, birim, hours, phone in defaults:
        key = (_norm(hizmet_tipi), _norm(birim))
        if key in existing:
            continue
        session.add(
            MunicipalService(
                hizmet_tipi=hizmet_tipi,
                birim=birim,
                calisma_saatleri=hours,
                iletisim=phone,
                source_url="https://www.aliaga.bel.tr/bize-ulasin",
                last_verified_at=date.today(),
                quality_score=0.8,
                ingestion_batch_id=f"curated-{date.today().isoformat()}",
            )
        )
        changed += 1
    return changed


async def _complete_service_providers(session: AsyncSession) -> int:
    rows = (await session.execute(select(ServiceProvider))).scalars().all()
    changed = 0
    for row in rows:
        address = row.address
        if _is_blank(address):
            address = f"{row.neighborhood}, Aliağa / İzmir" if not _is_blank(row.neighborhood) else "Aliağa merkez, Aliağa / İzmir"
        data = {
            "address": address,
            "description": _generic_service_description(row.name, row.category),
        }
        changed += _fill_model(row, data)
    return changed


async def _complete_news(session: AsyncSession) -> int:
    rows = (await session.execute(select(News))).scalars().all()
    changed = 0
    for row in rows:
        content = row.content
        if _is_blank(content):
            content = f"{row.title}. Haberin detayları kaynak bağlantısı ve belediye haber akışı üzerinden takip edilebilir."
        data = {
            "content": content,
            "image_url": row.image_url or CONTENT_IMAGES["news"],
            "category": row.category or "belediye_haber",
        }
        changed += _fill_model(row, data)
        if _is_generic_image(row.image_url):
            row.image_url = _pick_image("culture", row.title)
            changed += 1
    return changed


async def _complete_events(session: AsyncSession) -> int:
    rows = (await session.execute(select(Event))).scalars().all()
    changed = 0
    for row in rows:
        description = row.description
        if _is_blank(description):
            description = f"{row.title} etkinliği için tarih, saat ve katılım bilgileri belediye etkinlik akışı üzerinden takip edilebilir."
        data = {
            "description": description,
            "location": row.location or "Aliağa",
            "category": row.category or "kultur",
            "image_url": row.image_url or CONTENT_IMAGES["event"],
        }
        changed += _fill_model(row, data)
        if _is_generic_image(row.image_url):
            row.image_url = _pick_image("culture", row.title)
            changed += 1
    return changed


async def _complete_announcements(session: AsyncSession) -> int:
    rows = (await session.execute(select(Announcement))).scalars().all()
    changed = 0
    for row in rows:
        data = {
            "content": row.content or f"{row.title}. Duyuru ayrıntıları resmi belediye kaynağından takip edilebilir.",
        }
        changed += _fill_model(row, data)
    return changed


async def _complete_projects(session: AsyncSession) -> int:
    rows = (await session.execute(select(Project))).scalars().all()
    changed = 0
    for row in rows:
        description = row.description
        if _is_blank(description):
            description = f"{row.title} projesi Aliağa Belediyesi proje akışında yer alan resmi kayıttır."
        data = {
            "description": description,
            "category": row.category or "belediye_projesi",
            "image_url": row.image_url or _default_project_image(row),
        }
        changed += _fill_model(row, data)
        if _is_generic_image(row.image_url):
            row.image_url = _pick_image("park" if "park" in _norm(row.title) else "institution", row.title)
            changed += 1
    return changed


async def _complete_job_listings(session: AsyncSession) -> int:
    rows = (await session.execute(select(JobListing))).scalars().all()
    changed = 0
    for row in rows:
        data = {
            "company": row.company or "Aliağa iş ilanı",
            "location": row.location or "Aliağa / İzmir",
            "description": row.description or f"{row.title} ilanı için başvuru ve detay bilgileri kaynak bağlantısından takip edilebilir.",
        }
        changed += _fill_model(row, data)
    return changed


async def _complete_taxi_stands(session: AsyncSession) -> int:
    rows = (await session.execute(select(TaxiStand))).scalars().all()
    changed = 0
    for row in rows:
        data = {
            "phone": _phone_for_taxi(row.name),
            "address": row.address or "Aliağa / İzmir",
        }
        changed += _fill_model(row, data)
    return changed


async def _complete_daily_caches(session: AsyncSession) -> int:
    changed = 0
    weather_rows = (await session.execute(select(WeatherCache))).scalars().all()
    for row in weather_rows:
        data = {
            "description": row.description or "Hava durumu verisi",
            "humidity": row.humidity or "Kaynakta yok",
            "wind": row.wind or "Kaynakta yok",
            "min_temp": row.min_temp if row.min_temp is not None else row.temperature,
            "max_temp": row.max_temp if row.max_temp is not None else row.temperature,
        }
        changed += _fill_model(row, data)

    earthquake_rows = (await session.execute(select(EarthquakesCache))).scalars().all()
    for row in earthquake_rows:
        data = {
            "location": row.location or "Konum bilgisi bekleniyor",
            "source": row.source or "kandilli",
        }
        changed += _fill_model(row, data)

    izban_rows = (await session.execute(select(IzbanSchedule))).scalars().all()
    for row in izban_rows:
        if row.updated_at is None or row.updated_at.date() < date.today():
            row.updated_at = datetime.now()
            changed += 1
    return changed


async def _seed_sightseeing_routes(session: AsyncSession) -> int:
    from app.models.routes import Route, RouteStop
    from sqlalchemy import func

    existing_count = (await session.execute(select(func.count(Route.id)))).scalar() or 0
    if existing_count > 0:
        return 0

    default_routes = [
        {
            "title": "Merkez sahil, kahve ve gün batımı",
            "eyebrow": "SAHİL ROTASI",
            "description": "Aliağa merkez sahilinde yürüyüşle başlayıp deniz kenarında kahve molasıyla devam eden kısa rota. Akşamüstü ışığı ve kolay ulaşım nedeniyle ilk kez gelen kullanıcıya güvenli, sade ve uygulanabilir bir keşif planı sunar.",
            "duration": "2-3 saat",
            "icon": "water-outline",
            "image_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
            "tags": ["Sahil", "Kafe", "Yürüyüş", "Merkez"],
            "stops": [
                {"name": "Aliağa Balıkevi", "lat": 38.7960, "lng": 26.9720},
                {"name": "Seyir Cafe & Restaurant", "lat": 38.7955, "lng": 26.9755},
                {"name": "Kordon Cafeler", "lat": 38.7950, "lng": 26.9775},
                {"name": "Sahil Parkı", "lat": 38.7940, "lng": 26.9790},
            ]
        },
        {
            "title": "Aigai, Kyme ve Aiolis izleri",
            "eyebrow": "TARİH ROTASI",
            "description": "Aigai Antik Kenti, Kyme çevresi ve Aliağa'nın Aiolis geçmişini merkeze alan kültür rotası. Açık hava keşfi, arkeoloji ilgisi ve fotoğraf durakları için yarım günlük daha derin bir gezi akışı önerir.",
            "duration": "Yarım gün",
            "icon": "business-outline",
            "image_url": "https://images.unsplash.com/photo-1539650116574-75c0c6d73f6e?auto=format&fit=crop&w=1200&q=80",
            "tags": ["Antik kent", "Kültür", "Arkeoloji", "Fotoğraf"],
            "stops": [
                {"name": "Aigai Antik Kenti", "lat": 38.8319945, "lng": 27.1897746},
                {"name": "Kyme Antik Kenti", "lat": 38.8100, "lng": 26.9900},
                {"name": "Gryneion Apollon Tapınağı", "lat": 38.8320, "lng": 27.0320},
            ]
        },
        {
            "title": "Ağapark, plaj ve aile günü",
            "eyebrow": "AİLE PLANI",
            "description": "Ağapark çevresinde deniz, yürüyüş ve çocuklu aile molasını birleştiren rahat gün planı. Yaz aylarında plaj, sezon dışında yürüyüş ve açık hava dinlenmesi için kullanılabilir.",
            "duration": "3-4 saat",
            "icon": "leaf-outline",
            "image_url": "https://images.unsplash.com/photo-1473116763249-2faaef81ccda?auto=format&fit=crop&w=1200&q=80",
            "tags": ["Ağapark", "Plaj", "Aile", "Dinlenme"],
            "stops": [
                {"name": "Ağapark Plajı ve Sosyal Tesisleri", "lat": 38.825, "lng": 26.965},
                {"name": "Sahil Parkı", "lat": 38.7940, "lng": 26.9790},
            ]
        },
        {
            "title": "Yeni Şakran sahil molası",
            "eyebrow": "DENİZ KAÇAMAĞI",
            "description": "Yeni Şakran tarafında deniz havası, sahil yürüyüşü ve sakin mola arayanlar için hafif rota. Merkez dışına çıkmak isteyen kullanıcıya daha sessiz bir kıyı alternatifi verir.",
            "duration": "2-4 saat",
            "icon": "boat-outline",
            "image_url": "https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=1200&q=80",
            "tags": ["Yeni Şakran", "Sahil", "Deniz", "Sakin"],
            "stops": [
                {"name": "Yeni Şakran Sahili", "lat": 38.8800, "lng": 26.9900},
                {"name": "Gryneion Apollon Tapınağı", "lat": 38.8320, "lng": 27.0320},
            ]
        },
        {
            "title": "Kent Kitaplığı ve kültür durakları",
            "eyebrow": "KÜLTÜR PLANI",
            "description": "Kent Kitaplığı, sanat ve belediye kültür mekanlarını merkeze alan kısa şehir içi rota. Yağmurlu günlerde veya kısa boşluklarda kapalı mekan ağırlıklı keşif için uygundur.",
            "duration": "1-2 saat",
            "icon": "library-outline",
            "image_url": "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=1200&q=80",
            "tags": ["Kitaplık", "Kültür", "Sanat", "Merkez"],
            "stops": [
                {"name": "Aliağa Kent Kitaplığı", "lat": 38.7965, "lng": 26.9730},
                {"name": "ASEV (Aliağa Sanat Evi)", "lat": 38.7955, "lng": 26.9750},
            ]
        },
        {
            "title": "Lezzet, pazar ve merkez işleri",
            "eyebrow": "GÜNLÜK AKIŞ",
            "description": "Haftalık pazar bilgisi, merkez yeme içme noktaları ve kısa alışveriş işlerini tek rotada toplar. Yerel ihtiyaç odaklı, hızlı ve yürünebilir bir Aliağa planı olarak çalışır.",
            "duration": "1-3 saat",
            "icon": "restaurant-outline",
            "image_url": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=1200&q=80",
            "tags": ["Yeme içme", "Pazar", "Merkez", "Alışveriş"],
            "stops": [
                {"name": "Deniz'in Mutfağı", "lat": 38.7950, "lng": 26.9740},
                {"name": "Chef Âlâ Ocakbaşı", "lat": 38.7945, "lng": 26.9725},
                {"name": "Kapalı Pazaryeri Çevresi Park Alanı", "lat": 38.7930, "lng": 26.9720},
            ]
        }
    ]

    routes_added = 0
    for r_data in default_routes:
        route = Route(
            title=r_data["title"],
            eyebrow=r_data["eyebrow"],
            description=r_data["description"],
            duration=r_data["duration"],
            icon=r_data["icon"],
            image_url=r_data["image_url"],
            tags=r_data["tags"],
            is_active=True
        )
        session.add(route)
        await session.flush()

        for idx, stop_data in enumerate(r_data["stops"]):
            stmt = select(Place).where(func.lower(Place.name) == stop_data["name"].lower())
            place_res = await session.execute(stmt)
            place = place_res.scalars().first()

            place_id = place.id if place else None
            lat = place.latitude if (place and place.latitude is not None) else stop_data["lat"]
            lng = place.longitude if (place and place.longitude is not None) else stop_data["lng"]

            stop = RouteStop(
                route_id=route.id,
                place_id=place_id,
                stop_name=stop_data["name"],
                latitude=lat,
                longitude=lng,
                sort_order=idx
            )
            session.add(stop)
        routes_added += 1

    return routes_added


async def ensure_core_city_data(session: AsyncSession) -> dict[str, int]:
    results = {
        "places": await _upsert_places(session),
        "institutions": await _upsert_institutions(session),
        "postal_codes": await _upsert_postal_codes(session),
        "emergency_contacts": await _complete_emergency_contacts(session),
        "poi_to_places": await _sync_poi_catalog_to_places(session),
        "service_providers": await _complete_service_providers(session),
        "taxi_stands": await _complete_taxi_stands(session),
        "daily_caches": await _complete_daily_caches(session),
        "news": await _complete_news(session),
        "events": await _complete_events(session),
        "announcements": await _complete_announcements(session),
        "projects": await _complete_projects(session),
        "job_listings": await _complete_job_listings(session),
        "municipal_services": await _ensure_municipal_service_basics(session),
        "routes": await _seed_sightseeing_routes(session),
    }
    await session.flush()
    return results
