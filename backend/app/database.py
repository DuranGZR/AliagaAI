"""
AliağaAI — Async veritabanı bağlantısı ve oturum yönetimi.

Supabase PostgreSQL + pgvector bağlantısını yönetir.
Tüm tablolar Base.metadata üzerinden oluşturulur.
"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

from app.core.config import settings


# ── Engine ────────────────────────────────────────────────────────────
engine = create_async_engine(
    settings.async_database_url,
    echo=settings.DEBUG,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

# ── Session Factory ───────────────────────────────────────────────────
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Base Model ────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Tüm SQLAlchemy modellerinin miras aldığı temel sınıf."""
    pass


# ── Dependency — FastAPI endpoint'lerde kullanılacak ──────────────────
async def get_db() -> AsyncSession:
    """Her request için bağımsız bir async session sağlar."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ── Init ──────────────────────────────────────────────────────────────
async def init_db():
    """
    Uygulama başladığında çağrılır.
    1) pgvector extension'ını etkinleştirmeye çalışır (yoksa uyarı verir).
    2) Tanımlı tüm tabloları oluşturur (varsa atlar).
    """
    from loguru import logger

    async with engine.begin() as conn:
        # pgvector extension — yoksa uyarı ver ama çökme
        try:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            logger.success("pgvector extension aktif.")
        except Exception:
            logger.warning(
                "pgvector extension yuklenemedi. "
                "DocumentChunk tablosu olusturulamayacak. "
                "Diger tum tablolar normal calisacak."
            )
        # Tüm modelleri import ederek metadata'ya kayıt ol
        from app.models import cache, city, content, places  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Uygulama kapanırken engine'i düzgünce kapat."""
    await engine.dispose()
