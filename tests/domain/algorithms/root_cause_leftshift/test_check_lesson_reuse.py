"""Test RootCauseLeftShift.check_lesson_reuse logic."""

from typing import Any

from agentic_workflow.domain.algorithms.root_cause_leftshift import (
    RootCauseCategory,
    RootCauseLeftShift,
)


class TestCheckLessonReuse:
    """Test RootCauseLeftShift.check_lesson_reuse logic."""

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
