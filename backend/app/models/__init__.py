"""
AliağaAI Database Models v3
15+ Ayrı Tablo - Kategori Bazlı Organizasyon
AI için optimize edilmiş yapı
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Float, Boolean, JSON
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.sql import func
from app.database import Base


# ============================================================================
# ŞEHİR BİLGİSİ (7 Tablo)
# ============================================================================

class History(Base):
    """Tarihçe - Aliağa'nın tarihi"""
    __tablename__ = "history"
    
    id = Column(Integer, primary_key=True, index=True)
    period = Column(String(100))  # Antik Çağ, Osmanlı, Cumhuriyet
    title = Column(String(255))
    content = Column(Text)
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class Geography(Base):
    """Coğrafya - İklim, nüfus, konum"""
    __tablename__ = "geography"
    
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(100))  # iklim, nufus, konum
    title = Column(String(255))
    content = Column(Text)
    statistics = Column(JSONB)  # {"nufus": 100000, "alan_km2": 300}
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class Economy(Base):
    """Ekonomi - Sanayi, tarım, ticaret"""
    __tablename__ = "economy"
    
    id = Column(Integer, primary_key=True, index=True)
    sector = Column(String(100))  # sanayi, tarim, ticaret
    title = Column(String(255))
    content = Column(Text)
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class Culture(Base):
    """Kültür - El sanatı, festival, gelenek"""
    __tablename__ = "culture"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(100))  # el_sanati, festival, gelenek
    title = Column(String(255))
    content = Column(Text)
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class EducationInfo(Base):
    """Eğitim Bilgisi - Genel eğitim durumu"""
    __tablename__ = "education_info"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    content = Column(Text)
    statistics = Column(JSONB)
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class HealthInfo(Base):
    """Sağlık Bilgisi - Genel sağlık durumu"""
    __tablename__ = "health_info"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    content = Column(Text)
    statistics = Column(JSONB)
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class Transport(Base):
    """Ulaşım - Nasıl gelinir"""
    __tablename__ = "transport"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(100))  # otobus, tren, deniz
    title = Column(String(255))
    content = Column(Text)
    how_to_get = Column(Text)  # Aliağa'ya nasıl gelinir
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


# ============================================================================
# TURİZM (4 Tablo)
# ============================================================================

class AntiqueCity(Base):
    """Antik Kentler - Kyme, Myrina, Gryneion"""
    __tablename__ = "antique_cities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    period = Column(String(100))  # MÖ 11. yy
    location = Column(String(255))
    description = Column(Text)
    visit_info = Column(Text)  # Ziyaret bilgileri
    maps_link = Column(String(500))
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class TourismSpot(Base):
    """Gezilecek Yerler"""
    __tablename__ = "tourism_spots"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100))  # plaj, doga, tarihi
    description = Column(Text)
    address = Column(String(500))
    maps_link = Column(String(500))
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class Gastronomy(Base):
    """Yöresel Lezzetler"""
    __tablename__ = "gastronomy"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50))  # yemek, tatli, icecek
    description = Column(Text)
    origin = Column(String(100))  # Şakran, Helvacı
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class HikingRoute(Base):
    """Gezi Rotaları"""
    __tablename__ = "hiking_routes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50))  # bisiklet, yuruyus, araba
    description = Column(Text)
    distance_km = Column(Float)
    difficulty = Column(String(50))
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


# ============================================================================
# KURUMLAR (6 Tablo)
# ============================================================================

class EmergencyPhone(Base):
    """Acil Telefonlar"""
    __tablename__ = "emergency_phones"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(20))
    description = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())


class PublicInstitution(Base):
    """Kamu Kuruluşları"""
    __tablename__ = "public_institutions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(String(500))
    phone = Column(String(100))
    fax = Column(String(50))
    email = Column(String(255))
    website = Column(String(500))
    working_hours = Column(String(200))
    maps_link = Column(String(500))
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class HealthFacility(Base):
    """Sağlık Kuruluşları"""
    __tablename__ = "health_facilities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50))  # hastane, saglik_ocagi, eczane
    address = Column(String(500))
    phone = Column(String(100))
    emergency = Column(Boolean, default=False)
    maps_link = Column(String(500))
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class School(Base):
    """Okullar"""
    __tablename__ = "schools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    level = Column(String(50))  # ilkokul, ortaokul, lise
    address = Column(String(500))
    phone = Column(String(100))
    website = Column(String(500))
    maps_link = Column(String(500))
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class Hotel(Base):
    """Oteller"""
    __tablename__ = "hotels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    stars = Column(Integer)
    address = Column(String(500))
    phone = Column(String(100))
    website = Column(String(500))
    maps_link = Column(String(500))
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class Library(Base):
    """Kütüphaneler"""
    __tablename__ = "libraries"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(String(500))
    phone = Column(String(100))
    working_hours = Column(String(200))
    facilities = Column(ARRAY(String(100)))  # wifi, calisma_salonu
    maps_link = Column(String(500))
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


# ============================================================================
# YEREL (4 Tablo)
# ============================================================================

class Neighborhood(Base):
    """Mahalleler"""
    __tablename__ = "neighborhoods"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    muhtar_name = Column(String(255))
    phone = Column(String(50))
    address = Column(String(500))
    population = Column(Integer)
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class MunicipalService(Base):
    """Belediye Hizmetleri"""
    __tablename__ = "municipal_services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50))  # sosyal, cevre, kultur, spor
    description = Column(Text)
    address = Column(String(500))
    phone = Column(String(50))
    working_hours = Column(String(200))
    how_to_apply = Column(Text)  # Başvuru bilgisi
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class PharmacyDuty(Base):
    """Nöbetçi Eczane"""
    __tablename__ = "pharmacy_duties"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(String(500))
    phone = Column(String(50))
    maps_link = Column(String(500))
    duty_date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())


class Place(Base):
    """Mekanlar (Manuel Giriş)"""
    __tablename__ = "places"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50))  # kafe, restoran, market
    address = Column(String(500))
    phone = Column(String(50))
    maps_link = Column(String(500))
    rating = Column(Float)
    tags = Column(ARRAY(String(50)))  # sessiz, wifi, otopark
    source = Column(String(20))  # manual, google
    created_at = Column(DateTime, server_default=func.now())


# ============================================================================
# DİNAMİK VERİLER (Sürekli Güncellenen)
# ============================================================================

class News(Base):
    """Haberler - Günlük/Haftalık güncelleme"""
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    summary = Column(Text)  # İlk paragraf
    content = Column(Text)
    image_url = Column(String(500))
    published_date = Column(Date, index=True)
    category = Column(String(50))  # genel, spor, kultur, altyapi
    source_url = Column(String(500), unique=True)  # Duplicate önleme
    created_at = Column(DateTime, server_default=func.now())


class Announcement(Base):
    """Duyurular - İhale, resmi ilan"""
    __tablename__ = "announcements"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text)
    type = Column(String(50))  # ihale, ilan, duyuru
    published_date = Column(Date, index=True)
    deadline = Column(Date)  # Son başvuru tarihi (ihaleler için)
    source_url = Column(String(500), unique=True)
    created_at = Column(DateTime, server_default=func.now())


class Event(Base):
    """Etkinlikler - Konser, tiyatro, panel"""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    event_date = Column(Date, index=True)
    event_time = Column(String(20))  # "20:00"
    location = Column(String(255))
    category = Column(String(50))  # konser, tiyatro, panel, festival
    image_url = Column(String(500))
    is_free = Column(Boolean, default=True)
    source_url = Column(String(500), unique=True)
    created_at = Column(DateTime, server_default=func.now())


class Project(Base):
    """Belediye Projeleri"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False)
    description = Column(Text)
    status = Column(String(50))  # tamamlanan, devam_eden, planlanan
    category = Column(String(50))  # altyapi, park, sosyal
    start_date = Column(Date)
    end_date = Column(Date)
    budget = Column(String(100))
    image_url = Column(String(500))
    source_url = Column(String(500), unique=True)
    created_at = Column(DateTime, server_default=func.now())

