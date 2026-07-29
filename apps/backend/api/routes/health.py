import time
from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy import text
from infrastructure.database.engine import engine
from infrastructure.redis.client import redis_client
from infrastructure.langchain.health import gemini_health_checker

router = APIRouter(tags=["Health"])


class ServiceHealthDetail(BaseModel):
    status: str
    online: bool
    latency_ms: float | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class SystemHealthResponse(BaseModel):
    status: str
    services: dict[str, ServiceHealthDetail]


@router.get("/health", response_model=SystemHealthResponse)
async def health_check():
    """Detailed health check testing connectivity to PostgreSQL, Redis, Qdrant, and Gemini API."""
    services: dict[str, ServiceHealthDetail] = {}

    # 1. PostgreSQL Check
    start_time = time.perf_counter()
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        latency = round((time.perf_counter() - start_time) * 1000, 2)
        services["postgres"] = ServiceHealthDetail(
            status="healthy", online=True, latency_ms=latency
        )
    except Exception as exc:
        latency = round((time.perf_counter() - start_time) * 1000, 2)
        services["postgres"] = ServiceHealthDetail(
            status="unhealthy",
            online=False,
            latency_ms=latency,
            details={"error": str(exc)},
        )

    # 2. Redis Check
    start_time = time.perf_counter()
    try:
        redis_online = await redis_client.ping()
        latency = round((time.perf_counter() - start_time) * 1000, 2)
        services["redis"] = ServiceHealthDetail(
            status="healthy" if redis_online else "offline",
            online=redis_online,
            latency_ms=latency,
            details={"url": redis_client.redis_url},
        )
    except Exception as exc:
        latency = round((time.perf_counter() - start_time) * 1000, 2)
        services["redis"] = ServiceHealthDetail(
            status="offline",
            online=False,
            latency_ms=latency,
            details={"error": str(exc)},
        )

    # 3. Gemini API Check
    gemini_data = await gemini_health_checker.check_health()
    services["gemini"] = ServiceHealthDetail(
        status=gemini_data.get("status", "offline"),
        online=gemini_data.get("online", False),
        latency_ms=gemini_data.get("latency_ms"),
        details={
            "model": gemini_data.get("model"),
            "error": gemini_data.get("error"),
        },
    )

    # Calculate overall system status
    all_online = all(s.online for s in services.values())
    postgres_online = services["postgres"].online
    overall_status = (
        "healthy" if all_online else ("degraded" if postgres_online else "unhealthy")
    )

    return SystemHealthResponse(status=overall_status, services=services)
