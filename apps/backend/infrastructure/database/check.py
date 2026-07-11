from sqlalchemy import text

from infrastructure.database.engine import engine


async def check_database() -> bool:

    try:
        async with engine.begin() as conn:
            await conn.execute(
                text("SELECT 1")
            )

        return True

    except Exception:
        return False