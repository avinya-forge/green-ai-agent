from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import time
from typing import Dict, List

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.
    Tracks request timestamps per IP address.
    """
    def __init__(self, app, limit: int = 100, window: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window = window
        # Dictionary to store request timestamps: {ip: [timestamp1, timestamp2, ...]}
        self._requests: Dict[str, List[float]] = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Initialize if new IP
        if client_ip not in self._requests:
            self._requests[client_ip] = []

        # Filter out timestamps older than window
        # We only filter when a new request comes in to avoid background tasks
        timestamps = self._requests[client_ip]
        valid_timestamps = [t for t in timestamps if now - t < self.window]
        self._requests[client_ip] = valid_timestamps

        # Check if limit exceeded
        if len(valid_timestamps) >= self.limit:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too Many Requests",
                    "limit": self.limit,
                    "window_seconds": self.window
                },
                headers={"Retry-After": str(self.window)}
            )

        # Record current request
        self._requests[client_ip].append(now)

        # Periodic cleanup of empty keys (simple strategy: if dict gets too big)
        if len(self._requests) > 1000:
            self._cleanup_stale_ips(now)

        return await call_next(request)

    def _cleanup_stale_ips(self, now: float):
        """Remove IPs that have no valid requests in the window."""
        keys_to_remove = []
        for ip, timestamps in self._requests.items():
            if not any(now - t < self.window for t in timestamps):
                keys_to_remove.append(ip)

        for ip in keys_to_remove:
            del self._requests[ip]
