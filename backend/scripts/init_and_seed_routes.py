"""Script to initialize database tables and seed sightseeing routes."""
import asyncio
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from loguru import logger
from app.database import init_db, close_db, async_session
from app.services.seed_data import seed_all


async def main():
    logger.info("Initializing database tables...")
    await init_db()
    logger.success("Database tables initialized.")

    logger.info("Seeding routes...")
    async with async_session() as session:
        results = await seed_all(session, sync_rag_chunks=False)
        logger.info(f"Seed results: {results}")

    await close_db()
    logger.success("Completed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
