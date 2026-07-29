import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.job_description.models import JobDescription, JobRequirements
from domain.job_description.repository import JobDescriptionRepository
from infrastructure.database.job_description_models import JobDescriptionModel


class JobDescriptionRepositoryImpl(JobDescriptionRepository):
    """SQLAlchemy implementation of the Job Description repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self, jd_id: uuid.UUID
    ) -> Optional[tuple[JobDescription, Optional[JobRequirements]]]:
        stmt = select(JobDescriptionModel).where(JobDescriptionModel.id == jd_id)
        result = await self.session.execute(stmt)
        db_model = result.scalar_one_or_none()
        if not db_model:
            return None

        jd = JobDescription(
            id=db_model.id,
            title=db_model.title,
            company=db_model.company,
            description=db_model.description,
            location=db_model.location,
            employment_type=db_model.employment_type,
            raw_extracted=db_model.raw_extracted,
        )

        reqs = None
        if db_model.parsed_requirements:
            reqs = JobRequirements(**db_model.parsed_requirements)

        return jd, reqs

    async def list_all(
        self,
    ) -> list[
        tuple[
            uuid.UUID,
            str,
            str | None,
            str | None,
            str | None,
            str | None,
            datetime,
            datetime,
        ]
    ]:
        stmt = select(
            JobDescriptionModel.id,
            JobDescriptionModel.title,
            JobDescriptionModel.company,
            JobDescriptionModel.description,
            JobDescriptionModel.created_at,
            JobDescriptionModel.updated_at,
        ).order_by(JobDescriptionModel.updated_at.desc())
        result = await self.session.execute(stmt)
        return [
            (
                row.id,
                row.title,
                row.company,
                row.description,
                "",
                "",
                row.created_at,
                row.updated_at,
            )
            for row in result.all()
        ]

    async def save(
        self, jd: JobDescription, requirements: Optional[JobRequirements] = None
    ) -> JobDescription:
        stmt = select(JobDescriptionModel).where(JobDescriptionModel.id == jd.id)
        result = await self.session.execute(stmt)
        db_model = result.scalar_one_or_none()

        reqs_dict = requirements.model_dump(mode="json") if requirements else None

        if db_model:
            db_model.title = jd.title
            db_model.company = jd.company or "Unknown Company"
            db_model.description = jd.description
            if jd.location is not None:
                db_model.location = jd.location
            if jd.employment_type is not None:
                db_model.employment_type = jd.employment_type
            if jd.raw_extracted is not None:
                db_model.raw_extracted = jd.raw_extracted
            if reqs_dict is not None:
                db_model.parsed_requirements = reqs_dict
        else:
            db_model = JobDescriptionModel(
                id=jd.id,
                title=jd.title,
                company=jd.company or "Unknown Company",
                description=jd.description,
                location=jd.location,
                employment_type=jd.employment_type,
                raw_extracted=jd.raw_extracted,
                parsed_requirements=reqs_dict,
            )
            self.session.add(db_model)

        await self.session.commit()
        return jd

    async def delete(self, jd_id: uuid.UUID) -> bool:
        stmt = select(JobDescriptionModel).where(JobDescriptionModel.id == jd_id)
        result = await self.session.execute(stmt)
        db_model = result.scalar_one_or_none()
        if not db_model:
            return False

        await self.session.delete(db_model)
        await self.session.commit()
        return True
