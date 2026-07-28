import io
import logging
import uuid
from typing import Any, Optional
from pydantic import BaseModel, Field
from llama_cloud import AsyncLlamaCloud
from config.settings import settings

logger = logging.getLogger(__name__)


class ExtractedResume(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    summary: str = ""
    skills: list[str] = Field(default_factory=list)
    experience: list[dict[str, Any]] = Field(default_factory=list)
    education: list[dict[str, Any]] = Field(default_factory=list)
    projects: list[dict[str, Any]] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)


class ExtractedJobRequirements(BaseModel):
    title: str = ""
    company: str = ""
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    seniority: str = ""
    keywords: list[str] = Field(default_factory=list)


class LlamaExtractor:
    """Structured data extraction using LlamaCloud Extract API."""

    def __init__(self, client: Optional[AsyncLlamaCloud] = None):
        self._client = client or AsyncLlamaCloud(api_key=settings.LLAMA_CLOUD_API_KEY)

    async def extract_resume(self, text: str) -> ExtractedResume:
        schema = ExtractedResume.model_json_schema()
        try:
            file_id = await self._upload_text(text, f"resume_{uuid.uuid4().hex}.txt")
            job = await self._client.extract.run(
                file_input=str(file_id),
                configuration={"data_schema": schema},
            )
            if job.status == "COMPLETED" and job.extract_result:
                return ExtractedResume.model_validate(job.extract_result)
        except Exception as exc:
            logger.warning("LlamaExtract resume failed: %s", str(exc))
        return ExtractedResume()

    async def extract_job_requirements(self, text: str) -> ExtractedJobRequirements:
        schema = ExtractedJobRequirements.model_json_schema()
        try:
            file_id = await self._upload_text(text, f"jd_{uuid.uuid4().hex}.txt")
            job = await self._client.extract.run(
                file_input=str(file_id),
                configuration={"data_schema": schema},
            )
            if job.status == "COMPLETED" and job.extract_result:
                return ExtractedJobRequirements.model_validate(job.extract_result)
        except Exception as exc:
            logger.warning("LlamaExtract JD failed: %s", str(exc))
        return ExtractedJobRequirements()

    async def _upload_text(self, text: str, filename: str) -> str:
        file_obj = await self._client.files.create(
            file=(filename, io.BytesIO(text.encode("utf-8")), "text/plain"),
            purpose="extract",
        )
        return file_obj.id
