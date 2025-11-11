"""Rate limiting middleware for API endpoints."""

import time
from typing import Callable, Dict, Tuple
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum number of requests allowed
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = {}

    def is_allowed(self, client_id: str) -> bool:
        """Check if client is allowed to make a request."""
        now = time.time()

        if client_id not in self.requests:
            self.requests[client_id] = []

        # Remove old requests outside the window
        self.requests[client_id] = [
            req_time
            for req_time in self.requests[client_id]
            if now - req_time < self.window_seconds
        ]

        if len(self.requests[client_id]) < self.max_requests:
            self.requests[client_id].append(now)
            return True

        return False

    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests for client."""
        now = time.time()

        if client_id not in self.requests:
            return self.max_requests

        # Remove old requests
        self.requests[client_id] = [
            req_time
            for req_time in self.requests[client_id]
            if now - req_time < self.window_seconds
        ]

        return max(0, self.max_requests - len(self.requests[client_id]))


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce rate limiting."""

    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.rate_limiter = RateLimiter(max_requests, window_seconds)

    async def dispatch(self, request: Request, call_next: Callable):
        """Process request with rate limiting."""
        client_ip = request.client.host if request.client else "unknown"

        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/health", "/metrics"]:
            return await call_next(request)

        if not self.rate_limiter.is_allowed(client_ip):
            remaining = self.rate_limiter.get_remaining(client_ip)
            logger.warning(f"Rate limit exceeded for client {client_ip}")

            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests",
                    "retry_after": self.rate_limiter.window_seconds,
                },
                headers={
                    "Retry-After": str(self.rate_limiter.window_seconds),
                    "X-RateLimit-Limit": str(self.rate_limiter.max_requests),
                    "X-RateLimit-Remaining": str(remaining),
                },
            )

        response = await call_next(request)

        # Add rate limit headers
        remaining = self.rate_limiter.get_remaining(client_ip)
        response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(
            int(time.time()) + self.rate_limiter.window_seconds
        )

        return response
