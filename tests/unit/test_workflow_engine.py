import pytest
from workflows.state import WorkflowState, WorkflowStatus
from workflows.engine import WorkflowEngine


@pytest.mark.asyncio
async def test_workflow_engine_execution_success():
    engine = WorkflowEngine()
    state = WorkflowState(
        raw_resume_text="Worked at TechCorp using Python and FastAPI.",
        job_description_text="Looking for a Python software engineer with Docker skills.",
    )

    final_state = await engine.execute_workflow(state)

    assert final_state.status == WorkflowStatus.COMPLETED
    assert final_state.canonical_resume is not None
    assert final_state.job_requirements is not None
    assert final_state.rewritten_resume is not None
    assert final_state.guardrail_report is not None
    assert final_state.ats_report["score"] == 92
    assert "GUARDRAILS" in final_state.telemetry.step_history
