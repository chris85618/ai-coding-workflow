"""Use Case: Start Pipeline."""

from agentic_workflow.application.ports.repositories.pipeline_repository import IPipelineRepository
from agentic_workflow.domain.aggregates.pipeline import Pipeline


class StartPipelineUseCase:
    """UC-001: Start a new pipeline."""

    def __init__(self, repo: IPipelineRepository):
        """Initialize with a pipeline repository."""
        self._repo = repo

    def execute(self, pipeline_id: str) -> Pipeline:
        """Execute the use case.

        Args:
            pipeline_id: The ID for the new pipeline.

        Returns:
            The started Pipeline aggregate root.
        """
        pipeline = Pipeline(pipeline_id=pipeline_id)
        pipeline.start()
        self._repo.save(pipeline)
        return pipeline
