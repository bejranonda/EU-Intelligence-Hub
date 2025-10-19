"""Pytest configuration importing shared fixtures."""

from app.testing.fixtures import client, db_session, engine  # noqa: F401
