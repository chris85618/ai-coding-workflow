"""Traceability System — TraceabilityNode Model.

Traceable to: FR-004
"""

from dataclasses import dataclass, field


@dataclass
class TraceabilityNode:
    """Represents a node in the traceability matrix."""

    id: str
    type: str
    upstream: list[str] = field(default_factory=list)
    downstream: list[str] = field(default_factory=list)
    links: dict[str, list[str]] = field(default_factory=dict)
