"""Tests for node_orchestrator."""

from agentic_workflow.adapters.langgraph.nodes import node_orchestrator
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


class TestOrchestratorNode:
    """Covers node_orchestrator logic."""

    def test_node_orchestrator_not_started(self) -> None:
        """TC-292: Node orchestrator Not Started."""
        state = _fresh_state("not_started")
        result = node_orchestrator(state)
        assert "orchestrator_result" in result["metadata"]

    def test_node_orchestrator_running(self) -> None:
        """TC-293: Node orchestrator Running."""
        state = _fresh_state("running")
        result = node_orchestrator(state)
        assert "orchestrator_result" in result["metadata"]
