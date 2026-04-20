from fastapi import APIRouter
from app.api.v1.endpoints import (
    health, chat, pharmacies, cache, places, content, city
)

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(pharmacies.router, prefix="/pharmacies", tags=["pharmacies"])
api_router.include_router(cache.router, prefix="/data", tags=["cache_data"])
api_router.include_router(places.router, prefix="/places", tags=["places"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(city.router, prefix="/city", tags=["city"])
