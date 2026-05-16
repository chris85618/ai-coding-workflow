"""Tests for node_start_pipeline."""

from agentic_workflow.adapters.langgraph.nodes import node_start_pipeline
from agentic_workflow.adapters.langgraph.state_mapper import WorkflowState


def _fresh_state(
    pipeline_status: str = "not_started",
) -> WorkflowState:
    """Create a fresh WorkflowState dict."""
    return WorkflowState(
        pipeline_id="test-pipeline-001",
        pipeline_status=pipeline_status,
        current_position="phase0",
        last_gate_decision=None,
        last_error=None,
        metadata={},
    )


class TestStartPipelineNode:
    """Covers node_start_pipeline logic."""

    def test_node_start_pipeline_transitions_to_running(self) -> None:
        """TC-273: Start pipeline Running state."""
        state = _fresh_state("not_started")
        result = node_start_pipeline(state)
        assert result.get("pipeline_status") == "running"

    def test_node_start_pipeline_already_running(self) -> None:
        """TC-274: Start pipeline already Running."""
        state = _fresh_state("running")
        result = node_start_pipeline(state)
        assert result.get("pipeline_status") == "running"
