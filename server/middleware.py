"""Hopper Ops — Security middleware (CSRF, rate limiting, security headers)"""

import hashlib
import logging
import secrets
import time
from collections import defaultdict

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("hopper-ops.middleware")


# ---------------------------------------------------------------------------
# CSRF Protection (double-submit cookie)
# ---------------------------------------------------------------------------
class CSRFMiddleware(BaseHTTPMiddleware):
    """Double-submit cookie CSRF protection.

    Sets XSRF-TOKEN cookie on GET responses. State-changing methods (POST,
    PATCH, PUT, DELETE) must include X-CSRF-Token header matching the cookie.

    Exempt paths: /auth/* (OAuth flow), /api/health, /api/brief/text (n8n).
    """

    SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
    EXEMPT_PREFIXES = ("/auth/", "/api/health", "/api/brief/text")

    async def dispatch(self, request: Request, call_next):
        method = request.method

        if method not in self.SAFE_METHODS and not self._is_exempt(request.url.path):
            cookie_token = request.cookies.get("XSRF-TOKEN", "")
            header_token = request.headers.get("X-CSRF-Token", "")

            if not cookie_token or not header_token or cookie_token != header_token:
                logger.warning("CSRF check failed: %s %s", method, request.url.path)
                return JSONResponse(
                    {"detail": "CSRF token missing or invalid"},
                    status_code=403,
                )

        response = await call_next(request)

        # Set CSRF cookie on every response so client always has a fresh token
        if "XSRF-TOKEN" not in request.cookies:
            token = secrets.token_hex(32)
            response.set_cookie(
                "XSRF-TOKEN",
                token,
                httponly=False,  # JS must read this
                samesite="strict",
                secure=request.url.scheme == "https",
                path="/",
            )

        return response

    @staticmethod
    def _is_exempt(path: str) -> bool:
        return any(path.startswith(p) for p in CSRFMiddleware.EXEMPT_PREFIXES)


# ---------------------------------------------------------------------------
# Rate Limiting (in-memory sliding window)
# ---------------------------------------------------------------------------
class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-IP sliding window rate limiter.

    Configurable limits per path prefix.
    Default: 100 requests per 60 seconds for API routes.
    Tighter limits for auth and refresh endpoints.
    """

    def __init__(self, app):
        super().__init__(app)
        # {path_prefix: (max_requests, window_seconds)}
        self.limits = {
            "/auth/": (20, 900),        # 20 per 15 min
            "/api/refresh": (10, 60),   # 10 per minute
        }
        self.default_limit = (100, 60)  # 100 per minute for all other API routes
        # {key: [timestamps]}
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Only rate-limit API and auth routes
        path = request.url.path
        if not (path.startswith("/api/") or path.startswith("/auth/")):
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        max_requests, window = self._get_limit(path)
        key = f"{client_ip}:{self._get_limit_key(path)}"

        now = time.monotonic()
        timestamps = self._requests[key]

        # Prune expired entries
        cutoff = now - window
        self._requests[key] = [t for t in timestamps if t > cutoff]
        timestamps = self._requests[key]

        if len(timestamps) >= max_requests:
            retry_after = int(window - (now - timestamps[0]))
            logger.warning("Rate limit hit: %s (%d/%d in %ds)", key, len(timestamps), max_requests, window)
            return JSONResponse(
                {"detail": "Rate limit exceeded", "retry_after": max(retry_after, 1)},
                status_code=429,
                headers={"Retry-After": str(max(retry_after, 1))},
            )

        timestamps.append(now)
        return await call_next(request)

    def _get_limit(self, path: str) -> tuple[int, int]:
        for prefix, limit in self.limits.items():
            if path.startswith(prefix):
                return limit
        return self.default_limit

    @staticmethod
    def _get_limit_key(path: str) -> str:
        if path.startswith("/auth/"):
            return "auth"
        if path.startswith("/api/refresh"):
            return "refresh"
        return "api"

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


# ---------------------------------------------------------------------------
# Security Headers
# ---------------------------------------------------------------------------
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add standard security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response
