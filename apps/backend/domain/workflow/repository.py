from abc import ABC, abstractmethod
from typing import Optional
import uuid
from domain.workflow.models import WorkflowState


class WorkflowRepository(ABC):
    @abstractmethod
    async def get_by_id(self, workflow_id: uuid.UUID) -> Optional[WorkflowState]:
        """Retrieve a workflow run state by its unique ID."""
        pass

    @abstractmethod
    async def save(self, state: WorkflowState) -> WorkflowState:
        """Save/update a workflow run state."""
        pass

    @abstractmethod
    async def delete(self, workflow_id: uuid.UUID) -> bool:
        """Delete a workflow run record."""
        pass
