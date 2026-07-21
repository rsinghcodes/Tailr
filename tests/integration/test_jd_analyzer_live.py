import pytest
import httpx
from config.settings import settings
from prompts.registry import PromptRegistry
from infrastructure.ollama.llm_provider import OllamaProvider
from domain.job_description.models import JobDescription, JobRequirements
from application.job_description.analyzer import JobDescriptionAnalyzer


async def get_available_models() -> list[str]:
    """Helper to query local Ollama tags API for pulled models."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.OLLAMA_URL}/api/tags", timeout=3.0)
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []
    return []


@pytest.mark.asyncio
async def test_jd_analyzer_live():
    models = await get_available_models()
    if not models:
        pytest.skip("Ollama service is offline or has no models pulled.")

    test_model = models[0]
    llm_provider = OllamaProvider(default_model=test_model)
    prompt_registry = PromptRegistry()
    
    analyzer = JobDescriptionAnalyzer(llm_provider=llm_provider, prompt_registry=prompt_registry)

    jd = JobDescription(
        title="Python Developer",
        company="StartupInc",
        description="We are looking for a Python Developer with 3 years of experience in writing backend APIs using FastAPI. Knowledge of Docker is preferred."
    )

    try:
        result = await analyzer.analyze(jd)
        assert isinstance(result, JobRequirements)
        assert len(result.required_skills) > 0 or len(result.preferred_skills) > 0
    finally:
        await llm_provider.close()
