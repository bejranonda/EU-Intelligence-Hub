"""Prometheus metrics collection and monitoring."""

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    CollectorRegistry,
    generate_latest,
)
import time
from functools import wraps
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)

# Create a custom registry for application metrics
registry = CollectorRegistry()

# HTTP Metrics
http_request_duration = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint", "status"],
    registry=registry,
)

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
    registry=registry,
)

http_request_size = Histogram(
    "http_request_size_bytes",
    "HTTP request size in bytes",
    ["method", "endpoint"],
    registry=registry,
)

http_response_size = Histogram(
    "http_response_size_bytes",
    "HTTP response size in bytes",
    ["method", "endpoint", "status"],
    registry=registry,
)

# Database Metrics
db_query_duration = Histogram(
    "db_query_duration_seconds",
    "Database query duration in seconds",
    ["query_type", "table"],
    registry=registry,
)

db_connection_pool_size = Gauge(
    "db_connection_pool_size",
    "Current database connection pool size",
    registry=registry,
)

db_active_connections = Gauge(
    "db_active_connections", "Active database connections", registry=registry
)

# Cache Metrics
cache_hits = Counter(
    "cache_hits_total", "Total cache hits", ["cache_name"], registry=registry
)

cache_misses = Counter(
    "cache_misses_total", "Total cache misses", ["cache_name"], registry=registry
)

cache_size = Gauge(
    "cache_size_bytes", "Current cache size in bytes", ["cache_name"], registry=registry
)

# Business Logic Metrics
keyword_searches_total = Counter(
    "keyword_searches_total",
    "Total keyword searches performed",
    ["search_type"],
    registry=registry,
)

semantic_searches_total = Counter(
    "semantic_searches_total",
    "Total semantic searches performed",
    ["language"],
    registry=registry,
)

sentiment_analyses_total = Counter(
    "sentiment_analyses_total", "Total sentiment analyses performed", registry=registry
)

documents_uploaded_total = Counter(
    "documents_uploaded_total",
    "Total documents uploaded",
    ["file_type"],
    registry=registry,
)

# Background Task Metrics
celery_task_duration = Histogram(
    "celery_task_duration_seconds",
    "Celery task execution time in seconds",
    ["task_name", "status"],
    registry=registry,
)

celery_tasks_total = Counter(
    "celery_tasks_total",
    "Total Celery tasks executed",
    ["task_name", "status"],
    registry=registry,
)

celery_queue_size = Gauge(
    "celery_queue_size", "Current Celery queue size", ["queue_name"], registry=registry
)

# Error Metrics
errors_total = Counter(
    "errors_total",
    "Total errors occurred",
    ["error_type", "endpoint"],
    registry=registry,
)

exceptions_total = Counter(
    "exceptions_total", "Total exceptions caught", ["exception_type"], registry=registry
)

# System Metrics
app_info = Gauge(
    "app_info", "Application info", ["version", "environment"], registry=registry
)

uptime_seconds = Gauge(
    "uptime_seconds", "Application uptime in seconds", registry=registry
)


def track_http_request(func: Callable) -> Callable:
    """Decorator to track HTTP request metrics."""

    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        method = kwargs.get("method", "UNKNOWN")
        endpoint = kwargs.get("endpoint", "unknown")
        start_time = time.time()

        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            status = getattr(result, "status_code", 200)

            http_request_duration.labels(method, endpoint, status).observe(duration)
            http_requests_total.labels(method, endpoint, status).inc()

            return result
        except Exception as e:
            duration = time.time() - start_time
            http_request_duration.labels(method, endpoint, "error").observe(duration)
            http_requests_total.labels(method, endpoint, "error").inc()
            exceptions_total.labels(type(e).__name__).inc()
            raise

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        method = kwargs.get("method", "UNKNOWN")
        endpoint = kwargs.get("endpoint", "unknown")
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            status = getattr(result, "status_code", 200)

            http_request_duration.labels(method, endpoint, status).observe(duration)
            http_requests_total.labels(method, endpoint, status).inc()

            return result
        except Exception as e:
            duration = time.time() - start_time
            http_request_duration.labels(method, endpoint, "error").observe(duration)
            http_requests_total.labels(method, endpoint, "error").inc()
            exceptions_total.labels(type(e).__name__).inc()
            raise

    # Return async or sync wrapper based on function type
    if hasattr(func, "__code__") and "async" in func.__code__.co_names:
        return async_wrapper
    return sync_wrapper


def track_db_query(query_type: str, table: str):
    """Decorator to track database query metrics."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                db_query_duration.labels(query_type, table).observe(duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                db_query_duration.labels(query_type, table).observe(duration)
                raise

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                db_query_duration.labels(query_type, table).observe(duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                db_query_duration.labels(query_type, table).observe(duration)
                raise

        if hasattr(func, "__code__") and "async" in func.__code__.co_names:
            return async_wrapper
        return sync_wrapper

    return decorator


def track_celery_task(task_name: str):
    """Decorator to track Celery task metrics."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                celery_task_duration.labels(task_name, "success").observe(duration)
                celery_tasks_total.labels(task_name, "success").inc()
                return result
            except Exception as e:
                duration = time.time() - start_time
                celery_task_duration.labels(task_name, "failure").observe(duration)
                celery_tasks_total.labels(task_name, "failure").inc()
                raise

        return wrapper

    return decorator


def get_metrics() -> bytes:
    """Get Prometheus metrics in text format."""
    return generate_latest(registry)
