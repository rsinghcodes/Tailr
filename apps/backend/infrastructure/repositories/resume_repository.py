import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from domain.resume.models import Resume
from domain.resume.repository import ResumeRepository
from infrastructure.database.resume_models import ResumeModel, ResumeVersionModel


class ResumeRepositoryImpl(ResumeRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_version_id(self, version_id: uuid.UUID) -> Optional[Resume]:
        stmt = select(ResumeVersionModel).where(ResumeVersionModel.id == version_id)
        result = await self.session.execute(stmt)
        db_version = result.scalar_one_or_none()
        if not db_version:
            return None
        return self._to_domain(db_version)

    async def save(
        self,
        resume: Resume,
        title: Optional[str] = None,
        resume_container_id: Optional[uuid.UUID] = None,
    ) -> tuple[Resume, uuid.UUID]:
        container_id = resume_container_id
        db_resume = None

        if not container_id:
            db_resume = ResumeModel(
                title=title or f"Resume - {datetime.utcnow().strftime('%Y-%m-%d')}",
                current_version=1,
                status="active",
            )
            self.session.add(db_resume)
            await self.session.flush()
            container_id = db_resume.id
        else:
            stmt_resume = select(ResumeModel).where(ResumeModel.id == container_id)
            result_resume = await self.session.execute(stmt_resume)
            db_resume = result_resume.scalar_one_or_none()
            if db_resume:
                db_resume.current_version += 1
                await self.session.flush()

        current_ver = db_resume.current_version if db_resume else 1

        stmt_version = select(ResumeVersionModel).where(
            ResumeVersionModel.id == resume.id
        )
        result_version = await self.session.execute(stmt_version)
        db_version = result_version.scalar_one_or_none()

        if db_version:
            db_version.canonical_json = resume.model_dump(mode="json")
            db_version.updated_at = datetime.utcnow()
        else:
            db_version = ResumeVersionModel(
                id=resume.id,
                resume_id=container_id,
                version=current_ver,
                canonical_json=resume.model_dump(mode="json"),
                created_at=resume.created_at,
                updated_at=resume.updated_at,
            )
            self.session.add(db_version)

        await self.session.commit()
        return resume, container_id

    async def delete(self, resume_id: uuid.UUID) -> bool:
        stmt = select(ResumeModel).where(ResumeModel.id == resume_id)
        result = await self.session.execute(stmt)
        db_resume = result.scalar_one_or_none()
        if not db_resume:
            return False

        await self.session.delete(db_resume)
        await self.session.commit()
        return True

    async def list_all(
        self,
    ) -> list[tuple[uuid.UUID, str, int, str, datetime, datetime]]:
        stmt = select(
            ResumeModel.id,
            ResumeModel.title,
            ResumeModel.current_version,
            ResumeModel.status,
            ResumeModel.created_at,
            ResumeModel.updated_at,
        ).order_by(ResumeModel.updated_at.desc())
        result = await self.session.execute(stmt)
        return [
            (
                row.id,
                row.title,
                row.current_version,
                row.status,
                row.created_at,
                row.updated_at,
            )
            for row in result.all()
        ]

    async def get_versions_by_resume_id(
        self, resume_id: uuid.UUID
    ) -> list[tuple[uuid.UUID, int, datetime, datetime]]:
        stmt = (
            select(
                ResumeVersionModel.id,
                ResumeVersionModel.version,
                ResumeVersionModel.created_at,
                ResumeVersionModel.updated_at,
            )
            .where(ResumeVersionModel.resume_id == resume_id)
            .order_by(ResumeVersionModel.version.desc())
        )
        result = await self.session.execute(stmt)
        return [
            (row.id, row.version, row.created_at, row.updated_at)
            for row in result.all()
        ]

    def _to_domain(self, db_version: ResumeVersionModel) -> Resume:
        resume_data = db_version.canonical_json
        resume = Resume(**resume_data)
        resume.id = db_version.id
        resume.created_at = db_version.created_at
        resume.updated_at = db_version.updated_at
        return resume
