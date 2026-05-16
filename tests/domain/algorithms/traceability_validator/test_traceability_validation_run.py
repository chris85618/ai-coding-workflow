"""Tests for TraceabilityValidator.run_validation facade."""

from agentic_workflow.domain.algorithms.traceability_validator import TraceabilityValidator


class TestTraceabilityValidationRun:
    """Tests for TraceabilityValidator.run_validation facade."""

    def test_run_validation_returns_passed(self) -> None:
        """TC-262: Full traceability validation."""
        result = TraceabilityValidator.run_validation("| FR-001 | BG-001 | ... |")
        assert result["passed"] is True
        assert result["orphans"] == []
