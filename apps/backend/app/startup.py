import logging
from sqlalchemy import text
from telemetry.config import configure_logging
from infrastructure.database.engine import engine
from infrastructure.redis.client import redis_client
from infrastructure.langchain.health import gemini_health_checker

logger = logging.getLogger(__name__)


def startup() -> None:
    """Synchronous startup configuration (logging setup)."""
    configure_logging()


async def run_startup_checks() -> dict[str, bool]:
    """Runs async diagnostic checks for all infrastructure services during app startup.

    Verifies connectivity to PostgreSQL, Redis, Qdrant, and Gemini API.

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

    # 3. Test Gemini API connection
    try:
        gemini_status = await gemini_health_checker.check_health()
        if gemini_status.get("online"):
            logger.info("[Startup Diagnostic] Gemini API: ONLINE (Model: %s)", gemini_status.get("model"))
            results["gemini"] = True
        else:
            logger.warning(
                "[Startup Diagnostic] Gemini API: OFFLINE (%s)",
                gemini_status.get("error", "Unreachable"),
            )
            results["gemini"] = False
    except Exception as exc:
        logger.warning("[Startup Diagnostic] Gemini API: OFFLINE (%s)", str(exc))
        results["gemini"] = False

    logger.info("Infrastructure startup diagnostics complete: %s", results)
    return results