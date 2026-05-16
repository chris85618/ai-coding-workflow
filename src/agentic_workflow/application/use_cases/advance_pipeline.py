"""Use Case: Advance Pipeline."""

from agentic_workflow.application.ports.repositories.pipeline_repository import IPipelineRepository
from agentic_workflow.domain.aggregates.pipeline import Pipeline
from agentic_workflow.domain.enums import GateDecision


class AdvancePipelineUseCase:
    """UC-001/UC-003: Advance pipeline to the next stage."""

    def __init__(self, repo: IPipelineRepository):
        """Initialize with a pipeline repository."""
        self._repo = repo

    def execute(self, pipeline_id: str, decision: GateDecision) -> Pipeline:
        """Execute the use case.

        Args:
            pipeline_id: The ID of the pipeline to advance.
            decision: The gate decision result to record before advancing.
        """
        pipeline = self._repo.get_by_id(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline {pipeline_id} not found")

        # Using the hardened Aggregate Root method (Task 3)
        pipeline.advance_stage(decision)

        self._repo.save(pipeline)
        return pipeline
