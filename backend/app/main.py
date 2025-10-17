"""Main FastAPI application entry point."""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

from app.config import get_settings
from app.database import get_db, engine
from app.models import models

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="European News Intelligence Hub API",
    description="AI-powered news aggregation and sentiment analysis platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS - Limit origins to only necessary domains
cors_origins = [
    "http://localhost:3000",
    "http://frontend:3000"
]

# Allow additional origins in development
if settings.environment == "development":
    cors_origins.extend([
        "http://192.168.178.50:3000",
        "http://192.168.178.70:3000"
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Explicitly allowed methods
    allow_headers=["Content-Type", "Authorization", "Accept"],  # Explicitly allowed headers
)

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup."""
    logger.info("Starting European News Intelligence Hub API...")
    logger.info(f"Environment: {settings.environment}")

    # Create tables if they don't exist
    try:
        models.Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down European News Intelligence Hub API...")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "European News Intelligence Hub API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
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
        "environment": settings.environment
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
            "mind_map_visualization": True
        }
    }


# Import and include routers
from app.api import keywords, search, sentiment, documents, suggestions, admin

app.include_router(keywords.router, prefix="/api/keywords", tags=["keywords"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(sentiment.router, prefix="/api/sentiment", tags=["sentiment"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(suggestions.router, prefix="/api/suggestions", tags=["suggestions"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
