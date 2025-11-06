"""Input validation and sanitization utilities."""
import re
from typing import Optional, List
from pydantic import BaseModel, Field, validator
import logging

logger = logging.getLogger(__name__)


class PaginationParams(BaseModel):
    """Common pagination parameters."""

    skip: int = Field(0, ge=0, description="Number of items to skip")
    limit: int = Field(
        10, ge=1, le=100, description="Number of items to return (max 100)"
    )

    class Config:
        json_schema_extra = {"example": {"skip": 0, "limit": 10}}


class SearchParams(BaseModel):
    """Search query parameters with validation."""

    q: str = Field(..., min_length=1, max_length=500, description="Search query")

    @validator("q")
    def sanitize_query(cls, v):
        """Remove potentially dangerous characters."""
        # Allow alphanumeric, spaces, and common punctuation
        if not re.match(
            r'^[a-zA-Z0-9\s\-_.(),&"\']+(?: [a-zA-Z0-9\s\-_.(),&"\']+)*$', v
        ):
            raise ValueError("Search query contains invalid characters")
        return v.strip()


class FilterParams(BaseModel):
    """Common filter parameters."""

    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: str = Field("asc", regex="^(asc|desc)$", description="Sort order")

    @validator("sort_by")
    def validate_sort_field(cls, v):
        """Validate sort field name."""
        if v and not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", v):
            raise ValueError("Invalid sort field")
        return v


def validate_file_upload(
    filename: str,
    file_size: int,
    allowed_extensions: List[str],
    max_size_bytes: int = 10 * 1024 * 1024,
) -> tuple[bool, Optional[str]]:
    """
    Validate uploaded file.

    Args:
        filename: Name of the file
        file_size: Size of the file in bytes
        allowed_extensions: List of allowed file extensions
        max_size_bytes: Maximum file size in bytes

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file extension
    if not filename:
        return False, "Filename cannot be empty"

    file_ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if file_ext not in allowed_extensions:
        return (
            False,
            f"File type .{file_ext} not allowed. Allowed types: {', '.join(allowed_extensions)}",
        )

    # Check file size
    if file_size > max_size_bytes:
        max_mb = max_size_bytes / (1024 * 1024)
        return False, f"File size exceeds maximum of {max_mb}MB"

    if file_size == 0:
        return False, "File is empty"

    # Check filename for path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        return False, "Invalid filename"

    return True, None


def sanitize_input(value: str, max_length: int = 1000) -> str:
    """Sanitize user input."""
    if not isinstance(value, str):
        return str(value)

    # Strip whitespace
    value = value.strip()

    # Limit length
    if len(value) > max_length:
        value = value[:max_length]

    # Remove potentially dangerous characters
    value = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", value)

    return value


def validate_url(url: str) -> bool:
    """Validate URL format."""
    url_pattern = re.compile(
        r"^https?://"
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
        r"localhost|"
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        r"(?::\d+)?"
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    return url_pattern.match(url) is not None


def validate_email(email: str) -> bool:
    """Validate email format."""
    email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    return email_pattern.match(email) is not None
