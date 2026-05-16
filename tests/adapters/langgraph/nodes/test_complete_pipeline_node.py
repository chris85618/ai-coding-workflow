"""Tests for node_complete_pipeline."""

from agentic_workflow.adapters.langgraph.nodes import node_complete_pipeline
from agentic_workflow.adapters.langgraph.state_mapper import WorkflowState


def _fresh_state(
    pipeline_status: str = "running",
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


class TestCompletePipelineNode:
    """Covers node_complete_pipeline logic."""

    def test_node_complete_pipeline(self) -> None:
        """TC-282: Pipeline completion."""
        state = _fresh_state("running")
        result = node_complete_pipeline(state)
        assert result.get("pipeline_status") == "completed"

    def test_node_complete_pipeline_already_completed(self) -> None:
        """TC-283: Pipeline already completed."""
        state = _fresh_state("completed")
        result = node_complete_pipeline(state)
        assert result.get("pipeline_status") == "completed"
