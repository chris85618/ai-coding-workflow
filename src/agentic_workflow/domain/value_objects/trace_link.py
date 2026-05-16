"""Value Object for a directional trace link between two TraceableIDs."""

from __future__ import annotations

from dataclasses import dataclass

from agentic_workflow.domain.enums.link_type import LinkType


@dataclass(frozen=True)
class TraceLink:
    """A directional trace link between two TraceableIDs.

    Attributes:
        source_id: Source node identifier string.
        target_id: Target node identifier string.
        link_type: Relationship type.
    """

    source_id: str
    target_id: str
    link_type: LinkType

    def __post_init__(self) -> None:
        """Enforce no-self-link invariant (INV-008)."""
        if self.source_id == self.target_id:
            raise ValueError(f"Self-link forbidden: {self.source_id} -> {self.target_id} (INV-008)")
