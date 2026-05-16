"""Coverage tests for MicroValidation module."""

from agentic_workflow.domain.algorithms.micro_validation import MicroValidation


class TestMicroValidationCoverage:
    """Tests for ALG-004 MicroValidation."""

    def test_valid_content_passes(self) -> None:
        """TC-221: Valid content verification."""
        result = MicroValidation.run_all("good content", ["FR-001"])
        assert result["passed"] is True
        assert result["failures"] == []
        assert result["prompt_for_agent"] is None

    def test_invalid_format_fails(self) -> None:
        """TC-222: Invalid format detection."""
        result = MicroValidation.run_all("from vibe import magic", [])
        assert result["passed"] is False
        assert any("FORMAT_ERROR" in f for f in result["failures"])
        assert result["prompt_for_agent"] is not None

    def test_validate_format_clean(self) -> None:
        """TC-223: Format clean check."""
        assert MicroValidation.validate_format("clean content") is True

    def test_validate_format_vibe_fails(self) -> None:
        """TC-224: Vibe import detection."""
        assert MicroValidation.validate_format("from vibe import x") is False

    def test_validate_structure_returns_true(self) -> None:
        """TC-225: Structure validation helper."""
        assert MicroValidation.validate_structure(["FR-001"]) is True

    def test_validate_structure_invalid_fails(self) -> None:
        """TC-294: Invalid ID structure detection."""
        assert MicroValidation.validate_structure(["INVALID"]) is False

    def test_next_actions_on_pass(self) -> None:
        """TC-226: Next actions on pass."""
        result = MicroValidation.run_all("valid", [])
        assert any("impact" in a.lower() for a in result["next_actions"])
