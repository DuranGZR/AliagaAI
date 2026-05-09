import asyncio
from app.database import async_session
from app.services.chunk_indexer import sync_all_document_chunks

async def run_sync():
    async with async_session() as s:
        print("Resyncing places and institutions...")
        res = await sync_all_document_chunks(s, source_types=["place", "institution"])
        print("Done:", res)

if __name__ == "__main__":
    asyncio.run(run_sync())
