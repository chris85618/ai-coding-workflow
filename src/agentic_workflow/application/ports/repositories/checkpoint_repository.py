"""Port Interface — CheckpointRepository Contract.

Traceable to: FR-019-v2, FR-021-v2, UC-010, ADR-STR-003, ADR-STR-001
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class CheckpointRepository(ABC):
    """Abstract repository for LangGraph DAG checkpoint persistence.

    Traceable to: FR-019-v2, FR-021-v2, UC-010 (workflow resume)
    Implements DAG checkpoint pattern (ADR-STR-003).
    """

    @abstractmethod
    def save_checkpoint(self, pipeline_id: str, state: dict[str, Any]) -> str:
        """Save a pipeline checkpoint and return its identifier.

        Args:
            pipeline_id: Identifier for the pipeline being checkpointed.
            state: LangGraph state dictionary to persist.

        Returns:
            Checkpoint identifier (e.g., timestamp or UUID string).
        """

    @abstractmethod
    def load_latest(self, pipeline_id: str) -> dict[str, Any] | None:
        """Load the most recent checkpoint for a pipeline.

        Args:
            pipeline_id: Identifier for the pipeline to restore.

        Returns:
            State dictionary if a checkpoint exists, else None.
        """

    @abstractmethod
    def list_checkpoints(self, pipeline_id: str) -> list[str]:
        """List all checkpoint identifiers for a pipeline.

        Args:
            pipeline_id: Identifier for the target pipeline.

        Returns:
            List of checkpoint identifiers, newest first.
        """

    @abstractmethod
    def delete_checkpoint(self, pipeline_id: str, checkpoint_id: str) -> bool:
        """Delete a specific checkpoint.

        Args:
            pipeline_id: Pipeline identifier.
            checkpoint_id: Checkpoint identifier to delete.

        Returns:
            True if deleted, False if not found.
        """
