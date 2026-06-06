"""Pydantic schemas for sightseeing routes (Gezi Rotaları)."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RouteStopResponse(BaseModel):
    id: int
    route_id: int
    place_id: Optional[int] = None
    stop_name: str
    latitude: float
    longitude: float
    sort_order: int

    model_config = {"from_attributes": True}


class RouteResponse(BaseModel):
    id: int
    title: str
    eyebrow: str
    description: str
    duration: str
    icon: str
    image_url: Optional[str] = None
    tags: Optional[list[str]] = None
    is_active: bool
    created_at: datetime
    stops: list[RouteStopResponse]

    model_config = {"from_attributes": True}
