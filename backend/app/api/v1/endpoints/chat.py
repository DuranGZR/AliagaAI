"""Chat (AI) API Endpoint'i."""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.query_router import process_chat_query
from app.main import limiter

router = APIRouter()

@router.post("", response_model=ChatResponse)
@router.post("/", response_model=ChatResponse, include_in_schema=False)
@limiter.limit("5/minute")
async def chat_with_ai(request: Request, chat_request: ChatRequest, session: AsyncSession = Depends(get_db)):
    """Kullanıcının sorusunu alır, query router üzerinden işler ve AI yanıtı döner."""
    response = await process_chat_query(
        session=session, 
        user_message=chat_request.message,
        conversation_history=chat_request.conversation_history
    )
    return response
