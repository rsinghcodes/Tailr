from fastapi import FastAPI

from api.routes.health import router as health_router
from api.routes.resume import router as resume_router
from api.routes.job_description import router as job_description_router
from api.routes.workflow import router as workflow_router
from api.routes.guardrails import router as guardrails_router
from app.lifespan import lifespan
from app.middleware import (
    LoggingMiddleware,
    RequestIDMiddleware,
)
from app.middleware.exception import register_exception_handlers
from config.settings import settings


def create_app() -> FastAPI:

    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # Register standardized exception handlers
    register_exception_handlers(app)

    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(LoggingMiddleware)

    app.include_router(
        health_router,
        prefix=settings.API_PREFIX,
    )
    app.include_router(
        resume_router,
        prefix=settings.API_PREFIX,
    )
    app.include_router(
        job_description_router,
        prefix=settings.API_PREFIX,
    )
    app.include_router(
        workflow_router,
        prefix=settings.API_PREFIX,
    )
    app.include_router(
        guardrails_router,
        prefix=settings.API_PREFIX,
    )

    return app