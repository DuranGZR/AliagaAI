from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "AliağaAI"
    app_version: str = "2.0.0"
    debug: bool = Field(default=False, alias="DEBUG")
    env: str = Field(default="development", alias="ENV")

    database_url: str = Field(
        default="postgresql+asyncpg://aliagai:aliagai_secret@localhost:5432/aliagai_db",
        alias="DATABASE_URL",
    )
    db_echo: bool = False
    db_pool_size: int = 20
    db_max_overflow: int = 10

    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.3-70b-versatile", alias="GROQ_MODEL")
    groq_temperature: float = 0.1
    groq_max_tokens: int = 1024

    embedding_model: str = Field(
        default="intfloat/multilingual-e5-small",
        alias="EMBEDDING_MODEL",
    )
    embedding_dimension: int = 384

    rag_top_k: int = 5
    rag_similarity_threshold: float = 0.3
    rag_chunk_size: int = 512
    rag_chunk_overlap: int = 50

    scrape_timeout: int = 30
    user_agent: str = "AliagaAI/2.0 (Educational Project)"
    belediye_base_url: str = "https://www.aliaga.bel.tr"

    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = ["*"]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()
