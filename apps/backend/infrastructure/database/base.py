from sqlalchemy.orm import DeclarativeBase

from infrastructure.database.naming import metadata


class Base(DeclarativeBase):
    metadata = metadata