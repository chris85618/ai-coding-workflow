"""Tests for RootCauseLeftShift — 100% statement + branch coverage.
Consolidated from: test_algorithms_coverage.py, test_coverage_gap_fill.py
Traceable to: FR-007, FR-023, ALG
"""
import pytest
from agentic_workflow.domain.algorithms.root_cause_leftshift import (
    RootCauseLeftShift,
    RootCauseAnalysisResult,
    RootCauseCategory,
    InterventionType,
)


class TestAnalyzeFailure:
    """Covers analyze_failure — format branch + default branch."""

    def test_format_error_keyword_maps_to_format_category(self):
        result = RootCauseLeftShift.analyze_failure("format mismatch", [])
        assert result.category == RootCauseCategory.FORMAT_ERROR

    def test_FORMAT_uppercase_maps_to_format(self):
        result = RootCauseLeftShift.analyze_failure("FORMAT error detected", [])
        assert result.category == RootCauseCategory.FORMAT_ERROR

    def test_non_format_keyword_defaults_to_process_gap(self):
        result = RootCauseLeftShift.analyze_failure("coverage issue found", [])
        assert result.category == RootCauseCategory.PROCESS_GAP

    def test_empty_description_defaults_to_process_gap(self):
        result = RootCauseLeftShift.analyze_failure("", [])
        assert result.category == RootCauseCategory.PROCESS_GAP

    def test_result_is_rca_result_type(self):
        result = RootCauseLeftShift.analyze_failure("something", [])
        assert isinstance(result, RootCauseAnalysisResult)

    def test_intervention_type_is_new_guard(self):
        result = RootCauseLeftShift.analyze_failure("something", [])
        assert result.intervention_type == InterventionType.NEW_GUARD

    def test_is_new_lesson_true(self):
        result = RootCauseLeftShift.analyze_failure("something", [])
        assert result.is_new_lesson is True

    def test_bottleneck_location_set(self):
        result = RootCauseLeftShift.analyze_failure("x", [])
        assert result.bottleneck_location == "unknown_step"


class TestCheckLessonReuse:
    """Covers check_lesson_reuse — found branch + not-found branch."""

    def _lessons(self):
        return [
            {"id": "LESSON-001", "category": "FORMAT_ERROR"},
            {"id": "LESSON-002", "category": "PROCESS_GAP"},
        ]

    def test_finds_existing_lesson_by_category(self):
        result = RootCauseLeftShift.check_lesson_reuse(
            RootCauseCategory.FORMAT_ERROR, self._lessons()
        )
        assert result == "LESSON-001"

    def test_finds_process_gap_lesson(self):
        result = RootCauseLeftShift.check_lesson_reuse(
            RootCauseCategory.PROCESS_GAP, self._lessons()
        )
        assert result == "LESSON-002"

    def test_returns_none_when_no_match(self):
        result = RootCauseLeftShift.check_lesson_reuse(
            RootCauseCategory.COVERAGE_GAP, self._lessons()
        )
        assert result is None

    def test_empty_lessons_returns_none(self):
        result = RootCauseLeftShift.check_lesson_reuse(
            RootCauseCategory.FORMAT_ERROR, []
        )
        assert result is None

    def test_lesson_without_category_key_is_skipped(self):
        lessons = [{"id": "LESSON-003"}]  # no category key
        result = RootCauseLeftShift.check_lesson_reuse(
            RootCauseCategory.FORMAT_ERROR, lessons
        )
        assert result is None


class TestGenerateLessonMarkdown:
    """Covers generate_lesson_markdown — full output structure."""

    def _rca(self, category=RootCauseCategory.FORMAT_ERROR,
              intervention=InterventionType.NEW_GUARD,
              location="step_0", lesson_id="LESSON-001", is_new=True):
        return RootCauseAnalysisResult(
            category=category,
            intervention_type=intervention,
            bottleneck_location=location,
            lesson_id=lesson_id,
            is_new_lesson=is_new
        )

    def test_output_contains_lesson_id(self):
        md = RootCauseLeftShift.generate_lesson_markdown(self._rca())
        assert "LESSON-001" in md

    def test_output_contains_category(self):
        md = RootCauseLeftShift.generate_lesson_markdown(self._rca())
        assert "FORMAT_ERROR" in md

    def test_output_contains_intervention_type(self):
        md = RootCauseLeftShift.generate_lesson_markdown(self._rca())
        assert "NEW_GUARD" in md

    def test_output_contains_bottleneck(self):
        md = RootCauseLeftShift.generate_lesson_markdown(self._rca(location="step_3"))
        assert "step_3" in md

    def test_different_category_in_output(self):
        md = RootCauseLeftShift.generate_lesson_markdown(
            self._rca(category=RootCauseCategory.GOVERNANCE_BYPASS)
        )
        assert "GOVERNANCE_BYPASS" in md

    def test_returns_string(self):
        md = RootCauseLeftShift.generate_lesson_markdown(self._rca())
        assert isinstance(md, str)


class TestEnumValues:
    """Verify all enum members are accessible — covers enum class definitions."""

    def test_root_cause_categories(self):
        cats = {c.value for c in RootCauseCategory}
        assert "FORMAT_ERROR" in cats
        assert "COVERAGE_GAP" in cats
        assert "GOVERNANCE_BYPASS" in cats
        assert "DECLARATION_IMPLEMENTATION_GAP" in cats

    def test_intervention_types(self):
        types = {t.value for t in InterventionType}
        assert "GUARD_STRENGTHENING" in types
        assert "NEW_GUARD" in types
        assert "STEP_ADDITION" in types
