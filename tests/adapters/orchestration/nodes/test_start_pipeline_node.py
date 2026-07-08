"""Tests for node_start_pipeline."""

from agentic_workflow.adapters.orchestration.nodes import node_start_pipeline
from agentic_workflow.adapters.orchestration.state_mapper import WorkflowState


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

    def setup_method(self) -> None:
        """Set up for TestStartPipelineNode."""
        from unittest.mock import MagicMock

        from agentic_workflow.adapters.orchestration.nodes import set_container
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
        self.mock_repo.get_by_id.return_value = self.test_pipeline

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
