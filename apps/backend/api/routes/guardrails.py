import logging
from typing import Any
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from application.guardrails.service import GuardrailApplicationService
from api.dependencies.services import get_guardrail_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Guardrails Audit"])


class GuardrailEventResponse(BaseModel):
    id: str
    workflow_id: str
    validator_name: str
    severity: str
    violation_code: str | None = None
    repaired: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class GuardrailAuditListResponse(BaseModel):
    items: list[GuardrailEventResponse] = Field(default_factory=list)
    total: int = 0


@router.get("/guardrails/events", response_model=GuardrailAuditListResponse)
async def list_guardrail_events(
    workflow_id: str = Query(..., description="Workflow ID to filter events"),
    limit: int = Query(20, ge=1, le=100),
    guardrail_service: GuardrailApplicationService = Depends(get_guardrail_service),
):
    """Retrieve immutable audit events for a workflow execution."""
    events = await guardrail_service.get_events_for_workflow(workflow_id=workflow_id, limit=limit)
    items = [
        GuardrailEventResponse(
            id=str(e.id),
            workflow_id=e.workflow_id,
            validator_name=e.validator_name,
            severity=e.severity,
            violation_code=e.violation_code,
            repaired=e.repaired,
            metadata=e.metadata_json or {},
            created_at=e.created_at.isoformat(),
        )
        for e in events
    ]
    return GuardrailAuditListResponse(items=items, total=len(items))
