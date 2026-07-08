"""Tests for node_pipeline_completeness."""

from agentic_workflow.adapters.orchestration.nodes import node_pipeline_completeness
from agentic_workflow.adapters.orchestration.state_mapper import WorkflowState


def _fresh_state() -> WorkflowState:
    """Create a fresh WorkflowState dict."""
    return WorkflowState(
        pipeline_id="test-pipeline-001",
        pipeline_status="running",
        current_position="phase0",
        last_gate_decision=None,
        last_error=None,
        metadata={},
    )


class TestPipelineCompletenessNode:
    """Covers node_pipeline_completeness logic."""

    def test_node_pipeline_completeness_returns_metadata(self) -> None:
        """TC-275: Completeness metadata."""
        state = _fresh_state()
        result = node_pipeline_completeness(state)
        assert "metadata" in result
        assert "completeness" in result["metadata"]
