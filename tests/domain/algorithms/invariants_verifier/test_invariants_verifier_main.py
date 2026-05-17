"""Tests for the invariants run script in the frameworks layer."""

from typing import Any
from unittest.mock import MagicMock, patch

from agentic_workflow.domain.algorithms.invariants_verifier import DAGInvariantVerifier


def _mock_graph(node_names: dict[str, Any] | None = None) -> MagicMock:
    """Helper: create mock graph."""
    g = MagicMock()
    g.nodes = node_names or {"start": None, "phase_0": None, "gate": None}
    return g


class TestInvariantsRun:
    """Covers the invariants_run execution and pathways."""

    def test_run_verification_pass(self) -> None:
        """TC-012: Invariants run verification pass path."""
        from agentic_workflow.frameworks.graph import invariants_run

        mock_graph = _mock_graph()
        with patch(
            "agentic_workflow.frameworks.graph.master_graph_builder.MasterGraphBuilder.build",
            return_value=mock_graph,
        ):
            res = invariants_run.run_verification()
            assert res["passed"] is True
            assert len(res["failures"]) == 0

    def test_run_verification_fail(self) -> None:
        """TC-013: Invariants run verification fail path."""
        from agentic_workflow.frameworks.graph import invariants_run

        mock_graph = _mock_graph()
        with (
            patch(
                "agentic_workflow.frameworks.graph.master_graph_builder.MasterGraphBuilder.build",
                return_value=mock_graph,
            ),
            patch.object(DAGInvariantVerifier, "verify_no_orphan_nodes", return_value=["bad_node"]),
        ):
            res = invariants_run.run_verification()
            assert res["passed"] is False
            assert "bad_node" in res["failures"]

    def test_main_block_via_runpy(self) -> None:
        """TC-014: Invariants run main block via runpy."""
        import os
        import runpy

        from agentic_workflow.frameworks.graph import invariants_run

        file_path = os.path.abspath(invariants_run.__file__)
        mock_graph = _mock_graph()
        with patch(
            "agentic_workflow.frameworks.graph.master_graph_builder.MasterGraphBuilder.build",
            return_value=mock_graph,
        ):
            try:
                runpy.run_path(
                    file_path,
                    run_name="__main__",
                )
            except SystemExit as e:
                assert e.code == 0

    def test_main_block_fail_via_runpy(self) -> None:
        """TC-015: Invariants run main block fail exit via runpy."""
        import os
        import runpy

        from agentic_workflow.frameworks.graph import invariants_run

        file_path = os.path.abspath(invariants_run.__file__)
        mock_graph = _mock_graph()
        with (
            patch(
                "agentic_workflow.frameworks.graph.master_graph_builder.MasterGraphBuilder.build",
                return_value=mock_graph,
            ),
            patch.object(DAGInvariantVerifier, "verify_no_orphan_nodes", return_value=["bad_node"]),
        ):
            try:
                runpy.run_path(
                    file_path,
                    run_name="__main__",
                )
            except SystemExit as e:
                assert e.code == 1
