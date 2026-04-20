"""Pydantic şemaları — Cache tabloları (Weather, Prayer, Fuel, Currency, Gold, Earthquake)."""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


# ── Hava Durumu ───────────────────────────────
class WeatherResponse(BaseModel):
    id: int
    city: str
    date: date
    temperature: Optional[float] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    humidity: Optional[str] = None
    wind: Optional[str] = None
    min_temp: Optional[float] = None
    max_temp: Optional[float] = None
    forecast_json: Optional[dict] = None
    fetched_at: datetime

    model_config = {"from_attributes": True}


# ── Namaz Vakitleri ───────────────────────────
class PrayerTimesResponse(BaseModel):
    id: int
    city: str
    date: date
    fajr: Optional[str] = None
    sunrise: Optional[str] = None
    dhuhr: Optional[str] = None
    asr: Optional[str] = None
    maghrib: Optional[str] = None
    isha: Optional[str] = None
    fetched_at: datetime

    model_config = {"from_attributes": True}


# ── Akaryakıt ────────────────────────────────
class FuelPricesResponse(BaseModel):
    id: int
    city: str
    gasoline: Optional[float] = None
    diesel: Optional[float] = None
    lpg: Optional[float] = None
    fetched_at: datetime

    model_config = {"from_attributes": True}


# ── Döviz ─────────────────────────────────────
class CurrencyResponse(BaseModel):
    id: int
    code: str
    name: Optional[str] = None
    buying: Optional[float] = None
    selling: Optional[float] = None
    change_pct: Optional[float] = None
    fetched_at: datetime

    model_config = {"from_attributes": True}


# ── Altın ─────────────────────────────────────
class GoldResponse(BaseModel):
    id: int
    name: str
    buying: Optional[float] = None
    selling: Optional[float] = None
    change_pct: Optional[float] = None
    fetched_at: datetime

    model_config = {"from_attributes": True}


# ── Deprem ────────────────────────────────────
class EarthquakeResponse(BaseModel):
    id: int
    magnitude: float
    location: Optional[str] = None
    depth: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    event_date: Optional[datetime] = None
    source: Optional[str] = None
    fetched_at: datetime

    model_config = {"from_attributes": True}
