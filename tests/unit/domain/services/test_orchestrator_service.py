"""Unit tests for OrchestratorService."""

from unittest.mock import MagicMock

from agentic_workflow.domain.aggregates.pipeline import Pipeline
from agentic_workflow.domain.enums import PipelineStatus
from agentic_workflow.domain.services.orchestrator_service import OrchestratorService


class TestOrchestratorService:
    """Covers OrchestratorService logic."""

    def test_validate_phase_execution_fail(self) -> None:
        """Fails if pipeline is in FAILED status."""
        pipeline = MagicMock(spec=Pipeline)
        pipeline.status = PipelineStatus.FAILED
        assert OrchestratorService.validate_phase_execution(pipeline, 0) is False

    def test_validate_phase_execution_pass(self) -> None:
        """Passes if pipeline is running."""
        pipeline = MagicMock(spec=Pipeline)
        pipeline.status = PipelineStatus.RUNNING
        assert OrchestratorService.validate_phase_execution(pipeline, 0) is True

    def test_prepare_stage_context(self) -> None:
        """Prepares context dictionary."""
        pipeline = MagicMock(spec=Pipeline)
        pipeline.pipeline_id = "p-123"
        stage = MagicMock()
        stage.name = "Phase 0"
        stage.iteration_count = 1
        stage.findings = ["Finding 1"]
        pipeline.current_stage = stage

        ctx = OrchestratorService.prepare_stage_context(pipeline)
        assert ctx["pipeline_id"] == "p-123"
        assert ctx["current_stage"] == "Phase 0"
        assert ctx["iteration"] == 1
        assert "Finding 1" in ctx["findings"]
