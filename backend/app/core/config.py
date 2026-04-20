from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "AliağaAI"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # LLM & AI
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Embedding
    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-small"
    EMBEDDING_DIM: int = 384

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
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
