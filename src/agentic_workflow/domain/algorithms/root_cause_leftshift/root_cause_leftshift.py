"""Root Cause Left-Shift — RootCauseLeftShift Algorithm class.

Traceable to: FR-007, FR-023
Replaces: skills/workflow-skills/root-cause-leftshift.md
"""

from typing import Any

import deal

from agentic_workflow.domain.algorithms.root_cause_leftshift.intervention_type import (
    InterventionType,
)
from agentic_workflow.domain.algorithms.root_cause_leftshift.root_cause_analysis_result import (
    RootCauseAnalysisResult,
)
from agentic_workflow.domain.algorithms.root_cause_leftshift.root_cause_category import (
    RootCauseCategory,
)


class RootCauseLeftShift:
    """Performs Root Cause Analysis and Left-Shift guard implementation."""

    @classmethod
    @deal.post(
        lambda result: isinstance(result, RootCauseAnalysisResult),
        message="RCA must yield a structured analysis result",
    )
    def analyze_failure(cls, failure_description: str, session_history: list[Any]) -> RootCauseAnalysisResult:
        """Runs the 5-Whys and Theory of Constraints bottleneck identification."""
        # This function would use an LLM in the DAG to perform the 5 Whys.
        # We mock the return for the deterministic wrapper.

        # Simple heuristic mapping for mock
        category = RootCauseCategory.PROCESS_GAP
        if "format" in failure_description.lower():
            category = RootCauseCategory.FORMAT_ERROR

        return RootCauseAnalysisResult(
            category=category,
            intervention_type=InterventionType.NEW_GUARD,
            bottleneck_location="unknown_step",
            lesson_id="LESSON-NEW",
            is_new_lesson=True,
        )

    @classmethod
    @deal.has()
    @deal.post(lambda result: result is None or isinstance(result, str))
    def check_lesson_reuse(cls, category: RootCauseCategory, existing_lessons: list[dict[str, Any]]) -> str | None:
        """Checks if a lesson for this category already exists (FR-023)."""
        for lesson in existing_lessons:
            if lesson.get("category") == category.value:
                return lesson.get("id")
        return None

    @classmethod
    @deal.ensure(
        lambda _: _.rca_result.lesson_id in _.result,
        message="Rendered LESSON must embed its id",
    )
    def generate_lesson_markdown(cls, rca_result: RootCauseAnalysisResult) -> str:
        """Generates the Markdown representation of the LESSON."""
        return f"""### {rca_result.lesson_id}

- **變更類型**: FIX
- **根因分類**: {rca_result.category.value}
- **介入類型**: {rca_result.intervention_type.value}
- **瓶頸位置**: {rca_result.bottleneck_location}
"""
