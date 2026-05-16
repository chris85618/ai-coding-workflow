"""Tests for RootCauseLeftShift — 100% statement + branch coverage.

Consolidated from: test_algorithms_coverage.py, test_coverage_gap_fill.py
Traceable to: FR-007, FR-023, ALG.
"""

from typing import Any

from agentic_workflow.domain.algorithms.root_cause_leftshift import (
    InterventionType,
    RootCauseAnalysisResult,
    RootCauseCategory,
    RootCauseLeftShift,
)


class TestAnalyzeFailure:
    """Test RootCauseLeftShift.analyze_failure logic."""

    """Covers analyze_failure — format branch + default branch."""

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


class TestCheckLessonReuse:
    """Test RootCauseLeftShift.check_lesson_reuse logic."""

    """Covers check_lesson_reuse — found branch + not-found branch."""

    def _lessons(self) -> list[dict[str, Any]]:
        """Helper to create test lessons."""
        return [
            {"id": "LESSON-001", "category": "FORMAT_ERROR"},
            {"id": "LESSON-002", "category": "PROCESS_GAP"},
        ]

    def test_finds_existing_lesson_by_category(self) -> None:
        """Verify lesson reuse by category."""
        result = RootCauseLeftShift.check_lesson_reuse(RootCauseCategory.FORMAT_ERROR, self._lessons())
        assert result == "LESSON-001"

    def test_finds_process_gap_lesson(self) -> None:
        """Verify PROCESS_GAP reuse."""
        result = RootCauseLeftShift.check_lesson_reuse(RootCauseCategory.PROCESS_GAP, self._lessons())
        assert result == "LESSON-002"

    def test_returns_none_when_no_match(self) -> None:
        """Verify None returned when no match."""
        result = RootCauseLeftShift.check_lesson_reuse(RootCauseCategory.COVERAGE_GAP, self._lessons())
        assert result is None

    def test_empty_lessons_returns_none(self) -> None:
        """Verify empty lesson list handling."""
        result = RootCauseLeftShift.check_lesson_reuse(RootCauseCategory.FORMAT_ERROR, [])
        assert result is None

    def test_lesson_without_category_key_is_skipped(self) -> None:
        """Verify robustness against malformed lesson data."""
        lessons = [{"id": "LESSON-003"}]  # no category key
        result = RootCauseLeftShift.check_lesson_reuse(RootCauseCategory.FORMAT_ERROR, lessons)
        assert result is None


class TestGenerateLessonMarkdown:
    """Test RootCauseLeftShift.generate_lesson_markdown logic."""

    """Covers generate_lesson_markdown — full output structure."""

    def _rca(
        self,
        category: RootCauseCategory = RootCauseCategory.FORMAT_ERROR,
        intervention: InterventionType = InterventionType.NEW_GUARD,
        location: str = "step_0",
        lesson_id: str = "LESSON-001",
        is_new: bool = True,
    ) -> RootCauseAnalysisResult:
        """Helper to create RCA result."""
        return RootCauseAnalysisResult(
            category=category,
            intervention_type=intervention,
            bottleneck_location=location,
            lesson_id=lesson_id,
            is_new_lesson=is_new,
        )

    def test_output_contains_lesson_id(self) -> None:
        """Verify markdown contains ID."""
        md = RootCauseLeftShift.generate_lesson_markdown(self._rca())
        assert "LESSON-001" in md

    def test_output_contains_category(self) -> None:
        """Verify markdown contains category."""
        md = RootCauseLeftShift.generate_lesson_markdown(self._rca())
        assert "FORMAT_ERROR" in md

    def test_output_contains_intervention_type(self) -> None:
        """Verify markdown contains intervention type."""
        md = RootCauseLeftShift.generate_lesson_markdown(self._rca())
        assert "NEW_GUARD" in md

    def test_output_contains_bottleneck(self) -> None:
        """Verify markdown contains bottleneck location."""
        md = RootCauseLeftShift.generate_lesson_markdown(self._rca(location="step_3"))
        assert "step_3" in md

    def test_different_category_in_output(self) -> None:
        """Verify markdown handles different categories."""
        md = RootCauseLeftShift.generate_lesson_markdown(self._rca(category=RootCauseCategory.GOVERNANCE_BYPASS))
        assert "GOVERNANCE_BYPASS" in md

    def test_returns_string(self) -> None:
        """Verify output is string."""
        md = RootCauseLeftShift.generate_lesson_markdown(self._rca())
        assert isinstance(md, str)


class TestEnumValues:
    """Test Enum values and accessibility."""

    """Verify all enum members are accessible — covers enum class definitions."""

    def test_root_cause_categories(self) -> None:
        """Verify enum values for categories."""
        cats = {c.value for c in RootCauseCategory}
        assert "FORMAT_ERROR" in cats
        assert "COVERAGE_GAP" in cats
        assert "GOVERNANCE_BYPASS" in cats
        assert "DECLARATION_IMPLEMENTATION_GAP" in cats

    def test_intervention_types(self) -> None:
        """Verify enum values for interventions."""
        types = {t.value for t in InterventionType}
        assert "GUARD_STRENGTHENING" in types
        assert "NEW_GUARD" in types
        assert "STEP_ADDITION" in types
