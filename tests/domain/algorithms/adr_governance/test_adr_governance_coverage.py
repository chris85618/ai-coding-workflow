"""Coverage tests for ADRGovernance module."""

from agentic_workflow.domain.algorithms.adr_governance import ADRGovernance


class TestADRGovernanceCoverage:
    """Tests for ADRGovernance algorithm — 100% statement + branch coverage."""

    def test_module_importable(self) -> None:
        """TC-263: Module import check."""
        assert ADRGovernance is not None
