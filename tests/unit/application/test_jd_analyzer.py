import pytest
from unittest.mock import AsyncMock, MagicMock
from prompts.registry import PromptRegistry
from domain.shared.llm_provider import LLMProvider
from domain.job_description.models import JobDescription, JobRequirements
from application.job_description.analyzer import JobDescriptionAnalyzer


def test_prompt_registry_load_success(tmp_path):
    # Setup a temp directory with prompt templates
    category_dir = tmp_path / "jd_analyzer"
    category_dir.mkdir()
    
    system_file = category_dir / "system_v1.txt"
    system_file.write_text("System instructions", encoding="utf-8")
    
    user_file = category_dir / "user_v1.txt"
    user_file.write_text("User template {title} {company} {description}", encoding="utf-8")

    registry = PromptRegistry(prompts_dir=str(tmp_path))
    
    assert registry.get_prompt("jd_analyzer", "system") == "System instructions"
    assert registry.get_prompt("jd_analyzer", "user") == "User template {title} {company} {description}"


def test_prompt_registry_file_not_found():
    registry = PromptRegistry(prompts_dir="/non-existent")
    with pytest.raises(FileNotFoundError):
        registry.get_prompt("jd_analyzer", "system")


@pytest.mark.asyncio
async def test_jd_analyzer_service():
    # Setup mock registry and provider
    registry = MagicMock(spec=PromptRegistry)
    registry.get_prompt.side_effect = lambda cat, name, ver="v1": {
        ("jd_analyzer", "system"): "System instructions",
        ("jd_analyzer", "user"): "User template {title} {company} {description}"
    }[(cat, name)]

    mock_requirements = JobRequirements(
        required_skills=["Python", "FastAPI"],
        preferred_skills=["Docker"],
        responsibilities=["Build backend services"],
        soft_skills=["Communication"],
        keywords=["REST"],
        experience_level="Mid-Level"
    )

    llm_provider = MagicMock(spec=LLMProvider)
    llm_provider.generate = AsyncMock(return_value=mock_requirements)

    analyzer = JobDescriptionAnalyzer(llm_provider=llm_provider, prompt_registry=registry)

    jd = JobDescription(
        title="Software Engineer",
        company="TestCorp",
        description="We need a developer to code API endpoints."
    )

    result = await analyzer.analyze(jd)
    
    assert isinstance(result, JobRequirements)
    assert result.required_skills == ["Python", "FastAPI"]
    assert result.experience_level == "Mid-Level"

    # Verify formatting and generation parameters
    expected_user_prompt = "User template Software Engineer TestCorp We need a developer to code API endpoints."
    llm_provider.generate.assert_called_once_with(
        prompt=expected_user_prompt,
        system_prompt="System instructions",
        schema=JobRequirements,
        temperature=0.0,
        model=None
    )
