import logging
from typing import Sequence, Optional
from infrastructure.repositories.guardrail_repository import GuardrailRepositoryImpl
from infrastructure.database.guardrail_models import GuardrailEventModel

logger = logging.getLogger(__name__)


class GuardrailApplicationService:
    """Application Service providing read-only queries for guardrail audit events."""

    def __init__(self, guardrail_repo: Optional[GuardrailRepositoryImpl] = None):
        self.guardrail_repo = guardrail_repo

    async def get_events_for_workflow(self, workflow_id: str, limit: int = 20) -> Sequence[GuardrailEventModel]:
        if self.guardrail_repo:
            return await self.guardrail_repo.list_by_workflow(workflow_id=workflow_id, limit=limit)
        return []
