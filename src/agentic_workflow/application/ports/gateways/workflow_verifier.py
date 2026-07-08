"""Port Interface — Workflow Verifier Abstraction.

Traceable to: ADR-STR-021, ADR-STR-033, INV-001, INV-002, INV-003
Engine-neutral verification contract: the subject is the exported
workflow topology (Archon document) or a workflow state snapshot.
"""

from __future__ import annotations

from typing import Any, Protocol


class IGraphVerifier(Protocol):
    """Protocol interface for formal workflow verification."""

    @classmethod
    def run_all_verifications(cls, graph: Any) -> dict[str, Any]:
        """Verify the workflow topology/state and return results."""
