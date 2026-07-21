from typing import Any
from workflows.state import WorkflowState


class WorkflowCheckpoint:
    """Checkpoint adapter for persisting and recovering workflow state."""

    def __init__(self):
        self._checkpoints: dict[str, dict[str, Any]] = {}

    async def save_checkpoint(self, state: WorkflowState) -> None:
        """Persist current workflow state as a checkpoint."""
        self._checkpoints[state.workflow_id] = state.model_dump()

    async def load_checkpoint(self, workflow_id: str) -> WorkflowState | None:
        """Restore workflow state from the latest checkpoint."""
        data = self._checkpoints.get(workflow_id)
        if data:
            return WorkflowState.model_validate(data)
        return None
