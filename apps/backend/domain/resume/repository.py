from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
import uuid
from domain.resume.models import Resume


class ResumeRepository(ABC):
    @abstractmethod
    async def get_by_version_id(self, version_id: uuid.UUID) -> Optional[Resume]:
        """Retrieve a specific resume version by its version ID."""
        pass

    @abstractmethod
    async def save(
        self,
        resume: Resume,
        raw_latex: Optional[str] = None,
        title: Optional[str] = None,
        resume_container_id: Optional[uuid.UUID] = None,
    ) -> Resume:
        """Save a new resume version, optionally linked to a parent resume container."""
        pass

    @abstractmethod
    async def delete(self, resume_id: uuid.UUID) -> bool:
        """Delete a resume container and all its versions."""
        pass

    @abstractmethod
    async def list_all(self) -> list[tuple[uuid.UUID, str, int, str, datetime, datetime]]:
        """List all parent resume containers."""
        pass

    @abstractmethod
    async def get_versions_by_resume_id(
        self, resume_id: uuid.UUID
    ) -> list[tuple[uuid.UUID, int, Optional[str], datetime, datetime]]:
        """Get all version records for a specific resume container."""
        pass

