"""Database connection and session management."""
from sqlalchemy import create_engine, event, pool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)

settings = get_settings()

# Create SQLAlchemy engine with optimized connection pooling
engine = create_engine(
    settings.database_url,
    poolclass=pool.QueuePool,
    pool_size=20,  # Number of connections to keep in pool
    max_overflow=40,  # Maximum overflow connections
    pool_pre_ping=True,  # Test connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
    connect_args={
        "connect_timeout": 10,
        "application_name": "euint-app"
    },
    echo=settings.debug,
    echo_pool=settings.debug
)


# Event listeners for connection pooling
@event.listens_for(pool.Pool, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Configure new database connections."""
    cursor = dbapi_conn.cursor()
    # Enable useful PostgreSQL features
    cursor.execute("SET application_name = 'euint-app'")
    cursor.execute("SET idle_in_transaction_session_timeout = 10000")  # 10 second idle timeout
    cursor.close()


@event.listens_for(pool.Pool, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Log connection checkout."""
    logger.debug("Checked out database connection")


@event.listens_for(pool.Pool, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    """Log connection check-in."""
    logger.debug("Checked in database connection")


@event.listens_for(pool.Pool, "detach")
def receive_detach(dbapi_conn, connection_record):
    """Log connection detach."""
    logger.debug("Detached database connection")


# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Better for read-heavy operations
)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database (create tables if they don't exist)."""
    # Import all models to ensure they're registered
    from app.models import models  # noqa: F401
    Base.metadata.create_all(bind=engine)


def get_pool_status():
    """Get database connection pool status."""
    pool = engine.pool
    return {
        "size": pool.size(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "total": pool.size() + pool.overflow()
    }
