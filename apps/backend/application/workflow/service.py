import json
import logging
import uuid
from typing import Any, AsyncGenerator, Optional
from workflows.state import WorkflowState
from workflows.graph import get_compiled_graph
from workflows.diff import compute_bullet_diff
from infrastructure.repositories.workflow_repository import WorkflowRepositoryImpl
from infrastructure.repositories.guardrail_repository import GuardrailRepositoryImpl
from config.settings import settings

logger = logging.getLogger(__name__)

STEP_LABELS: dict[str, dict[str, str]] = {
    "retrieve_context": {
        "label": "Context Retrieval",
        "description": "Searching knowledge base for relevant context",
    },
    "plan": {
        "label": "Rewrite Planning",
        "description": "Generating optimization strategy",
    },
    "rewrite": {
        "label": "Resume Rewriting",
        "description": "Applying optimizations to resume content",
    },
    "guardrails": {
        "label": "Guardrail Check",
        "description": "Running safety and quality checks",
    },
    "validation": {
        "label": "Validation",
        "description": "Validating business rules and completeness",
    },
    "ats_analysis": {
        "label": "ATS Analysis",
        "description": "Scoring resume against applicant tracking system",
    },
    "render": {"label": "Rendering", "description": "Generating final output"},
}


class WorkflowApplicationService:
    """Application Service coordinating LangGraph workflow execution, persistence, and audit logging."""

    def __init__(
        self,
        workflow_repo: Optional[WorkflowRepositoryImpl] = None,
        guardrail_repo: Optional[GuardrailRepositoryImpl] = None,
    ):
        self.workflow_repo = workflow_repo
        self.guardrail_repo = guardrail_repo

    def _build_initial_state(
        self,
        user_id: str = "default_user",
        canonical_resume: dict[str, Any] | None = None,
        job_requirements: dict[str, Any] | None = None,
        user_feedback: dict[str, Any] | None = None,
    ) -> WorkflowState:
        state: WorkflowState = {
            "request_id": str(uuid.uuid4()),
            "workflow_id": str(uuid.uuid4()),
            "user_id": user_id,
            "telemetry": {
                "current_step": "NEW",
                "step_history": [],
                "model_versions": {
                    "planner": settings.GEMINI_MODEL,
                    "rewriter": settings.GEMINI_MODEL,
                    "ats_advisor": settings.GEMINI_MODEL,
                },
            },
            "errors": [],
        }
        if canonical_resume:
            state["canonical_resume"] = canonical_resume
        if job_requirements:
            state["job_requirements"] = job_requirements
        if user_feedback:
            state["user_feedback"] = user_feedback
        return state

    async def start_workflow(
        self,
        user_id: str = "default_user",
        canonical_resume: dict[str, Any] | None = None,
        job_requirements: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        graph = get_compiled_graph()
        initial_state = self._build_initial_state(
            user_id,
            canonical_resume=canonical_resume,
            job_requirements=job_requirements,
        )

        logger.info(
            "Starting LangGraph workflow",
            extra={"workflow_id": initial_state["workflow_id"], "user_id": user_id},
        )

        final_state = await graph.ainvoke(initial_state)

        if self.guardrail_repo and final_state.get("guardrail_report"):
            violations = final_state["guardrail_report"].get("violations", [])
            for v in violations:
                await self.guardrail_repo.record_event(
                    workflow_id=final_state["workflow_id"],
                    validator_name=final_state["guardrail_report"]
                    .get("metadata", {})
                    .get("failed_validator", "guardrails"),
                    severity=v.get("severity", "high"),
                    violation_code=v.get("code"),
                    repaired=final_state["guardrail_report"].get("repaired", False),
                    metadata=v.get("metadata"),
                )

        return dict(final_state)

    async def start_workflow_stream(
        self,
        user_id: str = "default_user",
        canonical_resume: dict[str, Any] | None = None,
        job_requirements: dict[str, Any] | None = None,
        user_feedback: dict[str, Any] | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        graph = get_compiled_graph()
        initial_state = self._build_initial_state(
            user_id,
            canonical_resume=canonical_resume,
            job_requirements=job_requirements,
            user_feedback=user_feedback,
        )
        workflow_id = initial_state["workflow_id"]

        logger.info(
            "Starting streamed LangGraph workflow", extra={"workflow_id": workflow_id}
        )

        yield {
            "event": "workflow_start",
            "data": {"workflow_id": workflow_id, "total_steps": len(STEP_LABELS)},
        }

        step_index = 0
        accumulated_state: dict[str, Any] = {}
        async for event in graph.astream(initial_state, stream_mode="updates"):
            for node_name, node_output in event.items():
                step_index += 1
                meta = STEP_LABELS.get(
                    node_name, {"label": node_name, "description": ""}
                )

                yield {
                    "event": "step_start",
                    "data": {
                        "step": node_name,
                        "step_index": step_index,
                        "total_steps": len(STEP_LABELS),
                        "label": meta["label"],
                        "description": meta["description"],
                    },
                }

                safe_output = {}
                for k, v in (node_output or {}).items():
                    try:
                        json.dumps(v)
                        safe_output[k] = v
                    except (TypeError, ValueError):
                        safe_output[k] = str(v)

                if safe_output:
                    accumulated_state.update(safe_output)

                yield {
                    "event": "step_complete",
                    "data": {
                        "step": node_name,
                        "step_index": step_index,
                        "total_steps": len(STEP_LABELS),
                        "label": meta["label"],
                        "output": safe_output,
                    },
                }

        rewritten_resume = accumulated_state.get("rewritten_resume")
        bullet_diff = (
            compute_bullet_diff(canonical_resume or {}, rewritten_resume or {})
            if isinstance(canonical_resume, dict)
            else None
        )

        yield {
            "event": "workflow_complete",
            "data": {
                "workflow_id": workflow_id,
                "status": "completed",
                "rewritten_resume": rewritten_resume,
                "bullet_diff": bullet_diff,
                "ats_report": accumulated_state.get("ats_report"),
                "guardrail_report": accumulated_state.get("guardrail_report"),
                "validation_report": accumulated_state.get("validation_report"),
                "rewrite_plan": accumulated_state.get("rewrite_plan"),
                "telemetry": initial_state.get("telemetry", {}),
            },
        }

    async def get_workflow_state(self, workflow_id: str) -> dict[str, Any] | None:
        if self.workflow_repo:
            try:
                wf_uuid = uuid.UUID(workflow_id)
                domain_state = await self.workflow_repo.get_by_id(wf_uuid)
                if domain_state:
                    return {
                        "workflow_id": str(domain_state.id),
                        "status": domain_state.current_state.value,
                    }
            except Exception as exc:
                logger.warning(
                    "Failed to retrieve workflow state from database: %s", str(exc)
                )

        return None
