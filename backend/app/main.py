from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.database import init_db, close_db
from app.config import get_settings
from app.routes.search import router as search_router
from app.routes.admin import router as admin_router
from app.scheduler import init_scheduler, shutdown_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AliağaAI Backend v%s", settings.app_version)
    await init_db()
    init_scheduler()
    yield
    shutdown_scheduler()
    await close_db()
    logger.info("AliağaAI Backend shut down")


app = FastAPI(
    title="AliağaAI API",
    description="Aliağa Hibrit Arama Tabanlı Mobil Şehir Rehberi",
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router, prefix="/api", tags=["Search & Chat"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "version": settings.app_version}
