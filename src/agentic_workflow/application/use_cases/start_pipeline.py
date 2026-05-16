"""Use Case: Start a new pipeline."""

from __future__ import annotations

from agentic_workflow.domain.aggregates.pipeline import Pipeline


class StartPipelineUseCase:
    """UC-001: Start a new pipeline."""

    def execute(self, pipeline_id: str) -> Pipeline:
        """Execute the use case.

        Args:
            pipeline_id: The ID for the new pipeline.

        Returns:
            The started Pipeline aggregate root.
        """
        pipeline = Pipeline(pipeline_id=pipeline_id)
        pipeline.start()
        return pipeline
