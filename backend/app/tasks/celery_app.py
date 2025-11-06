"""Celery application configuration."""
from celery import Celery
from celery.schedules import crontab
from app.config import get_settings

settings = get_settings()

# Create Celery app
celery_app = Celery(
    "euint", broker=settings.celery_broker_url, backend=settings.celery_result_backend
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    worker_prefetch_multiplier=1,
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    "scrape-news-hourly": {
        "task": "app.tasks.scraping.scrape_news",
        "schedule": crontab(minute=0),  # Every hour at :00
    },
    "aggregate-sentiment-daily": {
        "task": "app.tasks.sentiment_aggregation.aggregate_daily_sentiment",
        "schedule": crontab(hour=0, minute=30),  # Daily at 00:30 UTC
    },
    "process-keyword-suggestions": {
        "task": "app.tasks.keyword_management.process_pending_suggestions",
        "schedule": crontab(hour=2, minute=0),  # Daily at 02:00 UTC
    },
    "review-keyword-performance": {
        "task": "app.tasks.keyword_management.review_keyword_performance",
        "schedule": crontab(
            hour=3, minute=0, day_of_week=1
        ),  # Weekly on Monday at 03:00 UTC
    },
    "daily-database-backup": {
        "task": "app.tasks.backup_tasks.daily_database_backup",
        "schedule": crontab(hour=1, minute=0),  # Daily at 01:00 UTC
    },
    "cleanup-old-backups": {
        "task": "app.tasks.backup_tasks.cleanup_old_backups",
        "schedule": crontab(hour=4, minute=0),  # Daily at 04:00 UTC
        "kwargs": {"retention_days": 7},
    },
    "database-health-check": {
        "task": "app.tasks.backup_tasks.database_health_check",
        "schedule": crontab(minute=0),  # Every hour
    },
    "populate-keyword-queue": {
        "task": "app.tasks.keyword_search.populate_keyword_queue",
        "schedule": crontab(minute="*/30"),  # Every 30 minutes
    },
    "process-keyword-queue": {
        "task": "app.tasks.keyword_search.process_keyword_queue",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
    },
}

# Import tasks to register them
from app.tasks import (
    scraping,
    sentiment_aggregation,
    keyword_management,
    keyword_search,
    backup_tasks,
)  # noqa: F401
