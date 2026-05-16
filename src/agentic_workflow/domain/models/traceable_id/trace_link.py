"""CLS-005: TraceLink — A directional trace link between two TraceableIDs.

Traceable to: INV-008, INV-009
INV-008: source != target (no self-link).
INV-009: link_type must be valid for source→target prefix pair.
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_workflow.domain.models.enums.link_type import LinkType


@dataclass
class TraceLink:
    """CLS-005: A directional trace link between two TraceableIDs.

    Traceable to: INV-008, INV-009
    INV-008: source != target (no self-link).
    INV-009: link_type must be valid for source→target prefix pair.

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
