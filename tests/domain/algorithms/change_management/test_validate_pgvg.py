"""Tests for PGVG validation logic."""

from agentic_workflow.domain.algorithms.change_management import (
    ChangeManagement,
    ChangeType,
)


class TestValidatePGVG:
    """Tests for PGVG validation logic."""

    def test_valid_content_returns_no_failures(self) -> None:
        """TC-131: Valid content check."""
        result = ChangeManagement.validate_pgvg("Normal content without issues.", "original", ChangeType.MODIFY)
        assert result == []

    def test_unbalanced_backticks_returns_failure(self) -> None:
        """TC-132: Unbalanced backticks detection."""
        result = ChangeManagement.validate_pgvg("```code without closing", "original", ChangeType.CREATE)
        assert any("backtick" in f for f in result)

    def test_even_backticks_are_fine(self) -> None:
        """TC-133: Balanced backticks check."""
        result = ChangeManagement.validate_pgvg("```code``` and ```more```", "original", ChangeType.FIX)
        assert result == []

    def test_create_change_type_accepted(self) -> None:
        """TC-134: CREATE type validation."""
        result = ChangeManagement.validate_pgvg("clean content", "orig", ChangeType.CREATE)
        assert isinstance(result, list)

    def test_fix_change_type_accepted(self) -> None:
        """TC-135: FIX type validation."""
        result = ChangeManagement.validate_pgvg("clean content", "orig", ChangeType.FIX)
        assert isinstance(result, list)
