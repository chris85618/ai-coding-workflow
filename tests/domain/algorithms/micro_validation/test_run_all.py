"""Tests for MicroValidation.run_all facade."""

from unittest.mock import patch

from agentic_workflow.domain.algorithms.micro_validation import MicroValidation


class TestRunAll:
    """Test MicroValidation.run_all facade."""

    def test_clean_content_passes(self) -> None:
        """Verify clean content passes all validations."""
        result = MicroValidation.run_all("valid content", ["FR-001"])
        assert result["passed"] is True
        assert result["failures"] == []

    def test_vibe_content_fails(self) -> None:
        """Verify vibe content fails in run_all."""
        result = MicroValidation.run_all("from vibe import x", ["FR-001"])
        assert result["passed"] is False
        assert len(result["failures"]) == 1
        assert "FORMAT_ERROR" in result["failures"][0]

    def test_passed_next_actions_include_impact(self) -> None:
        """Verify next actions on success include impact analysis."""
        result = MicroValidation.run_all("clean", [])
        assert any("impact" in a.lower() for a in result["next_actions"])

    def test_failed_next_actions_include_rework(self) -> None:
        """Verify next actions on failure include rework."""
        result = MicroValidation.run_all("from vibe import x", [])
        assert "rework" in result["next_actions"]

    def test_passed_prompt_is_none(self) -> None:
        """Verify prompt for agent is None on success."""
        result = MicroValidation.run_all("clean content", ["FR-001"])
        assert result["prompt_for_agent"] is None

    def test_failed_prompt_contains_failure_detail(self) -> None:
        """Verify prompt for agent contains failure detail on error."""
        result = MicroValidation.run_all("from vibe import x", [])
        assert result["prompt_for_agent"] is not None
        assert "FORMAT_ERROR" in result["prompt_for_agent"]

    def test_validate_structure_false_branch(self) -> None:
        """Covers line 34 — validate_structure False path."""
        with patch.object(MicroValidation, "validate_structure", return_value=False):
            result = MicroValidation.run_all("valid content", ["BAD"])
        assert result["passed"] is False
        assert any("STRUCTURAL_ERROR" in f for f in result["failures"])

    def test_result_structure_keys(self) -> None:
        """Verify result dictionary has expected keys."""
        result = MicroValidation.run_all("content", [])
        assert set(result.keys()) == {
            "passed",
            "failures",
            "next_actions",
            "prompt_for_agent",
        }

    def test_both_checks_fail(self) -> None:
        """Covers both FORMAT and STRUCTURAL failures in same run."""
        with patch.object(MicroValidation, "validate_structure", return_value=False):
            result = MicroValidation.run_all("from vibe import x", ["BAD"])
        assert result["passed"] is False
        assert len(result["failures"]) == 2
