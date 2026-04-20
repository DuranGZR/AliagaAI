"""
İçerik tabloları — Haberler, Etkinlikler, Duyurular, Projeler, İş İlanları, Vefat.

Bu tablolardaki uzun metin alanları (content, description) aynı zamanda
pgvector document_chunks tablosuna chunk olarak işlenecek (SQL + RAG hibrit).
"""
from datetime import date, datetime

from sqlalchemy import Boolean, Date, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


# ═════════════════════════════════════════════
# HABERLER
# ═════════════════════════════════════════════
class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str | None] = mapped_column(String(500))
    content: Mapped[str | None] = mapped_column(Text)  # → pgvector chunk
    source_url: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(50))
    published_at: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )


# ═════════════════════════════════════════════
# ETKİNLİKLER
# ═════════════════════════════════════════════
class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)  # → pgvector chunk
    location: Mapped[str | None] = mapped_column(String(255))
    category: Mapped[str | None] = mapped_column(String(50))
    event_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    event_time: Mapped[str | None] = mapped_column(String(50))
    source_url: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )


# ═════════════════════════════════════════════
# DUYURULAR (duyuru + ihale)
# ═════════════════════════════════════════════
class Announcement(Base):
    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str | None] = mapped_column(Text)  # → pgvector chunk
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # duyuru | ihale
    published_at: Mapped[date | None] = mapped_column(Date)
    source_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )


# ═════════════════════════════════════════════
# BELEDİYE PROJELERİ
# ═════════════════════════════════════════════
class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)  # → pgvector chunk
    status: Mapped[str] = mapped_column(String(30), nullable=False)  # tamamlanan, devam_eden, sosyal
    category: Mapped[str | None] = mapped_column(String(50))
    source_url: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )


# ═════════════════════════════════════════════
# İŞ İLANLARI
# ═════════════════════════════════════════════
class JobListing(Base):
    __tablename__ = "job_listings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    company: Mapped[str | None] = mapped_column(String(255))
    location: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)  # → pgvector chunk
    source_url: Mapped[str | None] = mapped_column(Text)
    published_at: Mapped[date | None] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )


# ═════════════════════════════════════════════
# VEFAT / CENAZE
# ═════════════════════════════════════════════
class Obituary(Base):
    __tablename__ = "obituaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    death_date: Mapped[date | None] = mapped_column(Date)
    funeral_time: Mapped[str | None] = mapped_column(String(50))
    funeral_location: Mapped[str | None] = mapped_column(String(255))
    neighborhood: Mapped[str | None] = mapped_column(String(100))
    details: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )
