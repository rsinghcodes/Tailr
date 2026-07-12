"""
Logs every HTTP request.
"""

from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from telemetry import get_logger
from telemetry.request_context import get_request_id

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration = (
            time.perf_counter() - start
        ) * 1000
        logger.info(
            "HTTP Request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration, 2),
            request_id=get_request_id(),
        )

        return response