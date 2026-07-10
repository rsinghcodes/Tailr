from fastapi import FastAPI

from api.routes.health import router as health_router
from config.settings import settings

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)

app.include_router(
    health_router,
    prefix=settings.API_PREFIX,
)