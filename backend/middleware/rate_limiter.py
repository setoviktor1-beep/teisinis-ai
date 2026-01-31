"""
Rate Limiting Middleware
Limits API requests to 15 per minute per user
"""

from fastapi import Request, HTTPException
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List
import asyncio


class RateLimiter:
    """
    Rate limiting middleware for FastAPI
    Tracks requests per user and enforces limits
    """

    def __init__(self, max_requests: int = 15, window_seconds: int = 60):
        """
        Initialize rate limiter

        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[datetime]] = defaultdict(list)
        self.lock = asyncio.Lock()

    async def check_rate_limit(self, user_id: str, endpoint: str) -> bool:
        """
        Check if user has exceeded rate limit

        Args:
            user_id: User identifier
            endpoint: API endpoint path

        Returns:
            True if request allowed, False if rate limit exceeded
        """
        async with self.lock:
            key = f"{user_id}:{endpoint}"
            now = datetime.now()

            # Remove old requests outside the time window
            self.requests[key] = [
                ts for ts in self.requests[key]
                if now - ts < timedelta(seconds=self.window_seconds)
            ]

            # Check if limit exceeded
            if len(self.requests[key]) >= self.max_requests:
                return False

            # Add current request timestamp
            self.requests[key].append(now)
            return True

    async def get_remaining_requests(self, user_id: str, endpoint: str) -> int:
        """Get number of remaining requests in current window"""
        async with self.lock:
            key = f"{user_id}:{endpoint}"
            now = datetime.now()

            # Clean old requests
            self.requests[key] = [
                ts for ts in self.requests[key]
                if now - ts < timedelta(seconds=self.window_seconds)
            ]

            return max(0, self.max_requests - len(self.requests[key]))


# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=15, window_seconds=60)


async def rate_limit_middleware(request: Request, call_next):
    """
    FastAPI middleware function for rate limiting

    Args:
        request: FastAPI request object
        call_next: Next middleware/route handler

    Returns:
        Response or HTTPException if rate limit exceeded
    """
    # Skip rate limiting for certain endpoints
    skip_paths = ["/health", "/docs", "/openapi.json", "/redoc"]
    if request.url.path in skip_paths:
        return await call_next(request)

    # Get user ID from request state (set by auth middleware)
    user_id = getattr(request.state, "user_id", None)

    # If no user ID, use IP address as fallback
    if not user_id:
        client_host = request.client.host if request.client else "unknown"
        user_id = f"ip:{client_host}"

    endpoint = request.url.path

    # Check rate limit
    allowed = await rate_limiter.check_rate_limit(user_id, endpoint)

    if not allowed:
        # Get remaining time until window resets
        remaining = await rate_limiter.get_remaining_requests(user_id, endpoint)

        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": f"Maximum {rate_limiter.max_requests} requests per {rate_limiter.window_seconds} seconds",
                "retry_after": rate_limiter.window_seconds,
                "remaining": remaining
            }
        )

    # Add rate limit headers to response
    response = await call_next(request)

    remaining = await rate_limiter.get_remaining_requests(user_id, endpoint)
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.max_requests)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(rate_limiter.window_seconds)

    return response
