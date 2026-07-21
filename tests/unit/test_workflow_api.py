import pytest
from httpx import AsyncClient, ASGITransport
from app.app import create_app


@pytest.mark.asyncio
async def test_workflow_api_endpoint():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "raw_resume_text": "Experienced Software Engineer with Python and FastAPI experience.",
            "job_description_text": "Seeking Python engineer with Docker skills.",
        }
        response = await client.post("/api/v1/workflows", json=payload)
        assert response.status_code == 201

        data = response.json()
        assert "workflow_id" in data
        assert data["status"] == "COMPLETED"
        assert data["ats_report"]["score"] == 92
