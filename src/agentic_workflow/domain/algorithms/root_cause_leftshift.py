"""Root Cause Left-Shift Algorithm.

Traceable to: FR-007, FR-023
Replaces: skills/workflow-skills/root-cause-leftshift.md
"""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel


class RootCauseCategory(StrEnum):
    """Categories for root cause analysis."""

    FORMAT_ERROR = "FORMAT_ERROR"
    COVERAGE_GAP = "COVERAGE_GAP"
    LLM_HALLUCINATION = "LLM_HALLUCINATION"
    PROCESS_GAP = "PROCESS_GAP"
    SEMANTIC_DRIFT = "SEMANTIC_DRIFT"
    NAMING_INCONSISTENCY = "NAMING_INCONSISTENCY"
    GOVERNANCE_BYPASS = "GOVERNANCE_BYPASS"
    SCAN_INCOMPLETENESS = "SCAN_INCOMPLETENESS"
    DECLARATION_IMPLEMENTATION_GAP = "DECLARATION_IMPLEMENTATION_GAP"
    NEW_CAPABILITY = "NEW_CAPABILITY"
    IMPROVEMENT = "IMPROVEMENT"


class InterventionType(StrEnum):
    """Types of interventions for left-shifting guards."""

    GUARD_STRENGTHENING = "GUARD_STRENGTHENING"
    NEW_GUARD = "NEW_GUARD"
    STEP_ADDITION = "STEP_ADDITION"


class RootCauseAnalysisResult(BaseModel):
    """Result of a root cause analysis."""

    category: RootCauseCategory
    intervention_type: InterventionType
    bottleneck_location: str
    lesson_id: str
    is_new_lesson: bool


class RootCauseLeftShift:
    """Performs Root Cause Analysis and Left-Shift guard implementation."""

    @classmethod
    def analyze_failure(
        cls, failure_description: str, session_history: list[Any]
    ) -> RootCauseAnalysisResult:
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
    def check_lesson_reuse(
        cls, category: RootCauseCategory, existing_lessons: list[dict[str, Any]]
    ) -> str | None:
        """Checks if a lesson for this category already exists (FR-023)."""
        for lesson in existing_lessons:
            if lesson.get("category") == category.value:
                return lesson.get("id")
        return None

    @classmethod
    def generate_lesson_markdown(cls, rca_result: RootCauseAnalysisResult) -> str:
        """Generates the Markdown representation of the LESSON."""
        return f"""### {rca_result.lesson_id}

- **變更類型**: FIX
- **根因分類**: {rca_result.category.value}
- **介入類型**: {rca_result.intervention_type.value}
- **瓶頸位置**: {rca_result.bottleneck_location}
"""
