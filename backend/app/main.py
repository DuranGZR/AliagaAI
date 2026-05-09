"""
AliagaAI - FastAPI ana uygulama.
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


async def warmup_embedding_model() -> None:
    """Warm up embedding model in background to reduce first-query cold starts."""
    try:
        from app.services.embedding import get_embedding_model
        import asyncio

        await asyncio.to_thread(get_embedding_model)
        logger.info("Embedding modeli warmup tamamlandi.")
    except Exception as exc:
        logger.warning(f"Embedding warmup basarisiz: {exc}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("AliagaAI backend baslatiliyor...")
    logger.info(f"Veritabanina baglaniliyor: {settings.DATABASE_URL[:40]}...")
    await init_db()
    logger.success("Veritabani hazir - tum tablolar olusturuldu.")

    try:
        async with async_session() as session:
            seed_results = await seed_all(session)
            if any(v > 0 for v in seed_results.values()):
                logger.info(f"Seed verileri eklendi: {seed_results}")
            else:
                logger.info("Seed verileri zaten mevcut, atlaniyor.")
    except Exception as e:
        logger.error(f"Seed data yuklenirken hata olustu: {e}")

    import asyncio

    if settings.STARTUP_BACKGROUND_JOBS_ENABLED:
        start_scheduler()

        from app.services.scheduler import (
            job_aliaga_bel,
            job_chunk_sync,
            job_collectapi,
            job_earthquakes,
            job_news,
            job_obituaries_outages,
        )

        logger.info("Baslangic verileri asenkron olarak cekiliyor...")
        asyncio.create_task(job_collectapi())
        asyncio.create_task(job_earthquakes())
        asyncio.create_task(job_news())
        asyncio.create_task(job_aliaga_bel())
        asyncio.create_task(job_obituaries_outages())
        asyncio.create_task(job_chunk_sync())
    else:
        logger.warning("STARTUP_BACKGROUND_JOBS_ENABLED=false -> scheduler ve startup veri gorevleri kapali.")

    if settings.STARTUP_EMBEDDING_WARMUP_ENABLED:
        asyncio.create_task(warmup_embedding_model())
    else:
        logger.info("STARTUP_EMBEDDING_WARMUP_ENABLED=false -> embedding warmup atlandi.")

    yield

    logger.info("Veritabani baglantisi ve zamanlayici kapatiliyor...")
    if settings.STARTUP_BACKGROUND_JOBS_ENABLED:
        stop_scheduler()
    await close_db()
    logger.success("AliagaAI backend kapatildi.")


from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
