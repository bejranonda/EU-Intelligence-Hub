"""Pytest fixtures for the backend test suite."""

from __future__ import annotations

import os
from typing import Generator

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture(scope="session")
def engine():
    database_url = os.environ.get("DATABASE_URL", "sqlite:///./test.db")

    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        pool_args = (
            {"poolclass": StaticPool} if database_url.endswith(":memory:") else {}
        )
        engine = create_engine(database_url, connect_args=connect_args, **pool_args)
    else:
        engine = create_engine(database_url)

    # Drop views first if using PostgreSQL (they depend on tables)
    if not database_url.startswith("sqlite"):
        with engine.connect() as conn:
            conn.execute(
                text("DROP VIEW IF EXISTS keyword_sentiment_summary CASCADE;")
            )
            conn.commit()

    # Create pgvector extension for PostgreSQL
    if not database_url.startswith("sqlite"):
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()

    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        # Drop views before dropping tables
        if not database_url.startswith("sqlite"):
            with engine.connect() as conn:
                conn.execute(
                    text("DROP VIEW IF EXISTS keyword_sentiment_summary CASCADE;")
                )
                conn.commit()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine) -> Generator:
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Override auth for admin endpoints in tests
    def override_get_current_admin():
        return {"username": "test_admin", "authenticated": True}

    app.dependency_overrides[get_db] = override_get_db

    # Import and override auth dependency
    from app.auth import get_current_admin
    app.dependency_overrides[get_current_admin] = override_get_current_admin

    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
