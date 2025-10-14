"""Celery application configuration."""
from celery import Celery
from celery.schedules import crontab
from app.config import get_settings

settings = get_settings()

# Create Celery app
celery_app = Celery(
    "euint",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    worker_prefetch_multiplier=1,
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    'scrape-news-hourly': {
        'task': 'app.tasks.scraping.scrape_news',
        'schedule': crontab(minute=0),  # Every hour at :00
    },
    'aggregate-sentiment-daily': {
        'task': 'app.tasks.sentiment_aggregation.aggregate_daily_sentiment',
        'schedule': crontab(hour=0, minute=30),  # Daily at 00:30 UTC
    },
}

# Import tasks to register them
from app.tasks import scraping, sentiment_aggregation  # noqa: F401
