import pytest
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from domain.resume.models import Resume, Skill, SkillCategory
from domain.resume.repository import ResumeRepository
from application.resume.service import ResumeService


@pytest.mark.asyncio
async def test_upload_resume():
    mock_repo = MagicMock(spec=ResumeRepository)
    mock_repo.save = AsyncMock()

    service = ResumeService(mock_repo)

    raw_latex = r"""
\section{Skills}
 \begin{itemize}
    \item \textbf{Languages}{: Python, Java}
 \end{itemize}
"""
    filename = "resume.tex"
    title = "My Resume"

    resume = await service.upload_resume(raw_latex, filename, title=title)

    assert isinstance(resume, Resume)
    assert resume.metadata.template_name == filename
    assert resume.metadata.additional_metadata["custom_title"] == title

    # Ensure Skills were parsed
    assert len(resume.skills) == 2
    skill_names = [s.name for s in resume.skills]
    assert "Python" in skill_names
    assert "Java" in skill_names

    # Ensure save was called on repo
    mock_repo.save.assert_called_once_with(
        resume=resume,
        raw_latex=raw_latex,
        title=title,
        resume_container_id=None,
    )


@pytest.mark.asyncio
async def test_get_resume_by_version():
    mock_repo = MagicMock(spec=ResumeRepository)
    version_id = uuid.uuid4()
    expected_resume = Resume(summary="Expert developer")
    mock_repo.get_by_version_id = AsyncMock(return_value=expected_resume)

    service = ResumeService(mock_repo)
    result = await service.get_resume_by_version(version_id)

    assert result == expected_resume
    mock_repo.get_by_version_id.assert_called_once_with(version_id)


@pytest.mark.asyncio
async def test_list_resumes():
    mock_repo = MagicMock(spec=ResumeRepository)
    now = datetime.utcnow()
    resume_id = uuid.uuid4()
    mock_repo.list_all = AsyncMock(
        return_value=[
            (resume_id, "My Title", 2, "active", now, now)
        ]
    )

    service = ResumeService(mock_repo)
    result = await service.list_resumes()

    assert len(result) == 1
    assert result[0] == {
        "id": resume_id,
        "title": "My Title",
        "current_version": 2,
        "status": "active",
        "created_at": now,
        "updated_at": now,
    }
    mock_repo.list_all.assert_called_once()


@pytest.mark.asyncio
async def test_get_resume_versions():
    mock_repo = MagicMock(spec=ResumeRepository)
    now = datetime.utcnow()
    version_id = uuid.uuid4()
    mock_repo.get_versions_by_resume_id = AsyncMock(
        return_value=[
            (version_id, 1, "% raw latex", now, now)
        ]
    )

    service = ResumeService(mock_repo)
    resume_id = uuid.uuid4()
    result = await service.get_resume_versions(resume_id)

    assert len(result) == 1
    assert result[0] == {
        "version_id": version_id,
        "version": 1,
        "latex_path": "% raw latex",
        "created_at": now,
        "updated_at": now,
    }
    mock_repo.get_versions_by_resume_id.assert_called_once_with(resume_id)


@pytest.mark.asyncio
async def test_delete_resume_container():
    mock_repo = MagicMock(spec=ResumeRepository)
    mock_repo.delete = AsyncMock(return_value=True)

    service = ResumeService(mock_repo)
    resume_id = uuid.uuid4()
    result = await service.delete_resume_container(resume_id)

    assert result is True
    mock_repo.delete.assert_called_once_with(resume_id)
