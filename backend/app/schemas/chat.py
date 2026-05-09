"""Pydantic schemas - Chat endpoint."""
from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming user question."""

    message: str = Field(..., min_length=1, max_length=1000, description="User question")
    conversation_history: Optional[list[dict[str, str]]] = Field(
        default_factory=list,
        description="List of previous messages in the format [{'role': 'user'|'assistant', 'content': '...'}]"
    )


class SourceReference(BaseModel):
    """Source references used in the answer."""

    type: str
    title: Optional[str] = None
    url: Optional[str] = None
    date: Optional[str] = None


class ChatResponse(BaseModel):
    """Assistant response payload."""

    answer: str = Field(..., description="Assistant answer text")
    intent: str = Field(..., description="Detected intent")
    sources: list[SourceReference] = Field(default_factory=list, description="Used sources")
    search_method: str = Field(default="sql", description="Retrieval method: sql, rag, hybrid, llm_only")
    response_policy: str = Field(
        default="grounded_rag",
        description=(
            "Response policy: greeting, sql_only, grounded_rag, grounded_rag_strict, "
            "grounded_plus_model, model_only_fallback, no_answer"
        ),
    )
    confidence: float = Field(default=0.0, description="0-1 confidence score")
    persona_profile: str = Field(default="default", description="Applied persona style profile")
    follow_up_suggestions: list[str] = Field(
        default_factory=list,
        description="Suggested follow-up prompts",
    )
