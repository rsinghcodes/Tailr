from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
import uuid
from domain.resume.models import Resume


class ResumeRepository(ABC):
    @abstractmethod
    async def get_by_version_id(self, version_id: uuid.UUID) -> Optional[Resume]:
        pass

    @abstractmethod
    async def save(
        self,
        resume: Resume,
        raw_text: Optional[str] = None,
        title: Optional[str] = None,
        resume_container_id: Optional[uuid.UUID] = None,
    ) -> Resume:
        pass

    @abstractmethod
    async def delete(self, resume_id: uuid.UUID) -> bool:
        pass

    @abstractmethod
    async def list_all(self) -> list[tuple[uuid.UUID, str, int, str, datetime, datetime]]:
        pass

    @abstractmethod
    async def get_versions_by_resume_id(
        self, resume_id: uuid.UUID
    ) -> list[tuple[uuid.UUID, int, datetime, datetime]]:
        pass
