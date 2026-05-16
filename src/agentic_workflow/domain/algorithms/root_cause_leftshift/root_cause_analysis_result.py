"""Root Cause Left-Shift — RootCauseAnalysisResult Model.

Traceable to: FR-007, FR-023
"""

from pydantic import BaseModel

from agentic_workflow.domain.algorithms.root_cause_leftshift.intervention_type import (
    InterventionType,
)
from agentic_workflow.domain.algorithms.root_cause_leftshift.root_cause_category import (
    RootCauseCategory,
)


class RootCauseAnalysisResult(BaseModel):
    """Result of a root cause analysis."""

    category: RootCauseCategory
    intervention_type: InterventionType
    bottleneck_location: str
    lesson_id: str
    is_new_lesson: bool
