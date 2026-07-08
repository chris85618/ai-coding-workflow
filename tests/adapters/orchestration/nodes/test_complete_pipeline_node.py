"""Tests for node_complete_pipeline."""

from agentic_workflow.adapters.orchestration.nodes import node_complete_pipeline
from agentic_workflow.adapters.orchestration.state_mapper import WorkflowState


def _fresh_state(
    pipeline_status: str = "running",
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


class TestCompletePipelineNode:
    """Covers node_complete_pipeline logic."""

    def test_node_complete_pipeline(self) -> None:
        """TC-282: Pipeline completion."""
        state = _fresh_state("running")
        result = node_complete_pipeline(state)
        assert result.get("pipeline_status") == "completed"

    def test_node_complete_pipeline_already_completed(self) -> None:
        """TC-283: Pipeline already completed."""
        state = _fresh_state("completed")
        result = node_complete_pipeline(state)
        assert result.get("pipeline_status") == "completed"

    def test_node_complete_pipeline_persists_stored_aggregate(self) -> None:
        """TC-BOOT-016: Completion completes and saves the repository aggregate, keeping stage detail."""
        from unittest.mock import MagicMock

        from agentic_workflow.adapters.orchestration.nodes import set_container
        from agentic_workflow.domain.aggregates.pipeline import Pipeline

        stored = Pipeline(pipeline_id="test-pipeline-001")
        stored.start()
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = stored
        container = MagicMock()
        container.pipeline_repo = mock_repo
        try:
            set_container(container)
            result = node_complete_pipeline(_fresh_state("running"))
        finally:
            set_container(None)
        assert result.get("pipeline_status") == "completed"
        assert stored.status.value == "completed"
        mock_repo.save.assert_called_once_with(stored)

    def test_node_complete_pipeline_skips_completion_when_stored_already_done(self) -> None:
        """TC-BOOT-017: An already-completed stored aggregate is saved without re-completing."""
        from unittest.mock import MagicMock

        from agentic_workflow.adapters.orchestration.nodes import set_container
        from agentic_workflow.domain.aggregates.pipeline import Pipeline

        stored = Pipeline(pipeline_id="test-pipeline-001")
        stored.start()
        stored.complete()
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = stored
        container = MagicMock()
        container.pipeline_repo = mock_repo
        try:
            set_container(container)
            result = node_complete_pipeline(_fresh_state("running"))
        finally:
            set_container(None)
        assert result.get("pipeline_status") == "completed"
        mock_repo.save.assert_called_once_with(stored)

    def test_node_complete_pipeline_tolerates_missing_stored_aggregate(self) -> None:
        """TC-BOOT-018: A missing repository aggregate never blocks completion."""
        from unittest.mock import MagicMock

        from agentic_workflow.adapters.orchestration.nodes import set_container

        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = None
        container = MagicMock()
        container.pipeline_repo = mock_repo
        try:
            set_container(container)
            result = node_complete_pipeline(_fresh_state("running"))
        finally:
            set_container(None)
        assert result.get("pipeline_status") == "completed"
        mock_repo.save.assert_not_called()
