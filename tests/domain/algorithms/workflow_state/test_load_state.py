"""Tests for workflow state loading logic."""

from agentic_workflow.domain.algorithms.workflow_resume import WorkflowResume


class TestLoadState:
    """Tests for workflow state loading logic."""

    def test_load_state_returns_dict(self) -> None:
        """TC-036: Load state returns dictionary."""
        state = WorkflowResume.load_state("some workflow state content")
        assert isinstance(state, dict)
        assert "pipeline_position" in state
