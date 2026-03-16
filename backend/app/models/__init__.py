from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Float, Boolean
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.database import Base
from app.config import get_settings

settings = get_settings()
EMBEDDING_DIM = settings.embedding_dimension


class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    period = Column(String(100))
    title = Column(String(255))
    content = Column(Text)
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class Geography(Base):
    __tablename__ = "geography"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(100))
    title = Column(String(255))
    content = Column(Text)
    statistics = Column(JSONB)
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class Economy(Base):
    __tablename__ = "economy"

    id = Column(Integer, primary_key=True, index=True)
    sector = Column(String(100))
    title = Column(String(255))
    content = Column(Text)
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class Culture(Base):
    __tablename__ = "culture"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(100))
    title = Column(String(255))
    content = Column(Text)
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class EducationInfo(Base):
    __tablename__ = "education_info"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    content = Column(Text)
    statistics = Column(JSONB)
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class HealthInfo(Base):
    __tablename__ = "health_info"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    content = Column(Text)
    statistics = Column(JSONB)
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class Transport(Base):
    __tablename__ = "transport"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(100))
    title = Column(String(255))
    content = Column(Text)
    how_to_get = Column(Text)
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class AntiqueCity(Base):
    __tablename__ = "antique_cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    period = Column(String(100))
    location = Column(String(255))
    description = Column(Text)
    visit_info = Column(Text)
    maps_link = Column(String(500))
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class TourismSpot(Base):
    __tablename__ = "tourism_spots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100))
    description = Column(Text)
    address = Column(String(500))
    maps_link = Column(String(500))
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class Gastronomy(Base):
    __tablename__ = "gastronomy"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50))
    description = Column(Text)
    origin = Column(String(100))
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class HikingRoute(Base):
    __tablename__ = "hiking_routes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50))
    description = Column(Text)
    distance_km = Column(Float)
    difficulty = Column(String(50))
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class EmergencyPhone(Base):
    __tablename__ = "emergency_phones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(20))
    description = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())


class PublicInstitution(Base):
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
    __tablename__ = "health_facilities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50))
    address = Column(String(500))
    phone = Column(String(100))
    emergency = Column(Boolean, default=False)
    maps_link = Column(String(500))
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class School(Base):
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    level = Column(String(50))
    address = Column(String(500))
    phone = Column(String(100))
    website = Column(String(500))
    maps_link = Column(String(500))
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class Hotel(Base):
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
    __tablename__ = "libraries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(String(500))
    phone = Column(String(100))
    working_hours = Column(String(200))
    facilities = Column(ARRAY(String(100)))
    maps_link = Column(String(500))
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class Neighborhood(Base):
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
    __tablename__ = "municipal_services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50))
    description = Column(Text)
    address = Column(String(500))
    phone = Column(String(50))
    working_hours = Column(String(200))
    how_to_apply = Column(Text)
    source_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class PharmacyDuty(Base):
    __tablename__ = "pharmacy_duties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(String(500))
    phone = Column(String(50))
    maps_link = Column(String(500))
    duty_date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())


class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50))
    description = Column(Text)
    address = Column(String(500))
    phone = Column(String(50))
    maps_link = Column(String(500))
    rating = Column(Float)
    tags = Column(ARRAY(String(50)))
    features = Column(JSONB)
    source = Column(String(20), default="manual")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    summary = Column(Text)
    content = Column(Text)
    image_url = Column(String(500))
    published_date = Column(Date, index=True)
    category = Column(String(50))
    source_url = Column(String(500), unique=True)
    created_at = Column(DateTime, server_default=func.now())


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text)
    type = Column(String(50))
    published_date = Column(Date, index=True)
    deadline = Column(Date)
    source_url = Column(String(500), unique=True)
    created_at = Column(DateTime, server_default=func.now())


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    event_date = Column(Date, index=True)
    event_time = Column(String(20))
    location = Column(String(255))
    category = Column(String(50))
    image_url = Column(String(500))
    is_free = Column(Boolean, default=True)
    source_url = Column(String(500), unique=True)
    created_at = Column(DateTime, server_default=func.now())


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False)
    description = Column(Text)
    status = Column(String(50))
    category = Column(String(50))
    start_date = Column(Date)
    end_date = Column(Date)
    budget = Column(String(100))
    image_url = Column(String(500))
    source_url = Column(String(500), unique=True)
    created_at = Column(DateTime, server_default=func.now())


# RAG: vektör araması için chunk tablosu
class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    source_table = Column(String(100), nullable=False, index=True)
    source_id = Column(Integer, nullable=False)
    chunk_index = Column(Integer, default=0)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(EMBEDDING_DIM))
    metadata_ = Column("metadata", JSONB, default={})
    created_at = Column(DateTime, server_default=func.now())
