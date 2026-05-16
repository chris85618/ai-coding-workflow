"""Tests for AdvancePipelineUseCase."""

from agentic_workflow.application.use_cases.advance_pipeline import AdvancePipelineUseCase
from agentic_workflow.domain.aggregates.pipeline import Pipeline
from agentic_workflow.domain.enums import GateDecision


class TestAdvancePipelineUseCase:
    """UC-001/UC-003: Advance pipeline to the next stage."""

    def test_advance_pipeline_updates_gate_and_advances(self) -> None:
        """Verify that advancing records the gate and moves position."""
        pipeline = Pipeline(pipeline_id="advance-test")
        pipeline.start()

        initial_position = pipeline.current_position
        use_case = AdvancePipelineUseCase()
        use_case.execute(pipeline, GateDecision.PASS)

        assert pipeline.last_gate_decision == GateDecision.PASS
        assert pipeline.current_position != initial_position
