"""Tests for StartPipelineUseCase."""

from agentic_workflow.application.use_cases.start_pipeline import StartPipelineUseCase
from agentic_workflow.domain.enums import PipelineStatus


class TestStartPipelineUseCase:
    """UC-001: Start a new pipeline."""

    def test_start_pipeline_creates_running_pipeline(self) -> None:
        """Verify that starting a pipeline results in a RUNNING state."""
        use_case = StartPipelineUseCase()
        pipeline = use_case.execute(pipeline_id="use-case-test")

        assert pipeline.pipeline_id == "use-case-test"
        assert pipeline.status == PipelineStatus.RUNNING
