import io
import logging
from typing import Optional
from pydantic import BaseModel, Field
from llama_cloud import AsyncLlamaCloud
from config.settings import settings

logger = logging.getLogger(__name__)


class ExtractedExperience(BaseModel):
    company: str = ""
    role: str = ""
    location: str = ""
    employment_type: str = ""
    start_date: str = ""
    end_date: str = ""
    technologies: list[str] = Field(default_factory=list)
    bullets: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)


class ExtractedEducation(BaseModel):
    institution: str = ""
    degree: str = ""
    field: str = ""
    cgpa: str = ""
    start_date: str = ""
    end_date: str = ""


class ExtractedProject(BaseModel):
    title: str = ""
    description: str = ""
    technologies: list[str] = Field(default_factory=list)
    url: str = ""
    bullets: list[str] = Field(default_factory=list)


class ExtractedCertification(BaseModel):
    name: str = ""
    issuer: str = ""
    credential_id: str = ""
    issue_date: str = ""


class ExtractedAchievement(BaseModel):
    title: str = ""
    description: str = ""
    category: str = ""
    date: str = ""


class ExtractedResume(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    summary: str = ""
    skills: list[str] = Field(default_factory=list)
    experience: list[ExtractedExperience] = Field(default_factory=list)
    education: list[ExtractedEducation] = Field(default_factory=list)
    projects: list[ExtractedProject] = Field(default_factory=list)
    certifications: list[ExtractedCertification] = Field(default_factory=list)
    achievements: list[ExtractedAchievement] = Field(default_factory=list)


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

    async def extract_resume(self, file_bytes: bytes, filename: str = "resume.pdf") -> ExtractedResume:
        schema = ExtractedResume.model_json_schema()
        try:
            content_type = self._infer_mime(filename)
            file_obj = await self._client.files.create(
                file=(filename, io.BytesIO(file_bytes), content_type),
                purpose="extract",
            )
            job = await self._client.extract.run(
                file_input=str(file_obj.id),
                configuration={"data_schema": schema},
            )
            if job.status == "COMPLETED" and job.extract_result:
                return ExtractedResume.model_validate(job.extract_result)
        except Exception as exc:
            logger.warning("LlamaExtract resume failed: %s", str(exc))
        return ExtractedResume()

    async def extract_job_requirements(self, file_bytes: bytes, filename: str = "jd.pdf") -> ExtractedJobRequirements:
        schema = ExtractedJobRequirements.model_json_schema()
        try:
            content_type = self._infer_mime(filename)
            file_obj = await self._client.files.create(
                file=(filename, io.BytesIO(file_bytes), content_type),
                purpose="extract",
            )
            job = await self._client.extract.run(
                file_input=str(file_obj.id),
                configuration={"data_schema": schema},
            )
            if job.status == "COMPLETED" and job.extract_result:
                return ExtractedJobRequirements.model_validate(job.extract_result)
        except Exception as exc:
            logger.warning("LlamaExtract JD failed: %s", str(exc))
        return ExtractedJobRequirements()

    @staticmethod
    def _infer_mime(filename: str) -> str:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        return {
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "txt": "text/plain",
            "tex": "text/plain",
        }.get(ext, "application/octet-stream")
