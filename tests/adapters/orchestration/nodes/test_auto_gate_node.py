"""Tests for node_auto_gate."""

from agentic_workflow.adapters.orchestration.nodes import node_auto_gate
from agentic_workflow.adapters.orchestration.state_mapper import WorkflowState
from agentic_workflow.domain.enums import GateDecision


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


class TestAutoGateNode:
    """Covers node_auto_gate logic."""

    def test_node_auto_gate_default_pass(self) -> None:
        """TC-276: Auto gate default PASS."""
        state = _fresh_state()
        result = node_auto_gate(state)
        assert result.get("last_gate_decision") == GateDecision.PASS

    def test_node_auto_gate_override_warnings(self) -> None:
        """TC-277: Auto gate override warnings."""
        state = _fresh_state()
        state["metadata"] = {"gate_override": "pass_with_warnings"}
        result = node_auto_gate(state)
        assert result.get("last_gate_decision") == GateDecision.PASS_WITH_WARNINGS
