"""Test TraceabilityValidator.run_validation facade."""

from agentic_workflow.domain.algorithms.traceability_validator import TraceabilityValidator


class TestRunValidation:
    """Test TraceabilityValidator.run_validation facade."""

    def test_returns_passed_true(self) -> None:
        """Verify validation result PASS."""
        result = TraceabilityValidator.run_validation("FR-001 BG-001")
        assert result["passed"] is True

    def test_empty_content(self) -> None:
        """Verify empty content passes."""
        result = TraceabilityValidator.run_validation("")
        assert result["passed"] is True

    def test_result_structure(self) -> None:
        """Verify result dictionary keys."""
        result = TraceabilityValidator.run_validation("TC-001")
        assert "orphans" in result
        assert "invalid_ids" in result
        assert "next_action" in result
