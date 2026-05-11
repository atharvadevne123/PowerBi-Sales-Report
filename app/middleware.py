"""Custom FastAPI middleware for rate limiting and request logging."""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# In-memory request counter: ip -> (window_start, count)
_rate_counters: dict[str, tuple[float, int]] = defaultdict(lambda: (0.0, 0))
_RATE_LIMIT = 120
_WINDOW_SECONDS = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests exceeding _RATE_LIMIT per _WINDOW_SECONDS per IP."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """Check rate limit and pass through or return 429."""
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start, count = _rate_counters[client_ip]

        if now - window_start > _WINDOW_SECONDS:
            _rate_counters[client_ip] = (now, 1)
        else:
            count += 1
            _rate_counters[client_ip] = (window_start, count)
            if count > _RATE_LIMIT:
                logger.warning("Rate limit exceeded for %s", client_ip)
                return Response(
                    content='{"detail":"Rate limit exceeded. Try again in a minute."}',
                    status_code=429,
                    media_type="application/json",
                )

        return await call_next(request)
