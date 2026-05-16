"""Unit tests for AdvancePipelineUseCase."""

from unittest.mock import MagicMock

import pytest

from agentic_workflow.application.ports.repositories.pipeline_repository import IPipelineRepository
from agentic_workflow.application.use_cases.advance_pipeline import AdvancePipelineUseCase
from agentic_workflow.domain.aggregates.pipeline import Pipeline
from agentic_workflow.domain.enums import GateDecision


class TestAdvancePipelineUseCase:
    """Test suite for AdvancePipelineUseCase."""

    def test_execute_success(self) -> None:
        """Verify successful advancement of the pipeline."""
        mock_repo = MagicMock(spec=IPipelineRepository)
        # Initialize pipeline and make it ready to advance
        pipeline = Pipeline(pipeline_id="test-pipeline")
        pipeline.start()  # Status -> RUNNING
        pipeline.last_gate_decision = GateDecision.PASS  # Satisfy INV-002-v2

        mock_repo.get_by_id.return_value = pipeline

        use_case = AdvancePipelineUseCase(mock_repo)
        result = use_case.execute("test-pipeline", GateDecision.PASS)

        assert result == pipeline
        assert pipeline.last_gate_decision == GateDecision.PASS
        mock_repo.save.assert_called_once_with(pipeline)

    def test_execute_pipeline_not_found(self) -> None:
        """Verify error when pipeline is not found."""
        mock_repo = MagicMock(spec=IPipelineRepository)
        mock_repo.get_by_id.return_value = None

        use_case = AdvancePipelineUseCase(mock_repo)
        with pytest.raises(ValueError, match="Pipeline test-pipeline not found"):
            use_case.execute("test-pipeline", GateDecision.PASS)
