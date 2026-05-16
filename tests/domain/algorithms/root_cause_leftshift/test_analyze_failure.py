"""Test RootCauseLeftShift.analyze_failure logic."""

from agentic_workflow.domain.algorithms.root_cause_leftshift import (
    InterventionType,
    RootCauseAnalysisResult,
    RootCauseCategory,
    RootCauseLeftShift,
)


class TestAnalyzeFailure:
    """Test RootCauseLeftShift.analyze_failure logic."""

    def test_format_error_keyword_maps_to_format_category(self) -> None:
        """Verify 'format' keyword detection."""
        result = RootCauseLeftShift.analyze_failure("format mismatch", [])
        assert result.category == RootCauseCategory.FORMAT_ERROR

    def test_format_uppercase_maps_to_format(self) -> None:
        """Verify case-insensitive 'FORMAT' detection."""
        result = RootCauseLeftShift.analyze_failure("FORMAT error detected", [])
        assert result.category == RootCauseCategory.FORMAT_ERROR

    def test_non_format_keyword_defaults_to_process_gap(self) -> None:
        """Verify default category mapping."""
        result = RootCauseLeftShift.analyze_failure("coverage issue found", [])
        assert result.category == RootCauseCategory.PROCESS_GAP

    def test_empty_description_defaults_to_process_gap(self) -> None:
        """Verify empty input handling."""
        result = RootCauseLeftShift.analyze_failure("", [])
        assert result.category == RootCauseCategory.PROCESS_GAP

    def test_result_is_rca_result_type(self) -> None:
        """Verify result class type."""
        result = RootCauseLeftShift.analyze_failure("something", [])
        assert isinstance(result, RootCauseAnalysisResult)

    def test_intervention_type_is_new_guard(self) -> None:
        """Verify default intervention type."""
        result = RootCauseLeftShift.analyze_failure("something", [])
        assert result.intervention_type == InterventionType.NEW_GUARD

    def test_is_new_lesson_true(self) -> None:
        """Verify is_new_lesson default."""
        result = RootCauseLeftShift.analyze_failure("something", [])
        assert result.is_new_lesson is True

    def test_bottleneck_location_set(self) -> None:
        """Verify default bottleneck location."""
        result = RootCauseLeftShift.analyze_failure("x", [])
        assert result.bottleneck_location == "unknown_step"
