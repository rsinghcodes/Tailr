import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from domain.shared.base_entity import BaseEntity
from infrastructure.database.resume_models import ResumeModel
from infrastructure.database.job_description_models import JobDescriptionModel


class WorkflowRunModel(BaseEntity):
    __tablename__ = "workflow_runs"

    resume_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="SET NULL"),
        nullable=True,
    )
    job_description_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_descriptions.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    current_step: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    token_usage: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    state_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationships
    resume: Mapped[Optional[ResumeModel]] = relationship(
        "ResumeModel",
        foreign_keys=[resume_id],
    )
    job_description: Mapped[Optional[JobDescriptionModel]] = relationship(
        "JobDescriptionModel",
        foreign_keys=[job_description_id],
    )
