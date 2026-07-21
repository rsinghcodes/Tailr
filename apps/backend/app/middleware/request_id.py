"""
Assigns a Request ID to every incoming request.
"""

from __future__ import annotations

import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from telemetry.constants import REQUEST_ID_HEADER
from telemetry.request_context import (
    clear_request_id,
    set_request_id,
)
from telemetry.types import RequestId


class RequestIDMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        request_id = request.headers.get(
            REQUEST_ID_HEADER,
            str(uuid.uuid4()),
        )
        set_request_id(RequestId(request_id))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        clear_request_id()

        return response