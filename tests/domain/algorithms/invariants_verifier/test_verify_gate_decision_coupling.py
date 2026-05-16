"""Tests for DAGInvariantVerifier.verify_gate_decision_coupling logic."""

from typing import Any
from unittest.mock import MagicMock

from agentic_workflow.domain.algorithms.invariants_verifier import DAGInvariantVerifier


def _mock_graph(node_names: dict[str, Any] | None = None) -> MagicMock:
    """Helper: create mock graph."""
    g = MagicMock()
    g.nodes = node_names or {"start": None, "phase_0": None, "gate": None}
    return g


class TestVerifyGateDecisionCoupling:
    """Test DAGInvariantVerifier.verify_gate_decision_coupling logic."""

    def test_returns_empty_list(self) -> None:
        """TC-004: Returns empty list."""
        g = _mock_graph()
        assert DAGInvariantVerifier.verify_gate_decision_coupling(g) == []

    def test_returns_list_type(self) -> None:
        """TC-005: Returns list type."""
        g = _mock_graph()
        assert isinstance(DAGInvariantVerifier.verify_gate_decision_coupling(g), list)
