from typing import Optional
from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from domain.shared.base_entity import BaseEntity


class JobDescriptionModel(BaseEntity):
    __tablename__ = "job_descriptions"

    company: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_requirements: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
