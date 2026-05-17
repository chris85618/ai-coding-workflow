"""Use Case — Verify DAG Invariants.

Traceable to: ADR-STR-021, INV-001, INV-002, INV-003
"""

from __future__ import annotations

from typing import Any

from agentic_workflow.application.ports.gateways.graph_builder import IGraphVerifier


class VerifyDAGInvariantsUseCase:
    """Orchestrates formal verification of DAG invariants."""

    def __init__(self, verifier: IGraphVerifier) -> None:
        """Initialize the use case with a verifier gateway."""
        self._verifier = verifier

    def execute(self, graph: Any) -> dict[str, Any]:
        """Execute all structural DAG invariants on the compiled graph."""
        return self._verifier.run_all_verifications(graph)
