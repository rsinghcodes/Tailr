import logging
from typing import Any
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from api.dependencies.auth import get_current_user
from application.guardrails.service import GuardrailApplicationService
from api.dependencies.services import get_guardrail_service
from guardrails.pipeline import GuardrailsEngine
from guardrails.base import GuardrailContext, GuardrailResultStatus

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Guardrails Audit"], dependencies=[Depends(get_current_user)])


class GuardrailEventResponse(BaseModel):
    id: str
    workflow_id: str
    validator_name: str
    severity: str
    violations: list[Any] = Field(default_factory=list)
    violation_code: str | None = None
    repair_applied: bool = False
    repaired: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class GuardrailAuditListResponse(BaseModel):
    items: list[GuardrailEventResponse] = Field(default_factory=list)
    total: int = 0


class ValidateOutputRequest(BaseModel):
    content: Any
    schema_name: str = "resume_rewrite"
    profile_name: str = "rewrite_strict"


class ValidateOutputResponse(BaseModel):
    status: str
    repair_applied: bool = False
    violations: list[Any] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class InjectionCheckRequest(BaseModel):
    content: str


class InjectionCheckResponse(BaseModel):
    detected: bool
    severity: str = "LOW"
    rule: str = "PROMPT_INJECTION"


class RepairOutputRequest(BaseModel):
    content: Any
    schema_name: str = "resume_rewrite"


class RepairOutputResponse(BaseModel):
    repaired: bool
    content: Any


@router.get("/guardrails/events", response_model=GuardrailAuditListResponse)
async def list_guardrail_events(
    workflow_id: str = Query(..., description="Workflow ID to filter events"),
    limit: int = Query(20, ge=1, le=100),
    guardrail_service: GuardrailApplicationService = Depends(get_guardrail_service),
):
    """Retrieve immutable audit events for a workflow execution."""
    events = await guardrail_service.get_events_for_workflow(
        workflow_id=workflow_id, limit=limit
    )
    items = [
        GuardrailEventResponse(
            id=str(e.id),
            workflow_id=e.workflow_id,
            validator_name=e.validator_name,
            severity=e.severity,
            violation_code=e.violation_code,
            repair_applied=e.repaired,
            repaired=e.repaired,
            metadata=e.metadata_json or {},
            created_at=e.created_at.isoformat(),
        )
        for e in events
    ]
    return GuardrailAuditListResponse(items=items, total=len(items))


@router.post("/guardrails/validate", response_model=ValidateOutputResponse)
async def validate_ai_output(body: ValidateOutputRequest):
    """Validate AI output against the Guardrails Pipeline."""
    engine = GuardrailsEngine()
    context = GuardrailContext(profile_name=body.profile_name)
    result = await engine.execute(body.content, context)
    return ValidateOutputResponse(
        status=result.status.value,
        repair_applied=result.repair_applied,
        violations=[v.model_dump(mode="json") for v in result.violations],
        warnings=result.warnings,
        metadata=result.metadata,
    )


@router.post("/guardrails/injection-check", response_model=InjectionCheckResponse)
async def check_prompt_injection(body: InjectionCheckRequest):
    """Check text for prompt injection attempts."""
    from guardrails.validators.prompt_injection_validator import (
        PromptInjectionValidator,
    )

    validator = PromptInjectionValidator()
    result = await validator.validate(body.content, GuardrailContext())
    detected = result.status == GuardrailResultStatus.REJECTED
    severity = "CRITICAL" if detected else "LOW"
    return InjectionCheckResponse(detected=detected, severity=severity)


@router.post("/guardrails/repair", response_model=RepairOutputResponse)
async def repair_ai_output(body: RepairOutputRequest):
    """Attempt automatic output repair on malformed AI content."""
    engine = GuardrailsEngine()
    result = await engine.execute(body.content, GuardrailContext())
    return RepairOutputResponse(
        repaired=result.repair_applied or result.repaired,
        content=result.repaired_content or body.content,
    )
