import uuid
from typing import Any, Optional
from domain.resume.models import Resume, Skill, Experience, ExperienceBullet, Education, Project
from domain.resume.repository import ResumeRepository
from infrastructure.redis.cache import RedisCacheService


class ResumeService:
    """Application service to manage resume creation, updating, versioning, listing, and deletion."""

    def __init__(self, repository: ResumeRepository, cache_service: Optional[RedisCacheService] = None):
        self.repository = repository
        self.cache_service = cache_service or RedisCacheService()

    async def upload_resume(
        self,
        raw_text: str,
        filename: str,
        title: Optional[str] = None,
        resume_container_id: Optional[uuid.UUID] = None,
        extracted: Any = None,
    ) -> tuple[Resume, uuid.UUID]:
        if extracted:
            resume = Resume(
                summary=extracted.summary or raw_text[:500],
                skills=[Skill(name=s) for s in (extracted.skills or [])],
                experience=[
                    Experience(
                        company=e.get("company", ""),
                        role=e.get("role", ""),
                        start_date=e.get("start_date", ""),
                        end_date=e.get("end_date"),
                        bullets=[ExperienceBullet(text=b) for b in e.get("bullets", [])],
                    )
                    for e in (extracted.experience or [])
                ],
                education=[
                    Education(
                        institution=e.get("institution", ""),
                        degree=e.get("degree", ""),
                        start_date=e.get("start_date", ""),
                        end_date=e.get("end_date"),
                    )
                    for e in (extracted.education or [])
                ],
                projects=[
                    Project(
                        title=p.get("title", ""),
                        description=p.get("description"),
                    )
                    for p in (extracted.projects or [])
                ],
            )
        else:
            resume = Resume(summary=raw_text[:500] if len(raw_text) > 500 else raw_text)
        resume.metadata.template_name = filename
        if title:
            resume.metadata.additional_metadata["custom_title"] = title

        _, container_id = await self.repository.save(
            resume=resume,
            raw_text=raw_text,
            title=title,
            resume_container_id=resume_container_id,
        )

        cache_key = f"resume:version:{resume.id}"
        await self.cache_service.set_model(cache_key, resume, ttl_seconds=3600)

        return resume, container_id

    async def get_resume_by_version(self, version_id: uuid.UUID) -> Optional[Resume]:
        cache_key = f"resume:version:{version_id}"
        cached_resume = await self.cache_service.get_model(cache_key, Resume)
        if cached_resume:
            return cached_resume

        resume = await self.repository.get_by_version_id(version_id)
        if resume:
            await self.cache_service.set_model(cache_key, resume, ttl_seconds=3600)
        return resume

    async def list_resumes(self) -> list[dict]:
        raw_list = await self.repository.list_all()
        return [
            {
                "id": item[0],
                "title": item[1],
                "current_version": item[2],
                "status": item[3],
                "created_at": item[4],
                "updated_at": item[5],
            }
            for item in raw_list
        ]

    async def get_resume_versions(self, resume_id: uuid.UUID) -> list[dict]:
        raw_list = await self.repository.get_versions_by_resume_id(resume_id)
        return [
            {
                "version_id": item[0],
                "version": item[1],
                "created_at": item[2],
                "updated_at": item[3],
            }
            for item in raw_list
        ]

    async def delete_resume_container(self, resume_id: uuid.UUID) -> bool:
        return await self.repository.delete(resume_id)
