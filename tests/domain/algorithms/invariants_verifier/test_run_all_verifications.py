"""Tests for DAGInvariantVerifier.run_all_verifications facade."""

from typing import Any
from unittest.mock import MagicMock, patch

from agentic_workflow.domain.algorithms.invariants_verifier import DAGInvariantVerifier


def _mock_graph(node_names: dict[str, Any] | None = None) -> MagicMock:
    """Helper: create mock graph."""
    g = MagicMock()
    g.nodes = node_names or {"start": None, "phase_0": None, "gate": None}
    return g


class TestRunAllVerifications:
    """Test DAGInvariantVerifier.run_all_verifications facade."""

    def test_all_pass_returns_passed_true(self) -> None:
        """TC-008: All pass returns passed=True."""
        g = _mock_graph()
        result = DAGInvariantVerifier.run_all_verifications(g)
        assert result["passed"] is True
        assert result["failures"] == []

    def test_result_structure(self) -> None:
        """TC-009: Verify result structure."""
        g = _mock_graph()
        result = DAGInvariantVerifier.run_all_verifications(g)
        assert "passed" in result
        assert "failures" in result

    def test_with_failures_returns_passed_false(self) -> None:
        """TC-010: Failure returns passed=False."""
        g = _mock_graph()
        with patch.object(DAGInvariantVerifier, "verify_no_orphan_nodes", return_value=["orphan_node"]):
            result = DAGInvariantVerifier.run_all_verifications(g)
        assert result["passed"] is False
        assert "orphan_node" in result["failures"]

    def test_multiple_failures_accumulated(self) -> None:
        """TC-011: Accumulates multiple failures."""
        g = _mock_graph()
        with (
            patch.object(DAGInvariantVerifier, "verify_no_orphan_nodes", return_value=["n1"]),
            patch.object(
                DAGInvariantVerifier,
                "verify_gate_decision_coupling",
                return_value=["g1"],
            ),
            patch.object(DAGInvariantVerifier, "verify_iteration_cycle", return_value=["c1"]),
        ):
            result = DAGInvariantVerifier.run_all_verifications(g)
        assert result["passed"] is False
        assert len(result["failures"]) == 3
