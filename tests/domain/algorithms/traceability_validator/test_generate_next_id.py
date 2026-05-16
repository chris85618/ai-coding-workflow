"""Covers all branches: prefix match/no-match, num>max/num<=max, ValueError."""

from agentic_workflow.domain.algorithms.traceability_validator import TraceabilityValidator


class TestGenerateNextId:
    """Covers all branches: prefix match/no-match, num>max/num<=max, ValueError."""

    def test_no_existing_ids_starts_at_001(self) -> None:
        """Verify sequence start at 001."""
        result = TraceabilityValidator.generate_next_id("FR", [])
        assert result == "FR-001"

    def test_existing_ids_increments(self) -> None:
        """Verify sequence increment."""
        result = TraceabilityValidator.generate_next_id("FR", ["FR-001", "FR-002"])
        assert result == "FR-003"

    def test_skips_different_prefix(self) -> None:
        """Verify different prefix skip logic."""
        result = TraceabilityValidator.generate_next_id("FR", ["BG-001", "BG-005"])
        assert result == "FR-001"

    def test_num_not_greater_than_max(self) -> None:
        """Verify max number tracking."""
        result = TraceabilityValidator.generate_next_id("FR", ["FR-005", "FR-003"])
        assert result == "FR-006"

    def test_value_error_continue(self) -> None:
        """Verify robustness against non-numeric suffixes."""
        result = TraceabilityValidator.generate_next_id("FR", ["FR-abc", "FR-002"])
        assert result == "FR-003"

    def test_mixed_valid_invalid(self) -> None:
        """Verify mixed ID handling."""
        result = TraceabilityValidator.generate_next_id("TC", ["TC-010", "TC-bad", "FR-020"])
        assert result == "TC-011"

    def test_three_digit_padding(self) -> None:
        """Verify zero padding."""
        result = TraceabilityValidator.generate_next_id("BG", ["BG-009"])
        assert result == "BG-010"
