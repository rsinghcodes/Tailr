import io
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from app.app import create_app
from infrastructure.database import SessionFactory
from sqlalchemy import select
from infrastructure.database.resume_models import ResumeModel


@pytest.mark.asyncio
async def test_resume_api_lifecycle():
    app = create_app()
    # Use ASGITransport to call FastAPI in-process
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. POST /resumes - Upload valid LaTeX
        valid_latex = r"""
\section{Education}
\resumeSubheading
  {State University}{City, State}
  {Bachelor of Science in Computer Science}{Aug. 2018 -- May 2022}
"""
        # Create a file-like object in memory
        file_data = {"file": ("resume.tex", io.BytesIO(valid_latex.encode("utf-8")), "text/plain")}
        form_data = {"title": "Integration Test Resume"}

        response = await client.post("/api/v1/resumes", files=file_data, data=form_data)
        assert response.status_code == 201
        data = response.json()
        assert "resume_id" in data
        assert data["status"] == "uploaded"

        resume_version_id = uuid.UUID(data["resume_id"])

        # Fetch the resume_id container ID from database to perform operations and cleanups
        async with SessionFactory() as session:
            from infrastructure.database.resume_models import ResumeVersionModel
            stmt = select(ResumeVersionModel).where(ResumeVersionModel.id == resume_version_id)
            res = await session.execute(stmt)
            db_version = res.scalar_one_or_none()
            assert db_version is not None
            resume_container_id = db_version.resume_id

        try:
            # 2. GET /resumes - List all resumes
            response = await client.get("/api/v1/resumes")
            assert response.status_code == 200
            list_data = response.json()
            assert list_data["success"] is True
            assert len(list_data["data"]) >= 1
            matching = [x for x in list_data["data"] if uuid.UUID(x["id"]) == resume_container_id]
            assert len(matching) == 1
            assert matching[0]["title"] == "Integration Test Resume"
            assert matching[0]["current_version"] == 1

            # 3. GET /resumes/{resume_id} - Latest details
            response = await client.get(f"/api/v1/resumes/{resume_container_id}")
            assert response.status_code == 200
            details_data = response.json()
            assert details_data["success"] is True
            assert details_data["data"]["id"] == str(resume_version_id)
            assert len(details_data["data"]["education"]) == 1
            assert details_data["data"]["education"][0]["institution"] == "State University"

            # 4. GET /resumes/{resume_id}/versions - Version list
            response = await client.get(f"/api/v1/resumes/{resume_container_id}/versions")
            assert response.status_code == 200
            versions_data = response.json()
            assert versions_data["success"] is True
            assert len(versions_data["data"]) == 1
            assert versions_data["data"][0]["version"] == 1
            assert versions_data["data"][0]["version_id"] == str(resume_version_id)

            # 5. GET /resumes/versions/{version_id} - Specific version details
            response = await client.get(f"/api/v1/resumes/versions/{resume_version_id}")
            assert response.status_code == 200
            version_details = response.json()
            assert version_details["success"] is True
            assert version_details["data"]["id"] == str(resume_version_id)

            # 6. POST /resumes - Upload invalid file extension
            invalid_file = {"file": ("resume.pdf", io.BytesIO(b"dummy pdf content"), "application/pdf")}
            response = await client.post("/api/v1/resumes", files=invalid_file)
            # Should fail validation mapping to StandardErrorResponse
            assert response.status_code == 400
            err_data = response.json()
            assert err_data["success"] is False
            assert err_data["error"]["code"] == "VALIDATION_ERROR"
            assert "latex" in err_data["error"]["message"].lower()

            # 7. POST /resumes - Upload malformed LaTeX
            malformed_latex = r"\section{Education"  # Missing closing brace
            malformed_file = {"file": ("resume.tex", io.BytesIO(malformed_latex.encode("utf-8")), "text/plain")}
            response = await client.post("/api/v1/resumes", files=malformed_file)
            # Should fail parse mapping to StandardErrorResponse
            assert response.status_code == 422
            err_data = response.json()
            assert err_data["success"] is False
            assert err_data["error"]["code"] == "PARSE_ERROR"
            assert "missing matching" in err_data["error"]["message"].lower()

        finally:
            # 8. DELETE /resumes/{resume_id} - Cleanup
            response = await client.delete(f"/api/v1/resumes/{resume_container_id}")
            assert response.status_code == 200
            assert response.json()["success"] is True

            # Verify it is deleted from database
            async with SessionFactory() as session:
                stmt = select(ResumeModel).where(ResumeModel.id == resume_container_id)
                res = await session.execute(stmt)
                db_res = res.scalar_one_or_none()
                assert db_res is None
