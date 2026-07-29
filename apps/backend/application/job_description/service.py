import uuid
from typing import Optional, Any

from domain.job_description.models import JobDescription, JobRequirements
from domain.job_description.repository import JobDescriptionRepository
from application.job_description.analyzer import JobDescriptionAnalyzer
from infrastructure.llamaindex.extractors import ExtractedJobRequirements


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
        raw_extracted: Optional[dict[str, Any]] = None,
    ) -> JobDescription:
        """Creates a new Job Description and persists it. No LLM analysis."""
        jd = JobDescription(
            title=title,
            description=description,
            company=company,
            location=location,
            employment_type=employment_type,
            raw_extracted=raw_extracted,
        )
        await self.repository.save(jd)
        return jd

    async def analyze_job_description(
        self,
        jd_id: uuid.UUID,
        model: Optional[str] = None,
    ) -> tuple[JobDescription, JobRequirements]:
        """Run LLM analysis on an existing Job Description. Requires saved raw_extracted data."""
        result = await self.repository.get_by_id(jd_id)
        if not result:
            raise ValueError(f"Job description {jd_id} not found")

        jd, _existing_reqs = result

        extracted = None
        if jd.raw_extracted:
            extracted = ExtractedJobRequirements(**jd.raw_extracted)

        requirements = await self.analyzer.analyze(
            jd,
            model=model,
            extracted_requirements=extracted,
        )

        await self.repository.save(jd, requirements)

        return jd, requirements

    async def list_job_descriptions(
        self,
    ) -> list[dict[str, str | int | None]]:
        """List all job descriptions."""
        rows = await self.repository.list_all()
        return [
            {
                "id": str(row[0]),
                "title": row[1],
                "company": row[2],
                "description": row[3],
                "location": row[4],
                "employment_type": row[5],
                "created_at": row[6].isoformat() if row[6] else "",
                "updated_at": row[7].isoformat() if row[7] else "",
            }
            for row in rows
        ]

    async def get_job_description(
        self, jd_id: uuid.UUID
    ) -> Optional[tuple[JobDescription, Optional[JobRequirements]]]:
        """Retrieve a Job Description and its requirements by ID."""
        return await self.repository.get_by_id(jd_id)

    async def delete_job_description(self, jd_id: uuid.UUID) -> bool:
        """Delete a Job Description by ID."""
        return await self.repository.delete(jd_id)
