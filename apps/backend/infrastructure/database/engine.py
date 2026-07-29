import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool
from config.settings import settings

is_testing = (
    "pytest" in sys.modules
    or "PYTEST_CURRENT_TEST" in os.environ
    or os.getenv("TESTING", "").lower() in ("true", "1")
)

engine_kwargs = {
    "echo": settings.DEBUG,
    "future": True,
}

if is_testing:
    engine_kwargs["poolclass"] = NullPool
else:
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20
    engine_kwargs["pool_recycle"] = 3600

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)
