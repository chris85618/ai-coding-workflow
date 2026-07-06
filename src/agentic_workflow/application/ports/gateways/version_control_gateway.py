"""Port Interface — Version Control Gateway (degradation path).

Traceable to: FR-069, ADR-STR-029, FEA-030
Application-layer abstraction so the rollback degradation path never touches
git or subprocess machinery directly (DIP, ADR-STR-027).
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class IVersionControlGateway(ABC):
    """Abstract interface for version-control rollback operations."""

    @abstractmethod
    def current_ref(self) -> str:
        """Return the current commit reference."""

    @abstractmethod
    def rollback_to(self, ref: str) -> bool:
        """Hard-reset the working tree to ref; True on success."""

    @abstractmethod
    def tag_universal_base(self) -> str:
        """Tag the current commit as the universal base and return the tag name."""
