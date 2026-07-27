import time
import asyncio
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._store = defaultdict(list)
        self._lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return await call_next(request)

        key = auth_header[7:]
        now = time.time()

        async with self._lock:
            timestamps = self._store[key]
            cutoff = now - self.window_seconds
            self._store[key] = [t for t in timestamps if t > cutoff]

            if len(self._store[key]) >= self.max_requests:
                return JSONResponse(
                    status_code=429,
                    content={"error": "Rate limit exceeded"},
                )

            self._store[key].append(now)

        return await call_next(request)