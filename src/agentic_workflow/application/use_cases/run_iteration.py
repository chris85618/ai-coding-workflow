"""Use Case: Run a single iteration of a stage."""

from __future__ import annotations

from agentic_workflow.domain.aggregates.pipeline import Pipeline


class RunIterationUseCase:
    """UC-003: Run a single iteration of Agent alpha/beta loop."""

    def execute(self, pipeline: Pipeline, findings: list[str]) -> None:
        """Execute the use case.

        Args:
            pipeline: The Pipeline aggregate root.
            findings: New findings to record for the current stage.
        """
        pipeline.increment_stage_iteration()
        pipeline.update_stage_findings(findings)
