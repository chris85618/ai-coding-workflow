"""Tests for TraceabilityValidator ID format validation."""

from agentic_workflow.domain.algorithms.traceability_validator import TraceabilityValidator


class TestIdFormatValidation:
    """Tests for ALG-012 TraceabilityValidator ID format logic."""

    def test_valid_id_format(self) -> None:
        """TC-251: Valid ID format."""
        assert TraceabilityValidator.validate_id_format("FR-001") is True

    def test_invalid_id_format_no_prefix(self) -> None:
        """TC-252: Invalid ID prefix."""
        assert TraceabilityValidator.validate_id_format("INVALID-001") is False

    def test_invalid_id_format_no_num(self) -> None:
        """TC-253: Invalid ID number suffix."""
        assert TraceabilityValidator.validate_id_format("FR-abc") is False

    def test_valid_adr_gov(self) -> None:
        """TC-254: ADR-GOV ID format."""
        assert TraceabilityValidator.validate_id_format("ADR-GOV-001") is True

    def test_valid_adr_str(self) -> None:
        """TC-255: ADR-STR ID format."""
        assert TraceabilityValidator.validate_id_format("ADR-STR-001") is True
