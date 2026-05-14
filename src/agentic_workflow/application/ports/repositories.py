"""Port Interfaces — Repository Contracts.

Traceable to: FR-001, FR-018, ADR-STR-001
Clean Architecture: domain knows nothing about persistence details.
Adapters in adapters/persistence/ implement these interfaces.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_workflow.domain.models.traceable_id import TraceableID


class TraceableIDRepository(ABC):
    """Abstract repository for TraceableID persistence.

    Traceable to: FR-001 (traceability system), UC-011 (full-chain trace)
    """

    @abstractmethod
    def save(self, traceable_id: "TraceableID") -> None:
        """Persist a TraceableID.

        Args:
            traceable_id: The ID object to persist.
        """

    @abstractmethod
    def find_by_id(self, id_str: str) -> "TraceableID | None":
        """Look up a TraceableID by its string identifier.

        Args:
            id_str: The string representation (e.g., "FR-001").

        Returns:
            The TraceableID if found, else None.
        """

    @abstractmethod
    def find_all(self) -> list["TraceableID"]:
        """Return all persisted TraceableIDs.

        Returns:
            List of all stored IDs.
        """

    @abstractmethod
    def delete(self, id_str: str) -> bool:
        """Remove a TraceableID by its string identifier.

        Args:
            id_str: The string representation of the ID to remove.

        Returns:
            True if deleted, False if not found.
        """


class CheckpointRepository(ABC):
    """Abstract repository for LangGraph DAG checkpoint persistence.

    Traceable to: FR-019-v2, FR-021-v2, UC-010 (workflow resume)
    Implements DAG checkpoint pattern (ADR-STR-003).
    """

    @abstractmethod
    def save_checkpoint(self, pipeline_id: str, state: dict) -> str:
        """Save a pipeline checkpoint and return its identifier.

        Args:
            pipeline_id: Identifier for the pipeline being checkpointed.
            state: LangGraph state dictionary to persist.

        Returns:
            Checkpoint identifier (e.g., timestamp or UUID string).
        """

    @abstractmethod
    def load_latest(self, pipeline_id: str) -> dict | None:
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
