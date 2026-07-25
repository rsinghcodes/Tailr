import pytest
from httpx import AsyncClient, ASGITransport
from app.app import create_app


@pytest.mark.asyncio
async def test_guardrails_api_endpoints():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Validate output endpoint
        response = await client.post(
            "/api/v1/guardrails/validate",
            json={"content": {"summary": "Valid resume summary"}, "profile_name": "rewrite_strict"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "repair_applied" in data

        # Prompt injection check endpoint
        response = await client.post(
            "/api/v1/guardrails/injection-check",
            json={"content": "Normal resume content"},
        )
        assert response.status_code == 200
        assert response.json()["detected"] is False

        # Repair endpoint
        response = await client.post(
            "/api/v1/guardrails/repair",
            json={"content": "```json\n{\"summary\": \"test\"}\n```"},
        )
        assert response.status_code == 200
        assert "repaired" in response.json()


@pytest.mark.asyncio
async def test_ats_api_endpoints():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/ats/analyze",
            json={"resume_id": "res-1", "job_description_id": "jd-1"},
        )
        assert response.status_code == 200
        report = response.json()["report"]
        assert "overall_score" in report
        assert "keyword_coverage" in report

        response = await client.post(
            "/api/v1/ats/compare",
            json={"original_resume_id": "r1", "tailored_resume_id": "r2", "job_description_id": "jd1"},
        )
        assert response.status_code == 200
        assert "score_delta" in response.json()


@pytest.mark.asyncio
async def test_render_api_endpoints():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/render/latex",
            json={"resume_id": "res-1", "template_name": "classic"},
        )
        assert response.status_code == 200
        assert "latex_code" in response.json()

        response = await client.post(
            "/api/v1/render/pdf",
            json={"latex_code": r"\documentclass{article}\begin{document}Hello\end{document}"},
        )
        assert response.status_code == 200
        assert "pdf_url" in response.json()


@pytest.mark.asyncio
async def test_optimization_and_knowledge_api_endpoints():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Optimization plan
        response = await client.post(
            "/api/v1/optimization/plan",
            json={"resume_id": "res-1", "job_description_id": "jd-1"},
        )
        assert response.status_code == 200
        assert "plan_id" in response.json()

        # Knowledge search
        response = await client.post(
            "/api/v1/knowledge/search",
            json={"query": "Python FastAPI", "limit": 5},
        )
        assert response.status_code == 200
        assert "results" in response.json()

        # History & Analytics
        response = await client.get("/api/v1/history")
        assert response.status_code == 200

        response = await client.get("/api/v1/analytics")
        assert response.status_code == 200
        assert response.json()["total_optimizations"] >= 1
