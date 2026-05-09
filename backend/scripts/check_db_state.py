"""Check current database state for debugging RAG quality."""
import asyncio
from sqlalchemy import text
from app.database import async_session

async def check():
    async with async_session() as session:
        # First check what tables exist
        result = await session.execute(text(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
        ))
        print("=== EXISTING TABLES ===")
        tables = []
        for row in result:
            tables.append(row[0])
            print(f"  {row[0]}")

        # Check document_chunks if exists
        if "document_chunks" in tables:
            result = await session.execute(text(
                "SELECT source_type, COUNT(*) as cnt FROM document_chunks GROUP BY source_type ORDER BY cnt DESC"
            ))
            print("\n=== DOCUMENT_CHUNKS by source_type ===")
            for row in result:
                print(f"  {row[0]}: {row[1]}")

            result = await session.execute(text("SELECT COUNT(*) FROM document_chunks"))
            print(f"Total chunks: {result.scalar()}")

            # Sample chunks with 'izban' in content
            result = await session.execute(text(
                "SELECT source_type, LEFT(content, 200), metadata_json->>'title' FROM document_chunks WHERE LOWER(content) LIKE '%%izban%%' LIMIT 5"
            ))
            rows = result.fetchall()
            print(f"\n=== CHUNKS containing IZBAN: {len(rows)} ===")
            for row in rows:
                print(f"  [{row[0]}] title={row[2]} | {(row[1] or '')[:120]}...")

            # Chunks for 'tarih'
            result = await session.execute(text(
                "SELECT source_type, LEFT(content, 200), metadata_json->>'title' FROM document_chunks WHERE LOWER(content) LIKE '%%tarih%%' LIMIT 5"
            ))
            rows = result.fetchall()
            print(f"\n=== CHUNKS containing TARIH: {len(rows)} ===")
            for row in rows:
                print(f"  [{row[0]}] title={row[2]} | {(row[1] or '')[:120]}...")

            # Average chunk lengths
            result = await session.execute(text("SELECT AVG(LENGTH(content)), MIN(LENGTH(content)), MAX(LENGTH(content)) FROM document_chunks"))
            row = result.fetchone()
            if row and row[0]:
                print(f"\n=== CHUNK LENGTHS: avg={row[0]:.0f}, min={row[1]}, max={row[2]} ===")

        else:
            print("\n!!! document_chunks TABLE DOES NOT EXIST !!!")

        # Check other tables
        for table in ["izban_schedules", "transport_routes", "transport_stops", "city_knowledge",
                       "places", "institutions", "news", "events", "announcements", "projects",
                       "job_listings", "pharmacies", "utility_outages"]:
            if table in tables:
                result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                print(f"  {table}: {result.scalar()} rows")
            else:
                print(f"  {table}: TABLE MISSING")

asyncio.run(check())
