"""Traceability System — TraceabilityNode Model.

Traceable to: FR-004
"""

from pydantic import BaseModel


class TraceabilityNode(BaseModel):
    """Represents a node in the traceability matrix."""

    id: str
    type: str
    upstream: list[str] = []
    downstream: list[str] = []
    links: dict[str, list[str]] = {}
