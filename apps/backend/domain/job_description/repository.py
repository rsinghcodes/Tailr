import uuid
from abc import ABC, abstractmethod
from typing import Optional
from domain.job_description.models import JobDescription, JobRequirements


class JobDescriptionRepository(ABC):
    """Abstract port for persisting and retrieving Job Descriptions and their requirements."""

    @abstractmethod
    async def get_by_id(
        self, jd_id: uuid.UUID
    ) -> Optional[tuple[JobDescription, Optional[JobRequirements]]]:
        """Retrieve a job description and its parsed requirements by ID."""
        pass

    @abstractmethod
    async def save(
        self, jd: JobDescription, requirements: Optional[JobRequirements] = None
    ) -> JobDescription:
        """Save a new or update an existing job description."""
        pass

    @abstractmethod
    async def delete(self, jd_id: uuid.UUID) -> bool:
        """Delete a job description by its ID."""
        pass
