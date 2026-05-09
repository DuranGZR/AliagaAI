import asyncio

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database import get_db

router = APIRouter()

@router.get("/")
async def health_check(session: AsyncSession = Depends(get_db)):
    db_ok = False
    try:
        await asyncio.wait_for(session.execute(text("SELECT 1")), timeout=1.5)
        db_ok = True
    except Exception:
        db_ok = False

    llm_configured = bool(settings.GROQ_API_KEY)
    overall_status = "ok" if db_ok else "degraded"
    return {
        "status": overall_status,
        "database": "ok" if db_ok else "error",
        "llm_configured": llm_configured,
    }
