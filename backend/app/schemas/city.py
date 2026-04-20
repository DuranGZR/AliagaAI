"""Pydantic şemaları — Şehir/ulaşım modelleri."""
from datetime import datetime, time
from typing import Optional

from pydantic import BaseModel


# ── İZBAN ─────────────────────────────────────
class IzbanScheduleResponse(BaseModel):
    id: int
    line: Optional[str] = None
    station: Optional[str] = None
    direction: Optional[str] = None
    departure_time: Optional[time] = None
    day_type: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Feribot ───────────────────────────────────
class FerryScheduleResponse(BaseModel):
    id: int
    route: str
    company: Optional[str] = None
    departure_time: Optional[time] = None
    departure_port: str
    arrival_port: str
    day_type: Optional[str] = None
    season: Optional[str] = None
    duration: Optional[str] = None
    price_info: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Semt Pazarı ───────────────────────────────
class StreetMarketResponse(BaseModel):
    id: int
    name: str
    day_of_week: str
    neighborhood: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Acil Telefon ──────────────────────────────
class EmergencyContactResponse(BaseModel):
    id: int
    name: str
    phone: str
    category: Optional[str] = None
    description: Optional[str] = None
    priority: int

    model_config = {"from_attributes": True}


# ── Taksi ─────────────────────────────────────
class TaxiStandResponse(BaseModel):
    id: int
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_24h: bool

    model_config = {"from_attributes": True}


# ── Posta Kodu ────────────────────────────────
class PostalCodeResponse(BaseModel):
    id: int
    neighborhood: str
    postal_code: str
    district: str

    model_config = {"from_attributes": True}


# ── Kesinti ───────────────────────────────────
class UtilityOutageResponse(BaseModel):
    id: int
    type: str
    district: Optional[str] = None
    neighborhood: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    source: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
