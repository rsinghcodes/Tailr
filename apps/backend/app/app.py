from fastapi import FastAPI

from api.routes.health import router as health_router
from app.lifespan import lifespan
from app.middleware import (
    LoggingMiddleware,
    RequestIDMiddleware,
)
from config.settings import settings


def create_app() -> FastAPI:

    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(LoggingMiddleware)

    app.include_router(
        health_router,
        prefix=settings.API_PREFIX,
    )

    return app