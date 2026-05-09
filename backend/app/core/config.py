from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "AliağaAI"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:19006",
        "http://localhost:19000",
        "http://localhost:8081",
    ]

    # LLM & AI
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Embedding
    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-small"
    EMBEDDING_DIM: int = 384
    EMBEDDING_BATCH_SIZE: int = 16
    EMBEDDING_RETRY_COOLDOWN_SEC: int = 60

    # RAG
    RAG_TOP_K: int = 8
    RAG_MIN_SIMILARITY: float = 0.35
    RAG_VECTOR_CANDIDATES: int = 50
    RAG_LEXICAL_CANDIDATES: int = 50
    RAG_VECTOR_WEIGHT: float = 0.70
    RAG_LEXICAL_WEIGHT: float = 0.30
    RAG_RERANK_ENABLED: bool = True
    RAG_RERANK_TOP_N: int = 16
    RAG_QUERY_EXPANSION_ENABLED: bool = True
    RAG_MAX_QUERY_VARIANTS: int = 4
    RAG_SHORT_QUERY_MIN_SIMILARITY: float = 0.28
    RAG_MEDIUM_QUERY_MIN_SIMILARITY: float = 0.30
    RAG_LEXICAL_RESCUE_SCORE: float = 0.40
    RAG_QUERY_EMBED_TIMEOUT_SEC: float = 20.0
    RAG_MIN_EVIDENCE_CONFIDENCE: float = 0.20
    RAG_MIN_EVIDENCE_CHUNKS: int = 1
    RAG_ENABLE_CONTROLLED_AUGMENTATION: bool = True
    RAG_ENABLE_MODEL_ONLY_FALLBACK: bool = True
    RAG_MODEL_ONLY_BASE_CONFIDENCE: float = 0.35
    RAG_AUGMENTATION_MIN_EVIDENCE: float = 0.45
    RAG_PARALLEL_RETRIEVAL_ENABLED: bool = True
    RAG_SKIP_VECTOR_WHEN_SQL_HIT: bool = True
    PERSONA_ENABLED: bool = True
    PERSONA_TEMPERATURE: float = 0.20

    # Chunking
    CHUNK_SIZE: int = 900
    CHUNK_OVERLAP: int = 120
    CHUNK_MIN_LENGTH: int = 80

    # Database — .env'deki sync URL'yi asyncpg'ye çeviriyoruz
    DATABASE_URL: str = "postgresql://user:pass@localhost/dbname"

    @property
    def async_database_url(self) -> str:
        """Supabase sync URL'yi SQLAlchemy asyncpg formatına dönüştürür."""
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    # CollectAPI
    COLLECTAPI_KEY: str = ""

    # Scraper
    SCRAPE_TIMEOUT: int = 30
    USER_AGENT: str = "AliagaAI/1.0 (Educational Project)"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    STARTUP_BACKGROUND_JOBS_ENABLED: bool = True
    STARTUP_EMBEDDING_WARMUP_ENABLED: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
