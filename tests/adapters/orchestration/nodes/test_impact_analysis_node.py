"""Tests for node_impact_analysis."""

from agentic_workflow.adapters.orchestration.nodes import node_impact_analysis
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


class TestImpactAnalysisNode:
    """Covers node_impact_analysis logic."""

    def test_node_impact_analysis_empty_ids(self) -> None:
        """TC-290: Node impact analysis empty."""
        state = _fresh_state()
        state["metadata"] = {"recent_changed_ids": []}
        result = node_impact_analysis(state)
        assert result["metadata"]["impact_analysis_results"] == {}

    def test_node_impact_analysis_with_ids(self) -> None:
        """TC-291: Node impact analysis with IDs."""
        state = _fresh_state()
        state["metadata"] = {"recent_changed_ids": ["FR-001", "FR-002"]}
        result = node_impact_analysis(state)
        assert "FR-001" in result["metadata"]["impact_analysis_results"]
        assert "FR-002" in result["metadata"]["impact_analysis_results"]
