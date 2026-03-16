from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./aliaga.db"
    
    # AI - Groq
    groq_api_key: str = ""
    
    # Scraper
    scrape_timeout: int = 30
    user_agent: str = "AliagaAI/1.0 (Educational Project)"
    belediye_base_url: str = "https://www.aliaga.bel.tr"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
