"""Tests for DAGInvariantVerifier."""

from unittest.mock import MagicMock

from agentic_workflow.domain.algorithms.invariants_verifier import DAGInvariantVerifier


class TestInvariantsVerification:
    """Tests for DAGInvariantVerifier logic."""

    def _make_mock_graph(self, nodes: set[str] | None = None) -> MagicMock:
        mock = MagicMock()
        mock.nodes = nodes or {
            "start_pipeline",
            "orchestrator",
            "auto_gate",
            "advance_stage",
            "iterate_stage",
        }
        return mock

    def test_no_orphan_nodes_passes(self) -> None:
        """TC-269: Orphan nodes check."""
        graph = self._make_mock_graph()
        failures = DAGInvariantVerifier.verify_no_orphan_nodes(graph)
        assert failures == []

    def test_gate_decision_coupling_passes(self) -> None:
        """TC-270: Gate decision coupling."""
        graph = self._make_mock_graph()
        failures = DAGInvariantVerifier.verify_gate_decision_coupling(graph)
        assert failures == []

    def test_iteration_cycle_passes(self) -> None:
        """TC-271: Iteration cycle check."""
        graph = self._make_mock_graph()
        failures = DAGInvariantVerifier.verify_iteration_cycle(graph)
        assert failures == []

    def test_run_all_verifications_passes(self) -> None:
        """TC-272: All invariants run."""
        graph = self._make_mock_graph()
        result = DAGInvariantVerifier.run_all_verifications(graph)
        assert result["passed"] is True
        assert result["failures"] == []
