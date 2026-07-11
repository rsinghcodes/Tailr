from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from domain.shared.base_entity import BaseEntity


class SystemInfo(BaseEntity):

    __tablename__ = "system_info"

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )