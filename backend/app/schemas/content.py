"""Pydantic şemaları — İçerik modelleri (News, Event, Announcement, Project, Job, Obituary)."""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


# ── Haber ─────────────────────────────────────
class NewsResponse(BaseModel):
    id: int
    title: str
    slug: Optional[str] = None
    content: Optional[str] = None
    source_url: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    published_at: Optional[date] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class NewsListResponse(BaseModel):
    items: list[NewsResponse]
    total: int


# ── Etkinlik ──────────────────────────────────
class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    category: Optional[str] = None
    event_date: Optional[date] = None
    end_date: Optional[date] = None
    event_time: Optional[str] = None
    source_url: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Duyuru ────────────────────────────────────
class AnnouncementResponse(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    type: str
    published_at: Optional[date] = None
    source_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Proje ─────────────────────────────────────
class ProjectResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    category: Optional[str] = None
    source_url: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── İş İlanı ──────────────────────────────────
class JobListingResponse(BaseModel):
    id: int
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    source_url: Optional[str] = None
    published_at: Optional[date] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Vefat ─────────────────────────────────────
class ObituaryResponse(BaseModel):
    id: int
    name: str
    death_date: Optional[date] = None
    funeral_time: Optional[str] = None
    funeral_location: Optional[str] = None
    neighborhood: Optional[str] = None
    details: Optional[str] = None
    source: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
