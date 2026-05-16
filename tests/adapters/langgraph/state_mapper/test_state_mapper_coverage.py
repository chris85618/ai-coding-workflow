"""TC for StateMapper coverage gaps."""

from agentic_workflow.adapters.langgraph.state_mapper.state_mapper import StateMapper
from agentic_workflow.domain.aggregates.pipeline import Pipeline


class TestStateMapperCoverage:
    """Covers edge cases in StateMapper adapter."""

    def test_pipeline_to_state_no_current_stage(self) -> None:
        """Cover 42->47 (if current_stage is False)."""
        pipeline = Pipeline(pipeline_id="test")
        # Force current_position to something not in stages
        pipeline.current_position = "missing"

        state = StateMapper.pipeline_to_state(pipeline)

        assert "current_stage_id" not in state
        assert "stage_status" not in state
        assert "iteration_count" not in state
        assert state["pipeline_id"] == "test"
