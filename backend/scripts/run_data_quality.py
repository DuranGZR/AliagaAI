import asyncio

from loguru import logger

from app.database import async_session
from app.services.data_quality import run_data_quality_pass


async def main():
    async with async_session() as session:
        stats = await run_data_quality_pass(session)
        logger.success(f"Data quality sonucu: {stats}")


if __name__ == "__main__":
    asyncio.run(main())

