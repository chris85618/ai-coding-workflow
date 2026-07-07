"""Tests for AdvancePipelineUseCase."""

from agentic_workflow.application.use_cases.advance_pipeline import AdvancePipelineUseCase
from agentic_workflow.domain.aggregates.pipeline import Pipeline
from agentic_workflow.domain.enums import GateDecision


class TestAdvancePipelineUseCase:
    """UC-001/UC-003: Advance pipeline to the next stage."""

    def test_advance_pipeline_updates_gate_and_advances(self) -> None:
        """Verify that advancing records the gate and moves position."""
        from unittest.mock import MagicMock

        mock_repo = MagicMock()

        pipeline = Pipeline(pipeline_id="advance-test")
        pipeline.start()
        pipeline.last_gate_decision = GateDecision.PASS  # Satisfy INV-002-v2

        mock_repo.get_by_id.return_value = pipeline

        initial_position = pipeline.current_position
        use_case = AdvancePipelineUseCase(mock_repo)
        use_case.execute("advance-test", GateDecision.PASS)

        assert pipeline.last_gate_decision == GateDecision.PASS
        assert pipeline.current_position != initial_position
        mock_repo.save.assert_called_once_with(pipeline)

    def test_execute_to_advances_until_target_position(self) -> None:
        """TC-BOOT-010: execute_to advances slot by slot until the aggregate reaches the target."""
        from unittest.mock import MagicMock

        mock_repo = MagicMock()
        pipeline = Pipeline(pipeline_id="advance-to-test")
        pipeline.start()
        mock_repo.get_by_id.return_value = pipeline

        use_case = AdvancePipelineUseCase(mock_repo)
        use_case.execute_to("advance-to-test", "stage3", GateDecision.PASS)

        assert pipeline.current_position == "stage3"
        assert pipeline.stages["phase0"].status.value == "passed"
        assert pipeline.stages["phase2"].status.value == "passed"
        mock_repo.save.assert_called_once_with(pipeline)

    def test_execute_to_is_idempotent_at_target(self) -> None:
        """TC-BOOT-011: execute_to is a no-op when the aggregate already sits on the target."""
        from unittest.mock import MagicMock

        mock_repo = MagicMock()
        pipeline = Pipeline(pipeline_id="idempotent-test")
        pipeline.start()
        mock_repo.get_by_id.return_value = pipeline

        use_case = AdvancePipelineUseCase(mock_repo)
        use_case.execute_to("idempotent-test", "phase0", GateDecision.PASS)

        assert pipeline.current_position == "phase0"
        assert pipeline.stages["phase0"].status.value == "pending"

    def test_execute_to_rejects_unknown_target(self) -> None:
        """TC-BOOT-012: execute_to raises for a target outside the canonical stage order."""
        from unittest.mock import MagicMock

        import pytest

        mock_repo = MagicMock()
        pipeline = Pipeline(pipeline_id="bad-target-test")
        pipeline.start()
        mock_repo.get_by_id.return_value = pipeline

        use_case = AdvancePipelineUseCase(mock_repo)
        with pytest.raises(ValueError, match="Unknown target position"):
            use_case.execute_to("bad-target-test", "stage99", GateDecision.PASS)

    def test_execute_to_rejects_missing_pipeline(self) -> None:
        """TC-BOOT-013: execute_to raises when the pipeline id cannot be resolved."""
        from unittest.mock import MagicMock

        import pytest

        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = None

        use_case = AdvancePipelineUseCase(mock_repo)
        with pytest.raises(ValueError, match="not found"):
            use_case.execute_to("ghost", "stage3", GateDecision.PASS)
