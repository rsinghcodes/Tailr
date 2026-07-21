import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.guardrail_models import GuardrailEventModel


class GuardrailRepositoryImpl:
    """Repository for persisting and querying guardrail audit events."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def record_event(
        self,
        workflow_id: str,
        validator_name: str,
        severity: str,
        violation_code: str | None = None,
        repaired: bool = False,
        metadata: dict | None = None,
    ) -> GuardrailEventModel:
        db_event = GuardrailEventModel(
            id=uuid.uuid4(),
            workflow_id=workflow_id,
            validator_name=validator_name,
            severity=severity,
            violation_code=violation_code,
            repaired=repaired,
            metadata_json=metadata or {},
        )
        self.session.add(db_event)
        await self.session.flush()
        return db_event

    async def list_by_workflow(self, workflow_id: str, limit: int = 50) -> Sequence[GuardrailEventModel]:
        stmt = (
            select(GuardrailEventModel)
            .where(GuardrailEventModel.workflow_id == workflow_id)
            .order_by(GuardrailEventModel.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
