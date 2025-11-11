"""Structured logging configuration for production environments."""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict


class JsonFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id

        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms

        return json.dumps(log_data)


class ContextualFilter(logging.Filter):
    """Add contextual information to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        return True


def setup_logging(environment: str = "development", level: str = "INFO") -> None:
    """Configure logging for the application.

    Args:
        environment: Application environment (development, staging, production)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    if environment == "production":
        # Use JSON formatting in production
        formatter = JsonFormatter()
    else:
        # Use readable format in development
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Add contextual filter
    root_logger.addFilter(ContextualFilter())

    # Set specific logger levels for noisy libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("alembic").setLevel(logging.WARNING)

    # Application loggers
    for logger_name in (
        "app",
        "app.api",
        "app.services",
        "app.tasks",
        "app.monitoring",
    ):
        logging.getLogger(logger_name).setLevel(log_level)


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    return logging.getLogger(name)
