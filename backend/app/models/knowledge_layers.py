"""
AliağaAI - Knowledge layer tabloları.

Bu tablolar şehir bilgisini katmanlı ve izlenebilir şekilde saklar.
Her tabloda kalite yönetişimi alanları zorunludur:
- source_url
- last_verified_at
- quality_score
- ingestion_batch_id
"""
from datetime import date, datetime, time

from sqlalchemy import Boolean, Float, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class TransportRoute(Base):
    __tablename__ = "transport_routes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mode: Mapped[str] = mapped_column(String(30), nullable=False)  # eshot | izban | vapur
    hat_no: Mapped[str | None] = mapped_column(String(50))
    guzergah: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    last_verified_at: Mapped[date] = mapped_column(nullable=False)
    quality_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.8)
    ingestion_batch_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), server_default=func.now())


class TransportStop(Base):
    __tablename__ = "transport_stops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stop_id: Mapped[str] = mapped_column(String(100), nullable=False)
    ad: Mapped[str] = mapped_column(String(255), nullable=False)
    ilce: Mapped[str | None] = mapped_column(String(100))
    mahalle: Mapped[str | None] = mapped_column(String(100))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    mode: Mapped[str] = mapped_column(String(30), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    last_verified_at: Mapped[date] = mapped_column(nullable=False)
    quality_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.8)
    ingestion_batch_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), server_default=func.now())


class TransportDeparture(Base):
    __tablename__ = "transport_departures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    route_id: Mapped[int | None] = mapped_column(Integer)
    stop_id: Mapped[str | None] = mapped_column(String(100))
    zaman: Mapped[time | None] = mapped_column(Time)
    day_type: Mapped[str | None] = mapped_column(String(50))
    realtime_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    last_verified_at: Mapped[date] = mapped_column(nullable=False)
    quality_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.75)
    ingestion_batch_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), server_default=func.now())


class PoiCatalog(Base):
    __tablename__ = "poi_catalog"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kategori: Mapped[str] = mapped_column(String(100), nullable=False)
    ad: Mapped[str] = mapped_column(String(255), nullable=False)
    aciklama: Mapped[str | None] = mapped_column(Text)
    mahalle: Mapped[str | None] = mapped_column(String(100))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    resmi_url: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    last_verified_at: Mapped[date] = mapped_column(nullable=False)
    quality_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.75)
    ingestion_batch_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), server_default=func.now())


class MunicipalService(Base):
    __tablename__ = "municipal_services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hizmet_tipi: Mapped[str] = mapped_column(String(100), nullable=False)
    birim: Mapped[str] = mapped_column(String(255), nullable=False)
    calisma_saatleri: Mapped[str | None] = mapped_column(String(255))
    iletisim: Mapped[str | None] = mapped_column(String(255))
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    last_verified_at: Mapped[date] = mapped_column(nullable=False)
    quality_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.8)
    ingestion_batch_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), server_default=func.now())


class DistrictStat(Base):
    __tablename__ = "district_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    yil: Mapped[int] = mapped_column(Integer, nullable=False)
    metrik_adi: Mapped[str] = mapped_column(String(150), nullable=False)
    metrik_degeri: Mapped[float] = mapped_column(Float, nullable=False)
    birim: Mapped[str] = mapped_column(String(50), nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False, default="Aliağa")
    neighborhood: Mapped[str | None] = mapped_column(String(100))
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    last_verified_at: Mapped[date] = mapped_column(nullable=False)
    quality_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.8)
    ingestion_batch_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), server_default=func.now())

