"""Tests for the invariants run script in the frameworks layer — Main Block verification."""

from unittest.mock import MagicMock, patch


def _mock_graph() -> MagicMock:
    """Helper: create mock graph."""
    g = MagicMock()
    g.nodes = {"start": None, "phase_0": None, "gate": None}
    return g


class TestInvariantsRunFineGrained:
    """Covers specific return type and dictionary attributes of run_verification."""

    def test_run_verification_structure(self) -> None:
        """TC-016: Verify run_verification returns required keys."""
        from agentic_workflow.frameworks.graph import invariants_run

        mock_graph = _mock_graph()
        with patch(
            "agentic_workflow.frameworks.graph.master_graph_builder.MasterGraphBuilder.build",
            return_value=mock_graph,
        ):
            res = invariants_run.run_verification()
            assert isinstance(res, dict)
            assert "passed" in res
            assert "failures" in res
            assert isinstance(res["passed"], bool)
            assert isinstance(res["failures"], list)
