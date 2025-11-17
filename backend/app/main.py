"""Main FastAPI application entry point."""

from fastapi import FastAPI, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import time
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import get_db, engine
from app.models import models
from app.monitoring import setup_logging, get_logger, get_metrics
from app.monitoring.metrics import (
    app_info,
    uptime_seconds,
    errors_total,
    exceptions_total,
)
from app.middleware import RateLimitMiddleware, SecurityHeadersMiddleware

# Configure structured logging
settings_obj = get_settings()
setup_logging(environment=settings_obj.environment)
logger = get_logger(__name__)

# Track application startup time
_startup_time = time.time()

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="European News Intelligence Hub API",
    description="AI-powered news aggregation and sentiment analysis platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/openapi.json",
)

# Configure CORS - Limit origins to only necessary domains
cors_origins = ["http://localhost:3000", "http://frontend:3000"]

# Allow additional origins in development
if settings.environment == "development":
    cors_origins.extend(["http://192.168.178.50:3000", "http://192.168.178.70:3000"])

# Add middleware in reverse order of execution
# Security headers should be added first (executed last)
app.add_middleware(SecurityHeadersMiddleware)

# Rate limiting middleware - skip in testing environment to avoid test failures
if settings.environment not in ("testing", "test"):
    app.add_middleware(RateLimitMiddleware, max_requests=60, window_seconds=60)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
    max_age=3600,
)


# Create tables on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup."""
    logger.info("Starting European News Intelligence Hub API...")
    logger.info(f"Environment: {settings.environment}")

    # Initialize metrics
    app_info.labels(version="1.0.0", environment=settings.environment).set(1)

    # Create tables if they don't exist
    try:
        models.Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down European News Intelligence Hub API...")


@app.middleware("http")
async def add_metrics_middleware(request, call_next):
    """Middleware to track HTTP request metrics."""
    start_time = time.time()
    method = request.method
    path = request.url.path

    try:
        response = await call_next(request)
        duration = time.time() - start_time

        # Update uptime metric
        uptime_seconds.set(time.time() - _startup_time)

        return response
    except Exception as e:
        duration = time.time() - start_time
        exceptions_total.labels(exception_type=type(e).__name__).inc()
        logger.error(f"Request error: {method} {path} - {str(e)}", exc_info=True)
        raise


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "European News Intelligence Hub API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.

    Returns:
        dict: Health status including database connectivity
    """
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "environment": settings.environment,
    }


@app.get("/api/status")
async def api_status():
    """
    API status endpoint with more detailed information.

    Returns:
        dict: Detailed API status
    """
    return {
        "api_version": "1.0.0",
        "environment": settings.environment,
        "features": {
            "sentiment_analysis": True,
            "semantic_search": True,
            "news_scraping": True,
            "document_upload": True,
            "keyword_suggestions": True,
            "mind_map_visualization": True,
        },
    }


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """
    Prometheus metrics endpoint.

    Returns:
        PlainTextResponse: Prometheus-formatted metrics
    """
    return get_metrics()


@app.get("/api/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check with system information.

    Returns:
        dict: Detailed health status
    """
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"

    uptime = time.time() - _startup_time

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "environment": settings.environment,
        "uptime_seconds": uptime,
        "version": "1.0.0",
    }


# Import and include routers
from app.api import (
    keywords,
    search,
    sentiment,
    documents,
    suggestions,
    admin,
    admin_evaluations,
)

app.include_router(keywords.router, prefix="/api/keywords", tags=["keywords"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(sentiment.router, prefix="/api/sentiment", tags=["sentiment"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(suggestions.router, prefix="/api/suggestions", tags=["suggestions"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(admin_evaluations.router, prefix="/admin", tags=["admin"])
