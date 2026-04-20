"""Pydantic şemaları — Mekan modelleri (Pharmacy, Place, Institution, ServiceProvider)."""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


# ── Eczane ────────────────────────────────────
class PharmacyResponse(BaseModel):
    id: int
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    duty_date: date
    district: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Mekan ─────────────────────────────────────
class PlaceResponse(BaseModel):
    id: int
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    rating: float
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    working_hours: Optional[dict] = None
    image_url: Optional[str] = None
    website: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Kurum ─────────────────────────────────────
class InstitutionResponse(BaseModel):
    id: int
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    website: Optional[str] = None
    working_hours: Optional[dict] = None
    image_url: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Hizmet Sağlayıcı ─────────────────────────
class ServiceProviderResponse(BaseModel):
    id: int
    name: str
    phone: str
    category: str
    address: Optional[str] = None
    neighborhood: Optional[str] = None
    description: Optional[str] = None
    is_24h: bool
    rating: float
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
