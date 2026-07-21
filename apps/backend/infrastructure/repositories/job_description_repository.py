import uuid
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
        )

        reqs = None
        if db_model.parsed_requirements:
            reqs = JobRequirements(**db_model.parsed_requirements)

        return jd, reqs

    async def save(
        self, jd: JobDescription, requirements: Optional[JobRequirements] = None
    ) -> JobDescription:
        # Check if record exists
        stmt = select(JobDescriptionModel).where(JobDescriptionModel.id == jd.id)
        result = await self.session.execute(stmt)
        db_model = result.scalar_one_or_none()

        reqs_dict = requirements.model_dump(mode="json") if requirements else None

        if db_model:
            db_model.title = jd.title
            db_model.company = jd.company or "Unknown Company"
            db_model.description = jd.description
            if reqs_dict is not None:
                db_model.parsed_requirements = reqs_dict
        else:
            db_model = JobDescriptionModel(
                id=jd.id,
                title=jd.title,
                company=jd.company or "Unknown Company",
                description=jd.description,
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
