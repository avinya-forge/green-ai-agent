from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"

        # CSP: Allow self, data (for charts), and CDN for Chart.js
        # We need 'unsafe-inline' and 'unsafe-eval' because Chart.js and some inline scripts are used in templates.
        # Ideally we should move to nonces/hashes but for now this is an improvement.
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' https: data:;"
        )
        response.headers["Content-Security-Policy"] = csp

        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # HSTS (only effective if served over HTTPS)
        if request.url.scheme == "https":
             response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
