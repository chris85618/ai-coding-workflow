"""Tests for MicroValidation.validate_format."""

from agentic_workflow.domain.algorithms.micro_validation import MicroValidation


class TestValidateFormat:
    """Test MicroValidation.validate_format logic."""

    def test_clean_content_returns_true(self) -> None:
        """Verify clean content passes format validation."""
        assert MicroValidation.validate_format("normal content here") is True

    def test_vibe_import_returns_false(self) -> None:
        """Verify vibe import fails format validation."""
        assert MicroValidation.validate_format("from vibe import something") is False

    def test_empty_string_returns_true(self) -> None:
        """Verify empty string passes format validation."""
        assert MicroValidation.validate_format("") is True

    def test_partial_match_not_triggered(self) -> None:
        """Verify partial match does not trigger failure."""
        # "fromvibe" without space should not trigger
        assert MicroValidation.validate_format("fromvibe import") is True

    def test_mixed_content_with_vibe(self) -> None:
        """Verify mixed content with vibe fails."""
        assert MicroValidation.validate_format("clean code\nfrom vibe import x") is False
