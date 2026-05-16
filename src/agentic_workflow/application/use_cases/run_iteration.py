"""Use Case: Run Iteration."""

from agentic_workflow.application.ports.repositories.pipeline_repository import IPipelineRepository
from agentic_workflow.domain.aggregates.pipeline import Pipeline


class RunIterationUseCase:
    """UC-003: Run a single iteration of Agent alpha/beta loop."""

    def __init__(self, repo: IPipelineRepository):
        """Initialize with a pipeline repository."""
        self._repo = repo

    def execute(self, pipeline_id: str, alpha_findings: list[str]) -> Pipeline:
        """Execute the alpha/beta iteration.

        Args:
            pipeline_id: The ID of the pipeline.
            alpha_findings: New findings from Agent Alpha critique.
        """
        pipeline = self._repo.get_by_id(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline {pipeline_id} not found")

        pipeline.increment_stage_iteration()
        pipeline.update_stage_findings(alpha_findings)

        self._repo.save(pipeline)
        return pipeline
