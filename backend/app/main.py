"""
AliağaAI — FastAPI ana uygulama.

Uygulama başlatıldığında:
  1) PostgreSQL + pgvector bağlantısı kurulur.
  2) Tüm tablolar oluşturulur (create_all).
Uygulama kapatıldığında:
  3) DB engine düzgünce kapatılır.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.database import init_db, close_db, async_session
from app.api.v1.api import api_router
from app.services.seed_data import seed_all
from app.services.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama başlangıç/kapanış yaşam döngüsü."""
    logger.info("🚀 AliağaAI backend başlatılıyor...")
    logger.info(f"📦 Veritabanına bağlanılıyor: {settings.DATABASE_URL[:40]}...")
    await init_db()
    logger.success("✅ Veritabanı hazır — tüm tablolar oluşturuldu.")
    
    # 1. Sabit Verileri Yükle (Seed Data)
    try:
        async with async_session() as session:
            seed_results = await seed_all(session)
            if any(v > 0 for v in seed_results.values()):
                logger.info(f"🌱 Seed verileri eklendi: {seed_results}")
            else:
                logger.info("🌱 Seed verileri zaten mevcut, atlanıyor.")
    except Exception as e:
        logger.error(f"Seed data yüklenirken hata oluştu: {e}")

    # 2. Arka Plan Görevlerini (APScheduler) Başlat
    start_scheduler()

    yield
    
    # Kapanış işlemleri
    logger.info("🔌 Veritabanı bağlantısı ve zamanlayıcı kapatılıyor...")
    stop_scheduler()
    await close_db()
    logger.success("👋 AliağaAI backend kapatıldı.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs",
    }
