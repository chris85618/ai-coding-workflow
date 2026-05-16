"""Test suite for readiness completion checks."""

from agentic_workflow.domain.algorithms.completion_check import CompletionCheck


class TestCompletionCheckLogic:
    """Test suite for readiness completion checks."""

    def test_ready_when_all_green(self) -> None:
        """TC-001: All green returns ready=True."""
        result = CompletionCheck.verify_readiness(1.00, 0, 0)
        assert result["ready"] is True
        assert result["failures"] == []

    def test_fails_on_low_coverage(self) -> None:
        """TC-002: Low coverage blocks readiness."""
        result = CompletionCheck.verify_readiness(0.999, 0, 0)
        assert result["ready"] is False
        assert any("coverage" in f.lower() for f in result["failures"])

    def test_fails_on_open_risks(self) -> None:
        """TC-003: Open risks block readiness."""
        result = CompletionCheck.verify_readiness(1.00, 2, 0)
        assert result["ready"] is False
        assert any("risk" in f.lower() for f in result["failures"])

    def test_exactly_at_threshold_is_ready(self) -> None:
        """TC-004: Exactly at threshold is ready."""
        result = CompletionCheck.verify_readiness(1.00, 0, 0)
        assert result["ready"] is True

    def test_pending_debts_blocks_in_strict_mode(self) -> None:
        """TC-005: Technical debt blocks readiness."""
        result = CompletionCheck.verify_readiness(1.00, 0, 1)
        assert result["ready"] is False
        assert any("debt" in f.lower() for f in result["failures"])

    def test_oo_class_verify_readiness(self) -> None:
        """TC-006: Class method verify_readiness works directly."""
        result = CompletionCheck.verify_readiness(1.00, 0, 0)
        assert result["ready"] is True
