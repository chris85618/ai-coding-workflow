"""Tests for the invariants run script in the frameworks layer (ADR-STR-033)."""

from unittest.mock import patch

from agentic_workflow.domain.algorithms.invariants_verifier import DAGInvariantVerifier


class TestInvariantsRun:
    """Covers the invariants_run execution and pathways."""

    def test_run_verification_pass(self) -> None:
        """TC-012: Invariants run verification pass path over the exported workflow doc."""
        from agentic_workflow.frameworks import invariants_run

        res = invariants_run.run_verification()
        assert res["passed"] is True
        assert len(res["failures"]) == 0

    def test_run_verification_fail(self) -> None:
        """TC-013: Invariants run verification fail path."""
        from agentic_workflow.frameworks import invariants_run

        with patch.object(DAGInvariantVerifier, "verify_no_orphan_nodes", return_value=["bad_node"]):
            res = invariants_run.run_verification()
            assert res["passed"] is False
            assert "bad_node" in res["failures"]

    def test_main_block_via_runpy(self) -> None:
        """TC-014: Invariants run main block via runpy."""
        import os
        import runpy

        from agentic_workflow.frameworks import invariants_run

        file_path = os.path.abspath(invariants_run.__file__)
        try:
            runpy.run_path(file_path, run_name="__main__")
        except SystemExit as e:
            assert e.code == 0

    def test_main_block_fail_via_runpy(self) -> None:
        """TC-015: Invariants run main block fail exit via runpy."""
        import os
        import runpy

        from agentic_workflow.frameworks import invariants_run

        file_path = os.path.abspath(invariants_run.__file__)
        with patch.object(DAGInvariantVerifier, "verify_no_orphan_nodes", return_value=["bad_node"]):
            try:
                runpy.run_path(file_path, run_name="__main__")
            except SystemExit as e:
                assert e.code == 1
