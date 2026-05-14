"""CLS-004: TraceableID — Aggregate Root for traceability.

Traceable to: UC-002, UC-004, INV-006, INV-007
INV-006: ID prefix+sequence is globally unique within registry.
INV-007: BG has no upstream; TC has no downstream.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import icontract

from agentic_workflow.domain.models.enums import IDPrefix, LinkType


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
            raise ValueError(
                f"Self-link forbidden: {self.source_id} -> {self.target_id} (INV-008)"
            )


@dataclass
class TraceableID:
    """Aggregate root representing a traceable artifact ID.

    Attributes:
        prefix: ID prefix category (BG, FR, CLS, etc.).
        sequence: Numeric sequence within prefix namespace.
        title: Short human-readable title.
        upstream_links: Links to upstream IDs (parents).
        downstream_links: Links to downstream IDs (children).
    """

    prefix: IDPrefix
    sequence: int
    title: str
    upstream_links: list[TraceLink] = field(default_factory=list)
    downstream_links: list[TraceLink] = field(default_factory=list)

    @property
    def full_id(self) -> str:
        """Return the canonical ID string (e.g., 'FR-001')."""
        return f"{self.prefix.value}-{self.sequence:03d}"

    @icontract.require(
        lambda self: self.prefix != IDPrefix.BG,
        "BG IDs have no upstream links (INV-007)",
    )
    def add_upstream(self, link: TraceLink) -> None:
        """Add an upstream trace link.

        Args:
            link: The upstream TraceLink to add.
        """
        self.upstream_links.append(link)

    @icontract.require(
        lambda self: self.prefix != IDPrefix.TC,
        "TC IDs have no downstream links (INV-007)",
    )
    def add_downstream(self, link: TraceLink) -> None:
        """Add a downstream trace link.

        Args:
            link: The downstream TraceLink to add.
        """
        self.downstream_links.append(link)
