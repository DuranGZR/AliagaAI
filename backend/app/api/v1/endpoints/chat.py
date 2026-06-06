"""Chat (AI) API Endpoint'i — Agentic RAG."""
from functools import lru_cache

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agent.service import AgenticRAGService
from app.core.limiter import limiter
from app.core.auth import verify_api_key

router = APIRouter()


@lru_cache()
def get_agent_service() -> AgenticRAGService:
    """AgenticRAGService singleton — lazy init, test edilebilir."""
    return AgenticRAGService()


@router.post("", response_model=ChatResponse)
@limiter.limit("5/minute")
async def chat_with_ai(
    request: Request,
    chat_request: ChatRequest,
    session: AsyncSession = Depends(get_db),
    api_key: str | None = Depends(verify_api_key),
    agent: AgenticRAGService = Depends(get_agent_service),
):
    """Kullanıcının sorusunu alır, Agentic RAG servisi üzerinden işler
    ve AI yanıtı döner."""
    response = await agent.run(
        session=session,
        user_message=chat_request.message,
        conversation_history=chat_request.conversation_history,
    )
    return response
