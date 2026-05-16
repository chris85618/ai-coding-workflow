"""Tests for node_advance_stage."""

from agentic_workflow.adapters.langgraph.nodes import node_advance_stage
from agentic_workflow.adapters.langgraph.state_mapper import WorkflowState
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


class TestAdvanceStageNode:
    """Covers node_advance_stage logic."""

    def setup_method(self) -> None:
        """Set up for TestAdvanceStageNode."""
        from unittest.mock import MagicMock

        from agentic_workflow.adapters.langgraph.nodes import set_container
        from agentic_workflow.domain.aggregates.pipeline import Pipeline
        from agentic_workflow.frameworks.dependency_container import DependencyContainer

        # Initialize container with mocks to satisfy nodes
        self.mock_repo = MagicMock()
        self.container = DependencyContainer(
            pipeline_repo=self.mock_repo,
            checkpoint_repo=MagicMock(),
            doc_io=MagicMock(),
            reasoner=MagicMock(),
        )
        set_container(self.container)

        # Default setup: return a running pipeline
        self.test_pipeline = Pipeline(pipeline_id="test-pipeline-001")
        self.test_pipeline.start()
        self.mock_repo.get_by_id.return_value = self.test_pipeline

    def test_node_advance_stage(self) -> None:
        """TC-278: Advance stage transition."""
        state = _fresh_state()
        state["last_gate_decision"] = GateDecision.PASS.value
        # Satisfy DbC
        self.test_pipeline.last_gate_decision = GateDecision.PASS
        result = node_advance_stage(state)
        assert result.get("current_position") == "phase1"
