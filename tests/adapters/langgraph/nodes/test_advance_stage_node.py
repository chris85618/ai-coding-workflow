"""Tests for node_advance_stage."""

from agentic_workflow.adapters.langgraph.nodes import node_advance_stage
from agentic_workflow.adapters.langgraph.state_mapper import WorkflowState
from agentic_workflow.domain.models.enums import GateDecision


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


class TestAdvanceStageNode:
    """Covers node_advance_stage logic."""

    def test_node_advance_stage(self) -> None:
        """TC-278: Advance stage transition."""
        state = _fresh_state()
        state["last_gate_decision"] = GateDecision.PASS
        result = node_advance_stage(state)
        assert "current_position" in result
