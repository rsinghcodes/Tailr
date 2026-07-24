import pytest
from application.workflow.service import WorkflowApplicationService
from workflows.state import WorkflowStatus


@pytest.mark.asyncio
async def test_workflow_application_service_start_workflow():
    service = WorkflowApplicationService()
    state = await service.start_workflow(
        raw_resume_text="Experienced engineer with Python expertise.",
        job_description_text="Seeking Senior Python engineer.",
        user_id="test_user_123",
    )

    assert state.status == WorkflowStatus.COMPLETED
    assert state.user_id == "test_user_123"
    assert state.ats_report is not None
    assert state.ats_report["score"] == 92
