import asyncio
from app.database import async_session
from app.services.scraper_events import scrape_and_save_events
from app.services.scraper_gallery import scrape_and_save_galleries

async def test():
    async with async_session() as session:
        events_count = await scrape_and_save_events(session)
        print(f"Events fetched: {events_count}")
        galleries_count = await scrape_and_save_galleries(session)
        print(f"Galleries fetched: {galleries_count}")

if __name__ == "__main__":
    asyncio.run(test())
