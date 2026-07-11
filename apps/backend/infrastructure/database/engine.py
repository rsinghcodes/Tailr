from sqlalchemy.ext.asyncio import create_async_engine
from config.settings import settings


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True, # Automatically reconnect dead connections.
    pool_size=10, # Keep 10 open.
    max_overflow=20, # Can temporarily create 20 more.
    pool_recycle=3600,
)