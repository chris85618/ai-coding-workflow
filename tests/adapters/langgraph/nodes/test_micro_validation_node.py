"""Tests for node_micro_validation."""

from agentic_workflow.adapters.langgraph.nodes import node_micro_validation
from agentic_workflow.adapters.langgraph.state_mapper import WorkflowState


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


class TestMicroValidationNode:
    """Covers node_micro_validation logic."""

    def test_node_micro_validation_clean_content(self) -> None:
        """TC-288: Node micro-validation clean."""
        state = _fresh_state()
        state["metadata"] = {
            "recent_changes_content": "clean",
            "recent_changed_ids": ["FR-001"],
        }
        result = node_micro_validation(state)
        assert result["metadata"]["micro_validation_result"]["passed"] is True

    def test_node_micro_validation_bad_content(self) -> None:
        """TC-289: Node micro-validation failure."""
        state = _fresh_state()
        state["metadata"] = {
            "recent_changes_content": "from vibe import x",
            "recent_changed_ids": [],
        }
        result = node_micro_validation(state)
        assert result["metadata"]["micro_validation_result"]["passed"] is False
