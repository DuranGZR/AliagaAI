"""
Şehir altyapı tabloları + pgvector Doküman Chunk tablosu.

İZBAN, Feribot, Pazar, Acil Tel, Taksi, Posta Kodu, Kesinti → SQL Only (veya SQL+RAG)
DocumentChunk → pgvector tablosu (RAG Only / Hybrid aramalar için)
"""
import uuid
from datetime import date, datetime, time

from sqlalchemy import Boolean, Float, Index, Integer, String, Text, Time
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.config import settings
from app.database import Base

# pgvector opsiyonel — yüklü değilse DocumentChunk oluşturulmaz
try:
    from pgvector.sqlalchemy import Vector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False


# ═════════════════════════════════════════════
# İZBAN SEFER SAATLERİ
# ═════════════════════════════════════════════
class IzbanSchedule(Base):
    __tablename__ = "izban_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    line: Mapped[str | None] = mapped_column(String(100))       # Aliağa-Menderes
    station: Mapped[str | None] = mapped_column(String(100))
    direction: Mapped[str | None] = mapped_column(String(50))   # güney, kuzey
    departure_time: Mapped[time | None] = mapped_column(Time)
    day_type: Mapped[str | None] = mapped_column(String(20))    # weekday, weekend, holiday
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now(), onupdate=func.now()
    )


# ═════════════════════════════════════════════
# FERİBOT SEFERLERİ (Aliağa ↔ Midilli)
# ═════════════════════════════════════════════
class FerrySchedule(Base):
    __tablename__ = "ferry_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    route: Mapped[str] = mapped_column(String(100), default="Aliağa-Midilli")
    company: Mapped[str | None] = mapped_column(String(100))     # Turyol, Jalem Tur
    departure_time: Mapped[time | None] = mapped_column(Time)
    departure_port: Mapped[str] = mapped_column(String(100), default="Aliaport")
    arrival_port: Mapped[str] = mapped_column(String(100), default="Midilli (Mytilene)")
    day_type: Mapped[str | None] = mapped_column(String(20))     # daily, seasonal
    season: Mapped[str | None] = mapped_column(String(20))       # yaz, kış, tüm_yıl
    duration: Mapped[str | None] = mapped_column(String(20))     # "1 saat 30 dk"
    price_info: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now(), onupdate=func.now()
    )


# ═════════════════════════════════════════════
# SEMT PAZARLARI (sabit veri)
# ═════════════════════════════════════════════
class StreetMarket(Base):
    __tablename__ = "street_markets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    day_of_week: Mapped[str] = mapped_column(String(20), nullable=False)
    neighborhood: Mapped[str | None] = mapped_column(String(100))
    address: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )


# ═════════════════════════════════════════════
# ACİL TELEFONLAR (sabit veri)
# ═════════════════════════════════════════════
class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str | None] = mapped_column(String(50))  # acil, altyapi, belediye, saglik
    description: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[int] = mapped_column(Integer, default=0)  # 112 en üstte
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )


# ═════════════════════════════════════════════
# TAKSİ DURAKLARI
# ═════════════════════════════════════════════
class TaxiStand(Base):
    __tablename__ = "taxi_stands"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    is_24h: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )


# ═════════════════════════════════════════════
# POSTA KODLARI
# ═════════════════════════════════════════════
class PostalCode(Base):
    __tablename__ = "postal_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    neighborhood: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(10), nullable=False)
    district: Mapped[str] = mapped_column(String(50), default="Aliağa")
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )


# ═════════════════════════════════════════════
# SU / ELEKTRİK KESİNTİLERİ (SQL + RAG hibrit)
# ═════════════════════════════════════════════
class UtilityOutage(Base):
    __tablename__ = "utility_outages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # su | elektrik
    district: Mapped[str | None] = mapped_column(String(100))
    neighborhood: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)  # → pgvector'e de gider
    start_date: Mapped[datetime | None] = mapped_column()
    end_date: Mapped[datetime | None] = mapped_column()
    source: Mapped[str | None] = mapped_column(String(50))  # izsu | gdz
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )


# ═════════════════════════════════════════════
# DOKÜMAN CHUNK'LARI — pgvector (VEKTÖR TABLOSU)
# pgvector yüklüyse oluşturulur, yoksa atlanır.
# ═════════════════════════════════════════════
if HAS_PGVECTOR:
    class DocumentChunk(Base):
        __tablename__ = "document_chunks"

        id: Mapped[uuid.UUID] = mapped_column(
            UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        source_type: Mapped[str] = mapped_column(String(30), nullable=False)
        # source_type değerleri:
        #   place, news, event, announcement, city_info,
        #   outage, project, job, obituary
        source_id: Mapped[int | None] = mapped_column(Integer)
        chunk_index: Mapped[int] = mapped_column(Integer, default=0)
        content: Mapped[str] = mapped_column(Text, nullable=False)
        embedding: Mapped[list] = mapped_column(Vector(settings.EMBEDDING_DIM))
        metadata_json: Mapped[dict | None] = mapped_column(JSONB)
        created_at: Mapped[datetime] = mapped_column(
            default=func.now(), server_default=func.now()
        )

    # pgvector indeksleri
    Index("idx_chunks_source_type", DocumentChunk.source_type)
    Index(
        "idx_chunks_embedding",
        DocumentChunk.embedding,
        postgresql_using="ivfflat",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )
else:
    DocumentChunk = None  # pgvector yüklenince aktif olacak

