"""Entity representing a traceable artifact ID."""

from __future__ import annotations

from dataclasses import dataclass, field

import icontract

from agentic_workflow.domain.enums.id_prefix import IDPrefix
from agentic_workflow.domain.value_objects.trace_link import TraceLink


@dataclass
class TraceableID:
    """Entity representing a traceable artifact ID.

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
        """Add an upstream trace link."""
        self.upstream_links.append(link)

    @icontract.require(
        lambda self: self.prefix != IDPrefix.TC,
        "TC IDs have no downstream links (INV-007)",
    )
    def add_downstream(self, link: TraceLink) -> None:
        """Add a downstream trace link."""
        self.downstream_links.append(link)
