"""Unit tests for MicroValidation class — 100% statement + branch coverage.

Supplements: test_micro_validation.py (BDD scenarios for TraceableID/TraceLink)
Traceable to: FR-005, FR-006, FR-007, ALG-002.
"""

from unittest.mock import patch

from agentic_workflow.domain.algorithms.micro_validation import MicroValidation


class TestValidateFormat:
    """Test MicroValidation.validate_format logic."""

    """Covers validate_format — True branch + False branch."""

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
        assert (
            MicroValidation.validate_format("clean code\nfrom vibe import x") is False
        )


class TestValidateStructure:
    """Test MicroValidation.validate_structure logic."""

    """Covers validate_structure — always True (delegated)."""

    def test_valid_ids_returns_true(self) -> None:
        """Verify valid IDs pass structure validation."""
        assert MicroValidation.validate_structure(["FR-001", "BG-001"]) is True

    def test_empty_ids_returns_true(self) -> None:
        """Verify empty IDs pass structure validation."""
        assert MicroValidation.validate_structure([]) is True

    def test_invalid_ids_returns_false(self) -> None:
        """Verify invalid IDs fail structure validation."""
        # Now implemented using TraceabilityValidator
        assert MicroValidation.validate_structure(["INVALID"]) is False


class TestRunAll:
    """Test MicroValidation.run_all facade."""

    """Covers run_all — passed=True + passed=False branches."""

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
        """Covers line 34 — validate_structure False path.

        We patch validate_structure to return False to exercise that branch.
        """
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
