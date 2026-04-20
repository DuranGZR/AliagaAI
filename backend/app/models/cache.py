"""
Cache tabloları — CollectAPI ve açık API'lerden periyodik çekilen veriler.

Bu tablolar sadece SQL sorgusuyla erişilir (SQL Only).
pgvector'e gitmezler çünkü yapılandırılmış, kesin verilerdir.
"""
from datetime import date, datetime

from sqlalchemy import Date, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


# ═════════════════════════════════════════════
# HAVA DURUMU CACHE
# ═════════════════════════════════════════════
class WeatherCache(Base):
    __tablename__ = "weather_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    city: Mapped[str] = mapped_column(String(50), default="izmir")
    date: Mapped[date] = mapped_column(Date, nullable=False)
    temperature: Mapped[float | None] = mapped_column(Float)
    description: Mapped[str | None] = mapped_column(String(255))
    icon: Mapped[str | None] = mapped_column(String(100))
    humidity: Mapped[str | None] = mapped_column(String(20))
    wind: Mapped[str | None] = mapped_column(String(50))
    min_temp: Mapped[float | None] = mapped_column(Float)
    max_temp: Mapped[float | None] = mapped_column(Float)
    forecast_json: Mapped[dict | None] = mapped_column(JSONB)
    fetched_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )


# ═════════════════════════════════════════════
# NAMAZ VAKİTLERİ CACHE
# ═════════════════════════════════════════════
class PrayerTimesCache(Base):
    __tablename__ = "prayer_times_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    city: Mapped[str] = mapped_column(String(50), default="izmir")
    date: Mapped[date] = mapped_column(Date, nullable=False)
    fajr: Mapped[str | None] = mapped_column(String(10))       # imsak
    sunrise: Mapped[str | None] = mapped_column(String(10))     # güneş
    dhuhr: Mapped[str | None] = mapped_column(String(10))       # öğle
    asr: Mapped[str | None] = mapped_column(String(10))         # ikindi
    maghrib: Mapped[str | None] = mapped_column(String(10))     # akşam
    isha: Mapped[str | None] = mapped_column(String(10))        # yatsı
    fetched_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )


# ═════════════════════════════════════════════
# AKARYAKIT FİYATLARI CACHE
# ═════════════════════════════════════════════
class FuelPricesCache(Base):
    __tablename__ = "fuel_prices_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    city: Mapped[str] = mapped_column(String(50), default="izmir")
    gasoline: Mapped[float | None] = mapped_column(Float)
    diesel: Mapped[float | None] = mapped_column(Float)
    lpg: Mapped[float | None] = mapped_column(Float)
    fetched_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )


# ═════════════════════════════════════════════
# DÖVİZ KURLARI CACHE
# ═════════════════════════════════════════════
class CurrencyCache(Base):
    __tablename__ = "currency_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(10), nullable=False)  # USD, EUR, GBP
    name: Mapped[str | None] = mapped_column(String(100))
    buying: Mapped[float | None] = mapped_column(Float)
    selling: Mapped[float | None] = mapped_column(Float)
    change_pct: Mapped[float | None] = mapped_column(Float)
    fetched_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )


# ═════════════════════════════════════════════
# ALTIN FİYATLARI CACHE
# ═════════════════════════════════════════════
class GoldCache(Base):
    __tablename__ = "gold_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # Gram, Çeyrek vb.
    buying: Mapped[float | None] = mapped_column(Float)
    selling: Mapped[float | None] = mapped_column(Float)
    change_pct: Mapped[float | None] = mapped_column(Float)
    fetched_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )


# ═════════════════════════════════════════════
# SON DEPREMLER CACHE (Kandilli / AFAD)
# ═════════════════════════════════════════════
class EarthquakesCache(Base):
    __tablename__ = "earthquakes_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    magnitude: Mapped[float] = mapped_column(Float, nullable=False)
    location: Mapped[str | None] = mapped_column(String(255))
    depth: Mapped[float | None] = mapped_column(Float)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    event_date: Mapped[datetime | None] = mapped_column()
    source: Mapped[str | None] = mapped_column(String(20))  # kandilli | afad
    fetched_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )
