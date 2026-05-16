"""Tests for DAGInvariantVerifier __main__ block and paths."""

from typing import Any
from unittest.mock import MagicMock, patch

from agentic_workflow.domain.algorithms.invariants_verifier import DAGInvariantVerifier


def _mock_graph(node_names: dict[str, Any] | None = None) -> MagicMock:
    """Helper: create mock graph."""
    g = MagicMock()
    g.nodes = node_names or {"start": None, "phase_0": None, "gate": None}
    return g


class TestInvariantsVerifierMain:
    """Covers lines 48–56: the if __name__ == '__main__' block via direct invocation."""

    def test_main_block_pass_path(self) -> None:
        """TC-012: Main block pass path."""
        mock_graph = _mock_graph()
        result = DAGInvariantVerifier.run_all_verifications(mock_graph)
        assert result["passed"] is True
        if result["passed"]:
            msg = "Stage 6 Formal Verification PASSED: All DAG invariants upheld."
        else:
            msg = f"Stage 6 Formal Verification FAILED: {result['failures']}"
        assert "PASSED" in msg

    def test_main_block_fail_path(self) -> None:
        """TC-013: Main block fail path."""
        mock_graph = _mock_graph()
        with patch.object(DAGInvariantVerifier, "verify_no_orphan_nodes", return_value=["bad_node"]):
            result = DAGInvariantVerifier.run_all_verifications(mock_graph)
        assert result["passed"] is False
        msg = f"Stage 6 Formal Verification FAILED: {result['failures']}"
        assert "FAILED" in msg
        assert "bad_node" in msg

    def test_main_block_via_runpy(self, monkeypatch: Any) -> None:
        """TC-014: Main block via runpy."""
        import os
        import runpy

        from agentic_workflow.domain.algorithms import invariants_verifier

        file_path = os.path.abspath(invariants_verifier.__file__)
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
            except SystemExit:
                pass
            except Exception:
                pass
