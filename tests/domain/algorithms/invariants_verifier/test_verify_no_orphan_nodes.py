"""Tests for DAGInvariantVerifier.verify_no_orphan_nodes logic."""

from typing import Any
from unittest.mock import MagicMock

from agentic_workflow.domain.algorithms.invariants_verifier import DAGInvariantVerifier


def _mock_graph(node_names: dict[str, Any] | None = None) -> MagicMock:
    """Helper: create mock graph."""
    g = MagicMock()
    g.nodes = node_names or {"start": None, "phase_0": None, "gate": None}
    return g


class TestVerifyNoOrphanNodes:
    """Test DAGInvariantVerifier.verify_no_orphan_nodes logic."""

    def test_returns_empty_list_for_valid_graph(self) -> None:
        """TC-001: Returns empty list for valid graph."""
        g = _mock_graph()
        result = DAGInvariantVerifier.verify_no_orphan_nodes(g)
        assert result == []

    def test_returns_list_type(self) -> None:
        """TC-002: Returns list type."""
        g = _mock_graph()
        assert isinstance(DAGInvariantVerifier.verify_no_orphan_nodes(g), list)

    def test_accesses_nodes_attribute(self) -> None:
        """TC-003: Accesses nodes attribute."""
        g = _mock_graph({"alpha": None, "beta": None})
        result = DAGInvariantVerifier.verify_no_orphan_nodes(g)
        assert result == []
