import time
from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy import text
from infrastructure.database.engine import engine
from infrastructure.redis.client import redis_client
from infrastructure.qdrant.vector_store import QdrantVectorStore
from infrastructure.ollama.health import ollama_health_checker

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
    """Detailed health check testing connectivity to PostgreSQL, Redis, Qdrant, and Ollama Docker."""
    services: dict[str, ServiceHealthDetail] = {}

    # 1. PostgreSQL Check
    start_time = time.perf_counter()
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        latency = round((time.perf_counter() - start_time) * 1000, 2)
        services["postgres"] = ServiceHealthDetail(status="healthy", online=True, latency_ms=latency)
    except Exception as exc:
        latency = round((time.perf_counter() - start_time) * 1000, 2)
        services["postgres"] = ServiceHealthDetail(
            status="unhealthy", online=False, latency_ms=latency, details={"error": str(exc)}
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
            status="offline", online=False, latency_ms=latency, details={"error": str(exc)}
        )

    # 3. Qdrant Check
    start_time = time.perf_counter()
    try:
        store = QdrantVectorStore()
        qdrant_online = await store.health_check()
        latency = round((time.perf_counter() - start_time) * 1000, 2)
        services["qdrant"] = ServiceHealthDetail(
            status="healthy" if qdrant_online else "offline",
            online=qdrant_online,
            latency_ms=latency,
        )
    except Exception as exc:
        latency = round((time.perf_counter() - start_time) * 1000, 2)
        services["qdrant"] = ServiceHealthDetail(
            status="offline", online=False, latency_ms=latency, details={"error": str(exc)}
        )

    # 4. Ollama Docker Check
    ollama_data = await ollama_health_checker.check_health()
    services["ollama"] = ServiceHealthDetail(
        status=ollama_data.get("status", "offline"),
        online=ollama_data.get("online", False),
        latency_ms=ollama_data.get("latency_ms"),
        details={
            "available_models": ollama_data.get("available_models", []),
            "url": ollama_data.get("url"),
            "error": ollama_data.get("error"),
        },
    )

    # Calculate overall system status
    all_online = all(s.online for s in services.values())
    postgres_online = services["postgres"].online
    overall_status = "healthy" if all_online else ("degraded" if postgres_online else "unhealthy")

    return SystemHealthResponse(status=overall_status, services=services)