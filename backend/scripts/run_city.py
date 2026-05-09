import asyncio
from app.database import async_session
from app.services.scraper_city_info import scrape_and_save_city_info
from app.services.embedding import generate_embedding

async def main():
    async with async_session() as session:
        await scrape_and_save_city_info(session, embedding_fn=generate_embedding)
        await session.commit()

asyncio.run(main())
