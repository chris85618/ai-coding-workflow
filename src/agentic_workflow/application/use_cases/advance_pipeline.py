"""Use Case: Advance pipeline to the next stage."""

from __future__ import annotations

from agentic_workflow.domain.aggregates.pipeline import Pipeline
from agentic_workflow.domain.enums import GateDecision


class AdvancePipelineUseCase:
    """UC-001/UC-003: Advance pipeline to the next stage."""

    def execute(self, pipeline: Pipeline, decision: GateDecision) -> None:
        """Execute the use case.

        Args:
            pipeline: The Pipeline aggregate root.
            decision: The gate decision result to record before advancing.
        """
        pipeline.record_gate(decision)
        pipeline.advance()
