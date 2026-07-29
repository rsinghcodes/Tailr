from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.shutdown import shutdown
from app.startup import startup, run_startup_checks
from infrastructure.redis.client import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    startup()
    await run_startup_checks()
    yield
    await redis_client.close()
    shutdown()
