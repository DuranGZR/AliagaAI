"""
AliağaAI Backend - FastAPI Application
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.database import init_db
from app.config import get_settings
from app.routes import admin, search
from app.scheduler import init_scheduler, shutdown_scheduler

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama başlangıç ve kapanış işlemleri"""
    # Başlangıç
    logger.info("Starting AliağaAI Backend...")
    init_db()
    logger.info("Database initialized")
    
    # Scheduler başlat
    init_scheduler()
    logger.info("Scheduler initialized")
    
    yield
    
    # Kapanış
    shutdown_scheduler()
    logger.info("Shutting down AliağaAI Backend...")


app = FastAPI(
    title="AliağaAI API",
    description="Aliağa'nın Yerel Yapay Zeka Rehberi",
    version="0.1.0",
    lifespan=lifespan
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da değiştir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


@app.get("/")
async def root():
    """Ana sayfa"""
    return {
        "name": "AliağaAI API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Sağlık kontrolü"""
    return {"status": "healthy"}
