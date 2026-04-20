"""Lokal PostgreSQL baglanti testi."""
import asyncio
import sys
sys.path.insert(0, ".")

from app.core.config import settings
from app.database import engine, init_db, close_db
from sqlalchemy import text


async def test_connection():
    print(f"DB URL: {settings.async_database_url}")
    
    # 1) Baglanti testi
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            row = result.fetchone()
            print(f"[OK] PostgreSQL baglantisi BASARILI!")
            print(f"     Versiyon: {row[0][:60]}")
    except Exception as e:
        print(f"[HATA] Baglanti HATASI: {e}")
        return

    # 2) Tablolari olustur
    try:
        await init_db()
        print("[OK] init_db() calisti!")
    except Exception as e:
        print(f"[HATA] Tablo olusturma HATASI: {e}")
        import traceback
        traceback.print_exc()
        await close_db()
        return

    # 3) Tablo sayisini kontrol et
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' ORDER BY table_name"
            ))
            tables = [row[0] for row in result.fetchall()]
            print(f"\nVeritabanindaki tablolar ({len(tables)} adet):")
            for t in tables:
                print(f"   - {t}")
    except Exception as e:
        print(f"[HATA] Tablo listeleme hatasi: {e}")

    await close_db()
    print("\nTest tamamlandi!")


asyncio.run(test_connection())
