"""Database connection and session management."""

from __future__ import annotations

import logging
from typing import Dict

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _create_engine() -> Engine:
    """Create engine with runtime-specific configuration."""

    connect_args: Dict[str, object] = {}
    pool_kwargs: Dict[str, object] = {"pool_pre_ping": True}

    if settings.database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        pool_kwargs.update({"pool_size": None, "max_overflow": 0})
    else:
        pool_kwargs.update({
            "pool_size": 20,
            "max_overflow": 40,
            "pool_recycle": 3600,
        })
        connect_args.update({
            "connect_timeout": 10,
            "application_name": "euint-app",
        })

    engine = create_engine(
        settings.database_url,
        echo=settings.debug,
        **pool_kwargs,
        connect_args=connect_args,
    )

    if not settings.database_url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def receive_connect(dbapi_conn, connection_record):  # type: ignore[override]
            cursor = dbapi_conn.cursor()
            cursor.execute("SET application_name = 'euint-app'")
            cursor.execute("SET idle_in_transaction_session_timeout = 10000")
            cursor.close()

    return engine


engine: Engine = _create_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

Base = declarative_base()


def get_db():
    """Dependency to get database session."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database (create tables if they don't exist)."""

    from app.models import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_pool_status():
    """Get database connection pool status."""

    pool = engine.pool
    return {
        "size": getattr(pool, "size", lambda: 0)(),
        "checked_out": getattr(pool, "checkedout", lambda: 0)(),
        "overflow": getattr(pool, "overflow", lambda: 0)(),
        "total": getattr(pool, "size", lambda: 0)() + getattr(pool, "overflow", lambda: 0)(),
    }
