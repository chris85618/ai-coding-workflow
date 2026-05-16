"""Test TraceabilityValidator.validate_id_format logic."""

from agentic_workflow.domain.algorithms.traceability_validator import TraceabilityValidator


class TestValidateIdFormat:
    """Test TraceabilityValidator.validate_id_format logic."""

    def test_valid_fr_id(self) -> None:
        """Verify valid FR ID format."""
        assert TraceabilityValidator.validate_id_format("FR-001") is True

    def test_valid_bg_id(self) -> None:
        """Verify valid BG ID format."""
        assert TraceabilityValidator.validate_id_format("BG-001") is True

    def test_valid_adr_str(self) -> None:
        """Verify valid ADR-STR ID format."""
        assert TraceabilityValidator.validate_id_format("ADR-STR-001") is True

    def test_valid_tc(self) -> None:
        """Verify valid TC ID format."""
        assert TraceabilityValidator.validate_id_format("TC-099") is True

    def test_invalid_missing_number(self) -> None:
        """Verify invalid ID with missing number."""
        assert TraceabilityValidator.validate_id_format("FR-") is False

    def test_invalid_bad_prefix(self) -> None:
        """Verify invalid ID with bad prefix."""
        assert TraceabilityValidator.validate_id_format("XX-001") is False

    def test_invalid_no_dash(self) -> None:
        """Verify invalid ID with missing dash."""
        assert TraceabilityValidator.validate_id_format("FR001") is False

    def test_invalid_empty_string(self) -> None:
        """Verify empty string is invalid."""
        assert TraceabilityValidator.validate_id_format("") is False
