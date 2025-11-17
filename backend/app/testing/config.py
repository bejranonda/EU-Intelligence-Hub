"""Shared test configuration helpers."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Dict


TEST_ENVIRONMENT_OVERRIDES: Dict[str, str] = {
    "ENVIRONMENT": "testing",
    "DEBUG": "false",
    "KEYWORD_SCHEDULER_ENABLED": "false",
    "ENABLE_GEMINI_SENTIMENT": "false",
    "ENABLE_VADER_BASELINE": "true",
    "GEMINI_API_KEY": "",
    "DATABASE_URL": "sqlite:///./test.db",
    "REDIS_URL": "redis://localhost:6379/0",
}


@lru_cache()
def apply_test_overrides() -> None:
    """Apply default overrides for the test runtime."""

    for key, value in TEST_ENVIRONMENT_OVERRIDES.items():
        os.environ.setdefault(key, value)
