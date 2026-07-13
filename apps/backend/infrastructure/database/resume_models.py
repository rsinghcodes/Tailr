import uuid
from typing import Optional
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from domain.shared.base_entity import BaseEntity


class ResumeModel(BaseEntity):
    __tablename__ = "resumes"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    current_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    versions: Mapped[list["ResumeVersionModel"]] = relationship(
        "ResumeVersionModel",
        back_populates="resume",
        cascade="all, delete-orphan",
        order_by="ResumeVersionModel.version",
    )


class ResumeVersionModel(BaseEntity):
    __tablename__ = "resume_versions"

    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    latex_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    pdf_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    canonical_json: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Relationships
    resume: Mapped[ResumeModel] = relationship("ResumeModel", back_populates="versions")
