"""Application configuration using Pydantic settings."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    # Redis
    redis_url: str
    redis_host: str = "redis"
    redis_port: int = 6379

    # API Keys
    gemini_api_key: str

    # Admin
    admin_username: str = "admin"
    admin_password: str

    # Application
    secret_key: str
    environment: str = "development"
    debug: bool = True

    # Celery
    celery_broker_url: str
    celery_result_backend: str

    # Scraping
    scraping_interval_hours: int = 1
    max_articles_per_source: int = 50

    # Sentiment Analysis
    sentiment_confidence_threshold: float = 0.5
    enable_vader_baseline: bool = True
    enable_gemini_sentiment: bool = True

    # Rate Limiting
    rate_limit_per_minute: int = 60
    gemini_rate_limit_per_minute: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
