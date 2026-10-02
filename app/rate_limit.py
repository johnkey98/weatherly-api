"""Sliding-window rate limiter (per client IP, in memory)."""

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

from .config import settings


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: float = 60.0):
        self.max = max_requests
        self.window = window_seconds
        self._hits: dict[str, deque] = defaultdict(deque)

    def check(self, request: Request) -> None:
        client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
        now = time.time()
        window_hits = self._hits[client_ip]

        # Drop entries outside the current window
        while window_hits and window_hits[0] < now - self.window:
            window_hits.popleft()

        if len(window_hits) >= self.max:
            retry_after = int(self.window - (now - window_hits[0])) + 1
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded ({self.max} req/min). Retry in {retry_after}s.",
                headers={"Retry-After": str(retry_after)},
            )

        window_hits.append(now)

    def reset(self) -> None:
        self._hits.clear()


limiter = RateLimiter(settings.rate_limit_per_minute)
