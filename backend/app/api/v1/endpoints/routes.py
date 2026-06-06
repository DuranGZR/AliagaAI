"""Sightseeing routes (Gezi Rotaları) endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.routes import Route
from app.schemas.routes import RouteResponse
from app.core.limiter import limiter

router = APIRouter()


@router.get("/", response_model=list[RouteResponse])
@limiter.limit("60/minute")
async def get_routes(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """Retrieve all active sightseeing routes with their stops."""
    stmt = (
        select(Route)
        .options(selectinload(Route.stops))
        .where(Route.is_active == True)
        .offset(skip)
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get("/{route_id}", response_model=RouteResponse)
@limiter.limit("30/minute")
async def get_route(
    request: Request,
    route_id: int,
    session: AsyncSession = Depends(get_db),
):
    """Retrieve a single sightseeing route by its ID."""
    stmt = (
        select(Route)
        .options(selectinload(Route.stops))
        .where(Route.id == route_id, Route.is_active == True)
    )
    result = await session.execute(stmt)
    route = result.scalar_one_or_none()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route
