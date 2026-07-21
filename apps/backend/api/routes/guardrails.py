import logging
from typing import Any
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

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
):
    """Retrieve immutable audit events for a workflow execution."""
    return GuardrailAuditListResponse(items=[], total=0)
