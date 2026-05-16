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

    def setup_method(self) -> None:
        """Set up for TestOrchestratorNode."""
        from unittest.mock import MagicMock

        from agentic_workflow.adapters.langgraph.nodes import set_container
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

    def test_node_orchestrator_not_started(self) -> None:
        """TC-292: Node orchestrator Not Started."""
        state = _fresh_state("not_started")
        result = node_orchestrator(state)
        assert result["metadata"]["orchestrator_is_valid"] is True
        assert "domain_context" in result["metadata"]

    def test_node_orchestrator_running(self) -> None:
        """TC-293: Node orchestrator Running."""
        state = _fresh_state("running")
        result = node_orchestrator(state)
        assert result["metadata"]["orchestrator_is_valid"] is True
        assert "domain_context" in result["metadata"]
