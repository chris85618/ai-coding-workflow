"""Test RootCauseLeftShift.generate_lesson_markdown logic."""

from agentic_workflow.domain.algorithms.root_cause_leftshift import (
    InterventionType,
    RootCauseAnalysisResult,
    RootCauseCategory,
    RootCauseLeftShift,
)


class TestGenerateLessonMarkdown:
    """Test RootCauseLeftShift.generate_lesson_markdown logic."""

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
