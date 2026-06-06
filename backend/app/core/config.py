from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "AliağaAI"
    VERSION: str = "3.0.0"
    API_V1_STR: str = "/api/v1"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:19006",
        "http://localhost:19000",
        "http://localhost:8081",
    ]

    # ── LLM & AI ─────────────────────────────────────────────────────
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    LLM_DEFAULT_MAX_TOKENS: int = 2048
    LLM_MAX_RETRIES: int = 2

    # ── Ajan (Agentic RAG) ───────────────────────────────────────────
    AGENT_MAX_TOKENS: int = 3000
    AGENT_TEMPERATURE: float = 0.35
    AGENT_MAX_TOOL_ROUNDS: int = 3

    # ── Embedding ────────────────────────────────────────────────────
    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-small"
    EMBEDDING_DIM: int = 384
    EMBEDDING_BATCH_SIZE: int = 16
    EMBEDDING_RETRY_COOLDOWN_SEC: int = 60

    # ── RAG Retrieval (search_similar_chunks tarafından kullanılır) ──
    RAG_TOP_K: int = 10
    RAG_MIN_SIMILARITY: float = 0.35
    RAG_VECTOR_CANDIDATES: int = 60
    RAG_LEXICAL_CANDIDATES: int = 60
    RAG_VECTOR_WEIGHT: float = 0.70
    RAG_LEXICAL_WEIGHT: float = 0.30
    RAG_RERANK_ENABLED: bool = True
    RAG_RERANK_TOP_N: int = 20
    RAG_QUERY_EXPANSION_ENABLED: bool = True
    RAG_MAX_QUERY_VARIANTS: int = 4
    RAG_SHORT_QUERY_MIN_SIMILARITY: float = 0.28
    RAG_MEDIUM_QUERY_MIN_SIMILARITY: float = 0.30
    RAG_LEXICAL_RESCUE_SCORE: float = 0.40
    RAG_QUERY_EMBED_TIMEOUT_SEC: float = 20.0

    # ── Chunking ─────────────────────────────────────────────────────
    CHUNK_SIZE: int = 900
    CHUNK_OVERLAP: int = 120
    CHUNK_MIN_LENGTH: int = 80

    # ── Database ─────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql://user:pass@localhost/dbname"

    @property
    def async_database_url(self) -> str:
        """Supabase sync URL'yi SQLAlchemy asyncpg formatına dönüştürür."""
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    # ── CollectAPI ───────────────────────────────────────────────────
    COLLECTAPI_KEY: str = ""

    # ── Scraper ──────────────────────────────────────────────────────
    SCRAPE_TIMEOUT: int = 30
    USER_AGENT: str = "AliagaAI/1.0 (Educational Project)"

    # ── Auth ────────────────────────────────────────────────────────
    API_KEY: str = ""
    AUTH_ENABLED: bool = True
    JWT_SECRET: str = "aliaga_ai_super_secret_jwt_key_2026_please_change"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 gün
    GOOGLE_CLIENT_ID: str = ""


    # ── Server ───────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    STARTUP_SEED_RAG_CHUNKS_ENABLED: bool = True
    STARTUP_BACKGROUND_JOBS_ENABLED: bool = True
    STARTUP_EMBEDDING_WARMUP_ENABLED: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
