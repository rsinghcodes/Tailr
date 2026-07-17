import uuid
from typing import Optional

from domain.job_description.models import JobDescription, JobRequirements
from domain.job_description.repository import JobDescriptionRepository
from application.job_description.analyzer import JobDescriptionAnalyzer


class JobDescriptionService:
    """Application service to manage job description upload, analysis, and lifecycle."""

    def __init__(
        self,
        repository: JobDescriptionRepository,
        analyzer: JobDescriptionAnalyzer,
    ):
        self.repository = repository
        self.analyzer = analyzer

    async def create_job_description(
        self,
        title: str,
        description: str,
        company: Optional[str] = None,
        location: Optional[str] = None,
        employment_type: Optional[str] = None,
        model: Optional[str] = None,
    ) -> tuple[JobDescription, JobRequirements]:
        """Creates a new Job Description, analyzes it using an LLM, and persists it."""
        jd = JobDescription(
            title=title,
            description=description,
            company=company,
            location=location,
            employment_type=employment_type,
        )

        # Save initial record
        await self.repository.save(jd)

        # Run requirement analysis
        requirements = await self.analyzer.analyze(jd, model=model)

        # Save updated record with parsed requirements
        await self.repository.save(jd, requirements)

        return jd, requirements

    async def get_job_description(
        self, jd_id: uuid.UUID
    ) -> Optional[tuple[JobDescription, Optional[JobRequirements]]]:
        """Retrieve a Job Description and its requirements by ID."""
        return await self.repository.get_by_id(jd_id)

    async def delete_job_description(self, jd_id: uuid.UUID) -> bool:
        """Delete a Job Description by ID."""
        return await self.repository.delete(jd_id)
