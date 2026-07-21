import logging
import uuid
from typing import Optional
from workflows.state import WorkflowState
from workflows.engine import WorkflowEngine
from infrastructure.repositories.workflow_repository import WorkflowRepositoryImpl
from infrastructure.repositories.guardrail_repository import GuardrailRepositoryImpl

logger = logging.getLogger(__name__)


class WorkflowApplicationService:
    """Application Service coordinating workflow execution, persistence, and audit logging."""

    def __init__(
        self,
        engine: Optional[WorkflowEngine] = None,
        workflow_repo: Optional[WorkflowRepositoryImpl] = None,
        guardrail_repo: Optional[GuardrailRepositoryImpl] = None,
    ):
        self.engine = engine or WorkflowEngine()
        self.workflow_repo = workflow_repo
        self.guardrail_repo = guardrail_repo

    async def start_workflow(
        self,
        raw_resume_text: str | None = None,
        job_description_text: str | None = None,
        user_id: str = "default_user",
    ) -> WorkflowState:
        state = WorkflowState(
            raw_resume_text=raw_resume_text,
            job_description_text=job_description_text,
            user_id=user_id,
        )

        logger.info("Starting workflow execution", extra={"workflow_id": state.workflow_id, "user_id": user_id})

        final_state = await self.engine.execute_workflow(state)

        # Audit persistence if repository injected
        if self.guardrail_repo and final_state.guardrail_report:
            violations = final_state.guardrail_report.get("violations", [])
            for v in violations:
                await self.guardrail_repo.record_event(
                    workflow_id=final_state.workflow_id,
                    validator_name=final_state.guardrail_report.get("metadata", {}).get("failed_validator", "guardrails"),
                    severity=v.get("severity", "high"),
                    violation_code=v.get("code"),
                    repaired=final_state.guardrail_report.get("repaired", False),
                    metadata=v.get("metadata"),
                )

        return final_state

    async def get_workflow_state(self, workflow_id: str) -> WorkflowState | None:
        if self.workflow_repo:
            try:
                wf_uuid = uuid.UUID(workflow_id)
                domain_state = await self.workflow_repo.get_by_id(wf_uuid)
                if domain_state:
                    return WorkflowState(
                        workflow_id=str(domain_state.id),
                        status=domain_state.current_state.value,
                    )
            except Exception as exc:
                logger.warning("Failed to retrieve workflow state from database: %s", str(exc))

        return None
