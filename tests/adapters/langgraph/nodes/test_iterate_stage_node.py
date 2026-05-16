"""Tests for node_iterate_stage and should_continue_iterating."""

from agentic_workflow.adapters.langgraph.nodes import (
    node_iterate_stage,
    should_continue_iterating,
)
from agentic_workflow.adapters.langgraph.state_mapper import WorkflowState
from agentic_workflow.domain.models.stage import MAX_ITERATIONS


def _fresh_state(
    stage_status: str | None = None,
    iteration_count: int = 0,
) -> WorkflowState:
    """Create a fresh WorkflowState dict."""
    state = WorkflowState(
        pipeline_id="test-pipeline-001",
        pipeline_status="running",
        current_position="phase0",
        last_gate_decision=None,
        last_error=None,
        metadata={},
    )
    if stage_status is not None:
        state["current_stage_id"] = "stage-001"
        state["stage_status"] = stage_status
        state["iteration_count"] = iteration_count
    return state


class TestIterateStageNode:
    """Covers node_iterate_stage and should_continue_iterating logic."""

    def test_node_iterate_stage_no_stage(self) -> None:
        """TC-279: Iterate with no stage."""
        state = _fresh_state()  # no current_stage key
        result = node_iterate_stage(state)
        assert result.get("last_error") is not None

    def test_node_iterate_stage_pending(self) -> None:
        """TC-280: Iterate Pending state."""
        state = _fresh_state(stage_status="pending")
        result = node_iterate_stage(state)
        assert result.get("stage_status") == "iterating"

    def test_node_iterate_stage_iterating(self) -> None:
        """TC-281: Iterate Iterating state."""
        state = _fresh_state(stage_status="iterating", iteration_count=1)
        result = node_iterate_stage(state)
        assert result.get("iteration_count", 0) >= 1

    def test_should_continue_iterating_no_stage(self) -> None:
        """TC-284: Continue logic no stage."""
        state = _fresh_state()
        assert should_continue_iterating(state) == "gate"

    def test_should_continue_iterating_passed(self) -> None:
        """TC-285: Continue logic passed."""
        state = _fresh_state(stage_status="passed")
        assert should_continue_iterating(state) == "gate"

    def test_should_continue_iterating_max_reached(self) -> None:
        """TC-286: Continue logic max iterations."""
        state = _fresh_state(stage_status="iterating", iteration_count=MAX_ITERATIONS)
        assert should_continue_iterating(state) == "gate"

    def test_should_continue_iterating_not_done(self) -> None:
        """TC-287: Continue logic iterate path."""
        state = _fresh_state(stage_status="iterating", iteration_count=0)
        assert should_continue_iterating(state) == "iterate"
