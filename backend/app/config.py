"""Application configuration using Pydantic settings."""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.testing.config import apply_test_overrides

# Ensure deterministic defaults for test/runtime environments
apply_test_overrides()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = Field(
        default="sqlite:///./app.db", validation_alias="DATABASE_URL"
    )
    postgres_user: str = ""
    postgres_password: str = ""
    postgres_db: str = ""
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    # Redis
    redis_url: str = "redis://redis:6379/0"
    redis_host: str = "redis"
    redis_port: int = 6379

    # API Keys
    gemini_api_key: str = ""

    # Admin
    admin_username: str = Field(default="admin", validation_alias="ADMIN_USERNAME")
    admin_password: str = Field(default="admin", validation_alias="ADMIN_PASSWORD")

    # Application
    secret_key: str = "change_me"
    environment: str = "development"
    debug: bool = True

    # Celery
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/0"

    # Scraping
    scraping_interval_hours: int = 1
    max_articles_per_source: int = 50
    enable_source_expansion: bool = False

    # Sentiment Analysis
    sentiment_confidence_threshold: float = 0.5
    enable_vader_baseline: bool = True
    enable_gemini_sentiment: bool = False

    # Rate Limiting
    rate_limit_per_minute: int = 60
    gemini_rate_limit_per_minute: int = 30

    # Keyword search throttling
    keyword_scheduler_enabled: bool = False
    keyword_search_cooldown_minutes: int = 180
    keyword_daily_search_cap: int = 250
    keyword_scheduler_batch_size: int = 15
    keyword_scheduler_min_priority: int = 0
    keyword_scheduler_retry_minutes: int = 30

    # Optional external services
    sentry_dsn: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="allow",
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""

    return Settings()  # type: ignore[call-arg]
