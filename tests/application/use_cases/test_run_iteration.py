"""Tests for RunIterationUseCase."""

from agentic_workflow.application.use_cases.run_iteration import RunIterationUseCase
from agentic_workflow.domain.aggregates.pipeline import Pipeline


class TestRunIterationUseCase:
    """UC-003: Run a single iteration of Agent alpha/beta loop."""

    def test_run_iteration_updates_findings_and_increments(self) -> None:
        """Verify that running iteration updates findings and increments count."""
        from unittest.mock import MagicMock

        mock_repo = MagicMock()

        pipeline = Pipeline(pipeline_id="iter-test")
        pipeline.start()
        mock_repo.get_by_id.return_value = pipeline

        current_stage = pipeline.stages[pipeline.current_position]
        initial_count = current_stage.iteration_count
        use_case = RunIterationUseCase(mock_repo)
        findings = ["Finding A", "Finding B"]
        use_case.execute("iter-test", findings)

        assert current_stage.iteration_count == initial_count + 1
        # Check if findings are recorded in current stage
        assert len(current_stage.findings.items) == 2
        assert "Finding A" in current_stage.findings.items
        mock_repo.save.assert_called_once_with(pipeline)
