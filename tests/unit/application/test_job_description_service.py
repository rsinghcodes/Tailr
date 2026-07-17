import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from domain.job_description.models import JobDescription, JobRequirements
from domain.job_description.repository import JobDescriptionRepository
from application.job_description.analyzer import JobDescriptionAnalyzer
from application.job_description.service import JobDescriptionService


@pytest.mark.asyncio
async def test_create_job_description():
    mock_repo = MagicMock(spec=JobDescriptionRepository)
    mock_repo.save = AsyncMock()

    mock_reqs = JobRequirements(
        required_skills=["Python", "SQL"],
        experience_level="Senior"
    )
    mock_analyzer = MagicMock(spec=JobDescriptionAnalyzer)
    mock_analyzer.analyze = AsyncMock(return_value=mock_reqs)

    service = JobDescriptionService(mock_repo, mock_analyzer)

    title = "Data Engineer"
    description = "We need an engineer to manage pipeline scripts."
    company = "DataCorp"
    location = "Remote"
    employment_type = "Full-Time"

    jd, reqs = await service.create_job_description(
        title=title,
        description=description,
        company=company,
        location=location,
        employment_type=employment_type
    )

    assert isinstance(jd, JobDescription)
    assert jd.title == title
    assert jd.company == company
    assert jd.location == location
    assert jd.employment_type == employment_type
    assert jd.description == description
    assert reqs == mock_reqs

    # Verify repository save called twice (initially, then with parsed requirements)
    assert mock_repo.save.call_count == 2
    mock_repo.save.assert_any_call(jd)
    mock_repo.save.assert_any_call(jd, mock_reqs)

    mock_analyzer.analyze.assert_called_once_with(jd, model=None)


@pytest.mark.asyncio
async def test_get_job_description():
    mock_repo = MagicMock(spec=JobDescriptionRepository)
    mock_analyzer = MagicMock(spec=JobDescriptionAnalyzer)
    
    jd_id = uuid.uuid4()
    expected_jd = JobDescription(title="QA", description="Test app")
    expected_reqs = JobRequirements(required_skills=["Testing"])
    mock_repo.get_by_id = AsyncMock(return_value=(expected_jd, expected_reqs))

    service = JobDescriptionService(mock_repo, mock_analyzer)
    result = await service.get_job_description(jd_id)

    assert result == (expected_jd, expected_reqs)
    mock_repo.get_by_id.assert_called_once_with(jd_id)


@pytest.mark.asyncio
async def test_delete_job_description():
    mock_repo = MagicMock(spec=JobDescriptionRepository)
    mock_analyzer = MagicMock(spec=JobDescriptionAnalyzer)
    mock_repo.delete = AsyncMock(return_value=True)

    service = JobDescriptionService(mock_repo, mock_analyzer)
    jd_id = uuid.uuid4()
    result = await service.delete_job_description(jd_id)

    assert result is True
    mock_repo.delete.assert_called_once_with(jd_id)
