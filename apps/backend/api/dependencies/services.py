from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database import get_db

from domain.resume.repository import ResumeRepository
from infrastructure.repositories.resume_repository import ResumeRepositoryImpl
from application.resume.service import ResumeService

from domain.job_description.repository import JobDescriptionRepository
from infrastructure.repositories.job_description_repository import (
    JobDescriptionRepositoryImpl,
)
from application.job_description.service import JobDescriptionService
from domain.shared.llm_provider import LLMProvider
from infrastructure.langchain.llm_provider import GeminiProvider
from prompts.registry import PromptRegistry

from infrastructure.repositories.workflow_repository import WorkflowRepositoryImpl
from infrastructure.repositories.guardrail_repository import GuardrailRepositoryImpl
from application.workflow.service import WorkflowApplicationService
from application.guardrails.service import GuardrailApplicationService
from domain.user.repository import UserRepository
from infrastructure.repositories.user_repository import UserRepositoryImpl
from application.auth.service import AuthService
from infrastructure.llamaindex.client import get_llama_client
from infrastructure.llamaindex.extractors import LlamaExtractor
from infrastructure.llamaindex.vector_store import VectorStoreService

_prompt_registry = PromptRegistry()
_llm_provider = GeminiProvider()


_llama_client = get_llama_client()


def get_prompt_registry() -> PromptRegistry:
    return _prompt_registry


def get_llm_provider() -> LLMProvider:
    return _llm_provider


def get_llama_extractor() -> LlamaExtractor:
    return LlamaExtractor(client=_llama_client)


def get_vector_store_service() -> VectorStoreService:
    return VectorStoreService()


async def get_resume_repository(
    session: AsyncSession = Depends(get_db),
) -> ResumeRepository:
    return ResumeRepositoryImpl(session)


async def get_resume_service(
    repo: ResumeRepository = Depends(get_resume_repository),
) -> ResumeService:
    return ResumeService(repo)


async def get_job_description_repository(
    session: AsyncSession = Depends(get_db),
) -> JobDescriptionRepository:
    return JobDescriptionRepositoryImpl(session)


async def get_job_description_service(
    repo: JobDescriptionRepository = Depends(get_job_description_repository),
) -> JobDescriptionService:
    return JobDescriptionService(repo)


async def get_workflow_repository(
    session: AsyncSession = Depends(get_db),
) -> WorkflowRepositoryImpl:
    return WorkflowRepositoryImpl(session)


async def get_guardrail_repository(
    session: AsyncSession = Depends(get_db),
) -> GuardrailRepositoryImpl:
    return GuardrailRepositoryImpl(session)


async def get_workflow_service(
    workflow_repo: WorkflowRepositoryImpl = Depends(get_workflow_repository),
    guardrail_repo: GuardrailRepositoryImpl = Depends(get_guardrail_repository),
) -> WorkflowApplicationService:
    return WorkflowApplicationService(
        workflow_repo=workflow_repo, guardrail_repo=guardrail_repo
    )


async def get_guardrail_service(
    guardrail_repo: GuardrailRepositoryImpl = Depends(get_guardrail_repository),
) -> GuardrailApplicationService:
    return GuardrailApplicationService(guardrail_repo=guardrail_repo)


async def get_user_repository(
    session: AsyncSession = Depends(get_db),
) -> UserRepository:
    return UserRepositoryImpl(session)


async def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(user_repo)
