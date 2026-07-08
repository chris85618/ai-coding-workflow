"""Tests for the invariants run script in the frameworks layer — Main Block verification."""


class TestInvariantsRunFineGrained:
    """Covers specific return type and dictionary attributes of run_verification."""

    def test_run_verification_structure(self) -> None:
        """TC-016: Verify run_verification returns required keys."""
        from agentic_workflow.frameworks import invariants_run

        res = invariants_run.run_verification()
        assert isinstance(res, dict)
        assert "passed" in res
        assert "failures" in res
        assert isinstance(res["passed"], bool)
        assert isinstance(res["failures"], list)
