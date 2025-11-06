"""Database type adapters supporting PostgreSQL and SQLite runtimes."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import JSON
from sqlalchemy.sql.type_api import TypeEngine
from sqlalchemy.types import TypeDecorator


class JSONBType(TypeDecorator):
    """JSON type that maps to JSONB on PostgreSQL and JSON elsewhere."""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect) -> TypeEngine[Any]:  # type: ignore[override]
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import JSONB  # Lazy import

            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(JSON())


class ArrayType(TypeDecorator):
    """Array type backed by JSON when native arrays are unavailable."""

    impl = JSON
    cache_ok = True

    def __init__(
        self, item_type: Optional[TypeEngine[Any]] = None, *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.item_type = item_type

    def load_dialect_impl(self, dialect) -> TypeEngine[Any]:  # type: ignore[override]
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import ARRAY  # Lazy import

            return dialect.type_descriptor(ARRAY(self.item_type or JSON()))
        return dialect.type_descriptor(JSON())


class VectorType(TypeDecorator):
    """Vector embedding type with JSON fallback for non-PostgreSQL engines."""

    impl = JSON
    cache_ok = True

    def __init__(self, dims: int, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.dims = dims

    def load_dialect_impl(self, dialect) -> TypeEngine[Any]:  # type: ignore[override]
        if dialect.name == "postgresql":
            from pgvector.sqlalchemy import Vector  # Lazy import

            return dialect.type_descriptor(Vector(self.dims))
        return dialect.type_descriptor(JSON())
