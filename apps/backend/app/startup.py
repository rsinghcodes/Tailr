import logging
from sqlalchemy import text
from telemetry.config import configure_logging
from infrastructure.database.engine import engine
from infrastructure.redis.client import redis_client
from infrastructure.qdrant.vector_store import QdrantVectorStore
from infrastructure.ollama.health import ollama_health_checker

logger = logging.getLogger(__name__)


def startup() -> None:
    """Synchronous startup configuration (logging setup)."""
    configure_logging()


async def run_startup_checks() -> dict[str, bool]:
    """Runs async diagnostic checks for all infrastructure services during app startup.

    Verifies connectivity to PostgreSQL, Redis, Qdrant, and Ollama Docker container.

    Returns:
        Dictionary mapping service names to boolean readiness status.
    """
    logger.info("Starting backend infrastructure startup diagnostics...")
    results = {}

    # 1. Test PostgreSQL Database connection
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("[Startup Diagnostic] PostgreSQL Database: ONLINE")
        results["postgres"] = True
    except Exception as exc:
        logger.error("[Startup Diagnostic] PostgreSQL Database: OFFLINE (%s)", str(exc))
        results["postgres"] = False

    # 2. Test Redis connection
    try:
        redis_online = await redis_client.ping()
        if redis_online:
            logger.info("[Startup Diagnostic] Redis Cache: ONLINE")
        else:
            logger.warning("[Startup Diagnostic] Redis Cache: OFFLINE (Connection refused at %s)", redis_client.redis_url)
        results["redis"] = redis_online
    except Exception as exc:
        logger.warning("[Startup Diagnostic] Redis Cache: OFFLINE (%s)", str(exc))
        results["redis"] = False

    # 3. Test Qdrant Vector DB connection
    try:
        store = QdrantVectorStore()
        qdrant_online = await store.health_check()
        if qdrant_online:
            logger.info("[Startup Diagnostic] Qdrant Vector Store: ONLINE")
        else:
            logger.warning("[Startup Diagnostic] Qdrant Vector Store: OFFLINE")
        results["qdrant"] = qdrant_online
    except Exception as exc:
        logger.warning("[Startup Diagnostic] Qdrant Vector Store: OFFLINE (%s)", str(exc))
        results["qdrant"] = False

    # 4. Test Ollama Docker Container connection
    try:
        ollama_status = await ollama_health_checker.check_health()
        if ollama_status.get("online"):
            models = ollama_status.get("available_models", [])
            logger.info("[Startup Diagnostic] Ollama Docker Service: ONLINE (Models: %s)", models)
            results["ollama"] = True
        else:
            logger.warning(
                "[Startup Diagnostic] Ollama Docker Service: OFFLINE (%s at %s)",
                ollama_status.get("error", "Unreachable"),
                ollama_status.get("url"),
            )
            results["ollama"] = False
    except Exception as exc:
        logger.warning("[Startup Diagnostic] Ollama Docker Service: OFFLINE (%s)", str(exc))
        results["ollama"] = False

    logger.info("Infrastructure startup diagnostics complete: %s", results)
    return results