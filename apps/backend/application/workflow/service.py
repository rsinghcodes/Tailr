import logging
import uuid
from typing import Optional
from workflows.state import WorkflowState
from workflows.engine import WorkflowEngine
from infrastructure.repositories.workflow_repository import WorkflowRepositoryImpl
from infrastructure.repositories.guardrail_repository import GuardrailRepositoryImpl
from infrastructure.repositories.resume_repository import ResumeRepositoryImpl
from infrastructure.repositories.job_description_repository import JobDescriptionRepositoryImpl
from infrastructure.database.workflow_models import WorkflowRunModel
from infrastructure.database import SessionFactory

logger = logging.getLogger(__name__)

# In-memory cache for active workflow states (survives DB lookup issues)
_workflow_cache: dict[str, WorkflowState] = {}


class WorkflowApplicationService:
    """Application Service coordinating workflow execution, persistence, and audit logging."""

    def __init__(
        self,
        engine: Optional[WorkflowEngine] = None,
        workflow_repo: Optional[WorkflowRepositoryImpl] = None,
        guardrail_repo: Optional[GuardrailRepositoryImpl] = None,
        resume_repo: Optional[ResumeRepositoryImpl] = None,
        jd_repo: Optional[JobDescriptionRepositoryImpl] = None,
    ):
        self.engine = engine or WorkflowEngine()
        self.workflow_repo = workflow_repo
        self.guardrail_repo = guardrail_repo
        self.resume_repo = resume_repo
        self.jd_repo = jd_repo

    async def start_workflow(
        self,
        raw_resume_text: str | None = None,
        job_description_text: str | None = None,
        resume_id: str | None = None,
        job_description_id: str | None = None,
        user_id: str = "default_user",
    ) -> WorkflowState:
        # Fetch resume text from DB if resume_id provided
        if resume_id and not raw_resume_text and self.resume_repo:
            try:
                resume_uuid = uuid.UUID(resume_id)
                resume = await self.resume_repo.get_by_version_id(resume_uuid)
                if resume:
                    raw_resume_text = resume.to_latex() if hasattr(resume, "to_latex") else str(resume.model_dump())
            except Exception as exc:
                logger.warning("Failed to fetch resume %s: %s", resume_id, str(exc))

        # Fetch JD text from DB if job_description_id provided
        if job_description_id and not job_description_text and self.jd_repo:
            try:
                jd_uuid = uuid.UUID(job_description_id)
                jd_result = await self.jd_repo.get_by_id(jd_uuid)
                if jd_result:
                    jd, _ = jd_result
                    job_description_text = jd.description
            except Exception as exc:
                logger.warning("Failed to fetch JD %s: %s", job_description_id, str(exc))

        state = WorkflowState(
            raw_resume_text=raw_resume_text,
            job_description_text=job_description_text,
            user_id=user_id,
        )

        state.telemetry.model_versions = {
            "jd_analyzer": "Qwen 3 (8B)",
            "planner": "Qwen 3 (14B)",
            "rewriter": "Llama 3.1 (8B)",
            "ats_advisor": "Gemma 3 (9B)",
        }

        logger.info("Starting workflow execution", extra={"workflow_id": state.workflow_id, "user_id": user_id})

        final_state = await self.engine.execute_workflow(state)

        # Cache in memory for immediate status lookups
        _workflow_cache[final_state.workflow_id] = final_state

        # Persist to database
        try:
            async with SessionFactory() as session:
                db_run = WorkflowRunModel(
                    id=uuid.UUID(final_state.workflow_id),
                    status=final_state.status.value,
                    current_step=final_state.telemetry.current_step,
                    started_at=final_state.telemetry.started_at,
                    completed_at=final_state.telemetry.completed_at,
                    state_data={
                        "raw_resume_text": final_state.raw_resume_text,
                        "job_description_text": final_state.job_description_text,
                        "canonical_resume": final_state.canonical_resume,
                        "job_requirements": final_state.job_requirements,
                        "rewrite_plan": final_state.rewrite_plan,
                        "rewritten_resume": final_state.rewritten_resume,
                        "guardrail_report": final_state.guardrail_report,
                        "validation_report": final_state.validation_report,
                        "ats_report": final_state.ats_report,
                        "render_result": final_state.render_result,
                        "telemetry": final_state.telemetry.model_dump(),
                        "errors": final_state.errors,
                    },
                )
                session.add(db_run)
                await session.commit()
                logger.info("Workflow %s persisted to database", final_state.workflow_id)
        except Exception as exc:
            logger.warning("Failed to persist workflow to DB (in-memory cache used): %s", str(exc))

        # Audit persistence if repository injected
        if self.guardrail_repo and final_state.guardrail_report:
            violations = final_state.guardrail_report.get("violations", [])
            for v in violations:
                try:
                    await self.guardrail_repo.record_event(
                        workflow_id=final_state.workflow_id,
                        validator_name=final_state.guardrail_report.get("metadata", {}).get("failed_validator", "guardrails"),
                        severity=v.get("severity", "high"),
                        violation_code=v.get("code"),
                        repaired=final_state.guardrail_report.get("repaired", False),
                        metadata=v.get("metadata"),
                    )
                except Exception as exc:
                    logger.warning("Failed to record guardrail event: %s", str(exc))

        return final_state

    async def get_workflow_state(self, workflow_id: str) -> WorkflowState | None:
        # 1. Check in-memory cache first (fast path)
        if workflow_id in _workflow_cache:
            return _workflow_cache[workflow_id]

        # 2. Try database
        if self.workflow_repo:
            try:
                wf_uuid = uuid.UUID(workflow_id)
                domain_state = await self.workflow_repo.get_by_id(wf_uuid)
                if domain_state:
                    state = WorkflowState(
                        workflow_id=str(domain_state.id),
                        status=domain_state.status.value,
                        telemetry={"current_step": domain_state.status.value},
                    )
                    # Reconstruct full state from DB state_data if available
                    return state
            except Exception as exc:
                logger.warning("Failed to retrieve workflow state from database: %s", str(exc))

        return None
