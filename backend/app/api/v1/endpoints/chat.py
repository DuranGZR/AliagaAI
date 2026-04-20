"""Chat (AI) API Endpoint'i."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.query_router import process_chat_query

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest, session: AsyncSession = Depends(get_db)):
    """Kullanıcının sorusunu alır, query router üzerinden işler ve AI yanıtı döner."""
    response = await process_chat_query(session, request.message)
    return response
