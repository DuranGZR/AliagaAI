"""SQLAlchemy models for sightseeing routes (Gezi Rotaları)."""
from __future__ import annotations
from datetime import datetime

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    eyebrow: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "SAHİL ROTASI", "TARİH ROTASI"
    description: Mapped[str] = mapped_column(Text, nullable=False)
    duration: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "2-3 saat", "Yarım gün"
    icon: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "water-outline", "business-outline"
    image_url: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(Text))  # e.g., ['Sahil', 'Kafe']
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )

    # Relationships
    stops: Mapped[list[RouteStop]] = relationship(
        "RouteStop",
        back_populates="route",
        cascade="all, delete-orphan",
        order_by="RouteStop.sort_order",
    )


class RouteStop(Base):
    __tablename__ = "route_stops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    route_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("routes.id", ondelete="CASCADE"), nullable=False
    )
    place_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("places.id", ondelete="SET NULL"), nullable=True
    )

    stop_name: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    route: Mapped[Route] = relationship("Route", back_populates="stops")
    place: Mapped[Place | None] = relationship("Place")
