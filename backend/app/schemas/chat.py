"""Pydantic şemaları — Chat (ana AI endpoint)."""
from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Kullanıcıdan gelen soru."""
    message: str = Field(..., min_length=1, max_length=1000, description="Kullanıcının sorusu")


class SourceReference(BaseModel):
    """Yanıtta kullanılan kaynak referansı."""
    type: str               # news, place, event, pharmacy, ...
    title: Optional[str] = None
    url: Optional[str] = None
    date: Optional[str] = None


class ChatResponse(BaseModel):
    """AI yanıtı."""
    answer: str = Field(..., description="AI tarafından oluşturulan yanıt")
    intent: str = Field(..., description="Tespit edilen intent (ör. pharmacy, weather)")
    sources: list[SourceReference] = Field(default_factory=list, description="Kullanılan kaynaklar")
    search_method: str = Field(default="sql", description="Arama yöntemi: sql, rag, hybrid")
