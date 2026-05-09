import asyncio

from loguru import logger

from app.database import async_session
from app.services.scraper_knowledge_layers import sync_knowledge_layers


async def main():
    async with async_session() as session:
        stats = await sync_knowledge_layers(session)
        await session.commit()
        logger.success(f"Knowledge layers senkronize edildi: {stats}")


if __name__ == "__main__":
    asyncio.run(main())

