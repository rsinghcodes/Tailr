import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport
from app.app import create_app
from domain.shared.llm_provider import LLMProvider
from domain.job_description.models import JobRequirements
from api.dependencies.services import get_llm_provider
from infrastructure.database import SessionFactory
from sqlalchemy import select
from infrastructure.database.job_description_models import JobDescriptionModel


@pytest.mark.asyncio
async def test_job_description_api_lifecycle():
    app = create_app()

    # Setup dependency override for the LLM Provider to prevent live Ollama network requests
    mock_llm = MagicMock(spec=LLMProvider)
    mock_requirements = JobRequirements(
        required_skills=["Python", "FastAPI"],
        preferred_skills=["Docker"],
        responsibilities=["Build clean API routes"],
        keywords=["REST"],
        experience_level="Mid-Level"
    )
    mock_llm.generate = AsyncMock(return_value=mock_requirements)
    app.dependency_overrides[get_llm_provider] = lambda: mock_llm

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. POST /job-descriptions
        payload = {
            "title": "Backend Dev",
            "description": "Must know Python and FastAPI.",
            "company": "FastCorp",
            "location": "Remote",
            "employment_type": "Full-Time"
        }

        response = await client.post("/api/v1/job-descriptions", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "id" in data["data"]
        assert data["data"]["title"] == "Backend Dev"
        assert data["data"]["company"] == "FastCorp"
        assert data["data"]["parsed_requirements"]["required_skills"] == ["Python", "FastAPI"]

        jd_id = uuid.UUID(data["data"]["id"])

        try:
            # 2. GET /job-descriptions/{id}
            response = await client.get(f"/api/v1/job-descriptions/{jd_id}")
            assert response.status_code == 200
            get_data = response.json()
            assert get_data["success"] is True
            assert get_data["data"]["id"] == str(jd_id)
            assert get_data["data"]["parsed_requirements"]["required_skills"] == ["Python", "FastAPI"]

            # 3. GET non-existent
            non_existent_id = uuid.uuid4()
            response = await client.get(f"/api/v1/job-descriptions/{non_existent_id}")
            assert response.status_code == 404
            err_data = response.json()
            assert err_data["success"] is False
            assert err_data["error"]["code"] == "NOT_FOUND"

        finally:
            # 4. DELETE /job-descriptions/{id}
            response = await client.delete(f"/api/v1/job-descriptions/{jd_id}")
            assert response.status_code == 200
            assert response.json()["success"] is True

            # Verify it is deleted from database
            async with SessionFactory() as session:
                stmt = select(JobDescriptionModel).where(JobDescriptionModel.id == jd_id)
                res = await session.execute(stmt)
                db_res = res.scalar_one_or_none()
                assert db_res is None
