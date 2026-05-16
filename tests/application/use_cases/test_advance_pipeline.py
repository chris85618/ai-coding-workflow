"""Tests for AdvancePipelineUseCase."""

from agentic_workflow.application.use_cases.advance_pipeline import AdvancePipelineUseCase
from agentic_workflow.domain.aggregates.pipeline import Pipeline
from agentic_workflow.domain.enums import GateDecision


class TestAdvancePipelineUseCase:
    """UC-001/UC-003: Advance pipeline to the next stage."""

    def test_advance_pipeline_updates_gate_and_advances(self) -> None:
        """Verify that advancing records the gate and moves position."""
        from unittest.mock import MagicMock

        mock_repo = MagicMock()

        pipeline = Pipeline(pipeline_id="advance-test")
        pipeline.start()
        pipeline.last_gate_decision = GateDecision.PASS  # Satisfy INV-002-v2

        mock_repo.get_by_id.return_value = pipeline

        initial_position = pipeline.current_position
        use_case = AdvancePipelineUseCase(mock_repo)
        use_case.execute("advance-test", GateDecision.PASS)

        assert pipeline.last_gate_decision == GateDecision.PASS
        assert pipeline.current_position != initial_position
        mock_repo.save.assert_called_once_with(pipeline)
