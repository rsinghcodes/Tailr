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
        raw_latex: Optional[str] = None,
        title: Optional[str] = None,
        resume_container_id: Optional[uuid.UUID] = None,
    ) -> Resume:
        container_id = resume_container_id
        db_resume = None

        if not container_id:
            # Create a new parent Resume container
            db_resume = ResumeModel(
                title=title or f"Resume - {datetime.utcnow().strftime('%Y-%m-%d')}",
                current_version=1,
                status="active"
            )
            self.session.add(db_resume)
            await self.session.flush()
            container_id = db_resume.id
        else:
            # Check if parent container exists, and increment version
            stmt_resume = select(ResumeModel).where(ResumeModel.id == container_id)
            result_resume = await self.session.execute(stmt_resume)
            db_resume = result_resume.scalar_one_or_none()
            if db_resume:
                db_resume.current_version += 1
                await self.session.flush()

        current_ver = db_resume.current_version if db_resume else 1

        # Check if the version already exists in database
        stmt_version = select(ResumeVersionModel).where(ResumeVersionModel.id == resume.id)
        result_version = await self.session.execute(stmt_version)
        db_version = result_version.scalar_one_or_none()

        if db_version:
            # Update version record
            db_version.canonical_json = resume.model_dump(mode="json")
            if raw_latex:
                db_version.latex_path = raw_latex
            db_version.updated_at = datetime.utcnow()
        else:
            # Save new version record
            db_version = ResumeVersionModel(
                id=resume.id,
                resume_id=container_id,
                version=current_ver,
                latex_path=raw_latex,
                pdf_path=None,
                canonical_json=resume.model_dump(mode="json"),
                created_at=resume.created_at,
                updated_at=resume.updated_at
            )
            self.session.add(db_version)

        await self.session.commit()
        return resume

    async def delete(self, resume_id: uuid.UUID) -> bool:
        # Search parent container
        stmt = select(ResumeModel).where(ResumeModel.id == resume_id)
        result = await self.session.execute(stmt)
        db_resume = result.scalar_one_or_none()
        if not db_resume:
            return False
        
        await self.session.delete(db_resume)
        await self.session.commit()
        return True

    async def list_all(self) -> list[tuple[uuid.UUID, str, int, str, datetime, datetime]]:
        stmt = select(
            ResumeModel.id,
            ResumeModel.title,
            ResumeModel.current_version,
            ResumeModel.status,
            ResumeModel.created_at,
            ResumeModel.updated_at
        ).order_by(ResumeModel.updated_at.desc())
        result = await self.session.execute(stmt)
        # Convert list of Rows to list of tuples
        return [
            (row.id, row.title, row.current_version, row.status, row.created_at, row.updated_at)
            for row in result.all()
        ]

    async def get_versions_by_resume_id(
        self, resume_id: uuid.UUID
    ) -> list[tuple[uuid.UUID, int, Optional[str], datetime, datetime]]:
        stmt = select(
            ResumeVersionModel.id,
            ResumeVersionModel.version,
            ResumeVersionModel.latex_path,
            ResumeVersionModel.created_at,
            ResumeVersionModel.updated_at
        ).where(ResumeVersionModel.resume_id == resume_id).order_by(ResumeVersionModel.version.desc())
        result = await self.session.execute(stmt)
        return [
            (row.id, row.version, row.latex_path, row.created_at, row.updated_at)
            for row in result.all()
        ]

    def _to_domain(self, db_version: ResumeVersionModel) -> Resume:
        resume_data = db_version.canonical_json
        resume = Resume(**resume_data)
        resume.id = db_version.id
        resume.created_at = db_version.created_at
        resume.updated_at = db_version.updated_at
        return resume

