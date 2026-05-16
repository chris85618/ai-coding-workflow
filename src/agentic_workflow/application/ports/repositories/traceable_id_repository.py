"""Port Interface — TraceableIDRepository Contract.

Traceable to: FR-001, FR-018, ADR-STR-001
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_workflow.domain.entities.traceable_id import TraceableID


class TraceableIDRepository(ABC):
    """Abstract repository for TraceableID persistence.

    Traceable to: FR-001 (traceability system), UC-011 (full-chain trace)
    """

    @abstractmethod
    def save(self, traceable_id: TraceableID) -> None:
        """Persist a TraceableID.

        Args:
            traceable_id: The ID object to persist.
        """

    @abstractmethod
    def find_by_id(self, id_str: str) -> TraceableID | None:
        """Look up a TraceableID by its string identifier.

        Args:
            id_str: The string representation (e.g., "FR-001").

        Returns:
            The TraceableID if found, else None.
        """

    @abstractmethod
    def find_all(self) -> list[TraceableID]:
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
