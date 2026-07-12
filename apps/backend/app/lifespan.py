from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.shutdown import shutdown
from app.startup import startup


@asynccontextmanager
async def lifespan(app: FastAPI):
    startup()
    yield
    shutdown()