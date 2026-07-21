import logging
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from domain.shared.exceptions import BaseAppException

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Registers global exception handlers to return standard JSON error structures.

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(BaseAppException)
    async def app_exception_handler(request, exc: BaseAppException):
        code = "INTERNAL_ERROR"
        status_code = 500
        msg = str(exc)

        # Parse specific app errors
        lower_msg = msg.lower()
        if "parse" in lower_msg or "lexer" in lower_msg:
            code = "PARSE_ERROR"
            status_code = 422
        elif "validate" in lower_msg or "validation" in lower_msg:
            code = "VALIDATION_ERROR"
            status_code = 422

        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "error": {
                    "code": code,
                    "message": msg
                }
            }
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc: HTTPException):
        code = "VALIDATION_ERROR"
        if exc.status_code == 404:
            code = "NOT_FOUND"
        elif exc.status_code == 401:
            code = "UNAUTHORIZED"
        elif exc.status_code == 403:
            code = "FORBIDDEN"
        elif exc.status_code == 409:
            code = "CONFLICT"
        elif exc.status_code == 422 or "parsing" in str(exc.detail).lower():
            code = "PARSE_ERROR"

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": code,
                    "message": exc.detail
                }
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc: RequestValidationError):
        # Human readable validation message list
        details = []
        for err in exc.errors():
            loc = " -> ".join(str(x) for x in err.get("loc", []))
            msg = err.get("msg", "invalid value")
            details.append(f"{loc}: {msg}")
        
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "; ".join(details)
                }
            }
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request, exc: Exception):
        logger.exception("Unhandled server error: %s", str(exc))
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected internal server error occurred."
                }
            }
        )
