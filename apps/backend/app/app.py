from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.health import router as health_router
from api.routes.resume import router as resume_router
from api.routes.job_description import router as job_description_router
from api.routes.workflow import router as workflow_router
from api.routes.guardrails import router as guardrails_router
from api.routes.ats import router as ats_router
from api.routes.render import router as render_router
from api.routes.optimization import router as optimization_router
from api.routes.knowledge import router as knowledge_router
from api.routes.history import router as history_router
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

    # Register CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register standardized exception handlers
    register_exception_handlers(app)

    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(LoggingMiddleware)

    app.include_router(health_router, prefix=settings.API_PREFIX)
    app.include_router(resume_router, prefix=settings.API_PREFIX)
    app.include_router(job_description_router, prefix=settings.API_PREFIX)
    app.include_router(workflow_router, prefix=settings.API_PREFIX)
    app.include_router(guardrails_router, prefix=settings.API_PREFIX)
    app.include_router(ats_router, prefix=settings.API_PREFIX)
    app.include_router(render_router, prefix=settings.API_PREFIX)
    app.include_router(optimization_router, prefix=settings.API_PREFIX)
    app.include_router(knowledge_router, prefix=settings.API_PREFIX)
    app.include_router(history_router, prefix=settings.API_PREFIX)

    return app