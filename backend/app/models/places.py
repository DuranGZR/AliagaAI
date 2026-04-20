"""
Mekan ve kuruluş tabloları — Eczaneler, Mekanlar, Kurumlar, Hizmet Sağlayıcılar.

places.description ve institutions.description alanları isteğe bağlı olarak
pgvector document_chunks tablosuna da chunk olarak yazılabilir (hibrit arama).
"""
from datetime import date, datetime

from sqlalchemy import Boolean, Date, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


# ═════════════════════════════════════════════
# ECZANELER (CollectAPI — günlük güncelleme)
# ═════════════════════════════════════════════
class Pharmacy(Base):
    __tablename__ = "pharmacies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(String(50))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    duty_date: Mapped[date] = mapped_column(Date, nullable=False)
    district: Mapped[str] = mapped_column(String(100), default="Aliağa")
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now(), onupdate=func.now()
    )


# ═════════════════════════════════════════════
# MEKANLAR (Restoran, Kafe, Turistik, vb.)
# ═════════════════════════════════════════════
class Place(Base):
    __tablename__ = "places"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(String(50))
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # restoran, kafe, turistik, eglence
    subcategory: Mapped[str | None] = mapped_column(String(50))  # balik, kebap, antik_kent
    description: Mapped[str | None] = mapped_column(Text)  # → pgvector'e de gider
    tags: Mapped[list | None] = mapped_column(ARRAY(Text))  # ['deniz kenarı','aile dostu']
    rating: Mapped[float] = mapped_column(Float, default=0)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    working_hours: Mapped[dict | None] = mapped_column(JSONB)
    image_url: Mapped[str | None] = mapped_column(Text)
    website: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now(), onupdate=func.now()
    )


# ═════════════════════════════════════════════
# KURUMLAR VE TESİSLER (18 kategori)
# ═════════════════════════════════════════════
class Institution(Base):
    __tablename__ = "institutions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(String(50))
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    # kamu, saglik, egitim, banka, atm, kargo, noter, arac_muayene,
    # otel, cami, spor, kultur, kutuphane, cocuk_alani, dugun_salonu,
    # market, otopark, diger
    subcategory: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    website: Mapped[str | None] = mapped_column(Text)
    working_hours: Mapped[dict | None] = mapped_column(JSONB)
    image_url: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now(), onupdate=func.now()
    )


# ═════════════════════════════════════════════
# HİZMET SAĞLAYICILAR (Tesisatçı, Çilingir vb.)
# ═════════════════════════════════════════════
class ServiceProvider(Base):
    __tablename__ = "service_providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    # tesisatci, elektrikci, cilingir, oto_yikama, oto_tamir,
    # lastikci, kuafor, berber, veteriner, temizlik, nakliyat, diger
    address: Mapped[str | None] = mapped_column(Text)
    neighborhood: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    is_24h: Mapped[bool] = mapped_column(Boolean, default=False)
    rating: Mapped[float] = mapped_column(Float, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now(), onupdate=func.now()
    )
