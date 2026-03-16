from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)


class ChatResponse(BaseModel):
    query: str
    ai_response: str
    intent: dict
    results: list[dict]
    result_count: int


class PharmacyOut(BaseModel):
    id: int
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    maps_link: Optional[str] = None
    duty_date: date

    model_config = {"from_attributes": True}


class PlaceOut(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    maps_link: Optional[str] = None
    rating: Optional[float] = None
    tags: Optional[list[str]] = None

    model_config = {"from_attributes": True}


class PlaceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    maps_link: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    tags: Optional[list[str]] = None
    features: Optional[dict] = None


class PlaceUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    maps_link: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    tags: Optional[list[str]] = None
    features: Optional[dict] = None
    is_active: Optional[bool] = None


class NewsOut(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    published_date: Optional[date] = None
    category: Optional[str] = None
    source_url: Optional[str] = None

    model_config = {"from_attributes": True}


class EventOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    event_date: Optional[date] = None
    event_time: Optional[str] = None
    location: Optional[str] = None
    category: Optional[str] = None
    is_free: Optional[bool] = None

    model_config = {"from_attributes": True}


class AnnouncementOut(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    type: Optional[str] = None
    published_date: Optional[date] = None

    model_config = {"from_attributes": True}


class InstitutionOut(BaseModel):
    id: int
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    maps_link: Optional[str] = None

    model_config = {"from_attributes": True}


class ScrapeResponse(BaseModel):
    status: str
    message: str
    count: Optional[int] = None
    scraped_at: datetime


class SchedulerJobOut(BaseModel):
    id: str
    name: str
    next_run: Optional[str] = None
    trigger: str


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
