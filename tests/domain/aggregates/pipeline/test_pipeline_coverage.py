"""TC for Pipeline aggregate coverage gaps."""

import pytest

from agentic_workflow.domain.aggregates.pipeline import Pipeline
from agentic_workflow.domain.entities.stage import Stage
from agentic_workflow.domain.enums import StageStatus


class TestPipelineCoverage:
    """Covers edge cases and error paths in Pipeline aggregate."""

    def test_pipeline_init_with_stages(self) -> None:
        """Cover 46->exit (if not self.stages is False)."""
        from agentic_workflow.domain.aggregates.pipeline import _STAGE_ORDER

        stage_order = _STAGE_ORDER
        stages = {stage_id: Stage(stage_id=stage_id, name=stage_id.title()) for stage_id in stage_order}
        pipeline = Pipeline(pipeline_id="test", stages=stages)
        assert len(pipeline.stages) == len(stage_order)
        assert "phase0" in pipeline.stages

    def test_start_already_started_raises(self) -> None:
        """Cover line 81."""
        pipeline = Pipeline(pipeline_id="test")
        pipeline.start()
        import icontract

        with pytest.raises(icontract.errors.ViolationError, match="Can only start a pipeline that has not started"):
            pipeline.start()

    def test_complete_not_running_raises(self) -> None:
        """Cover line 87."""
        pipeline = Pipeline(pipeline_id="test")
        # Status is NOT_STARTED
        import icontract

        with pytest.raises(icontract.errors.ViolationError, match="Can only complete a running pipeline"):
            pipeline.complete()

    def test_update_findings_missing_stage_raises(self) -> None:
        """INV-016: corrupting current_position must trip the aggregate invariant."""
        import icontract

        pipeline = Pipeline(pipeline_id="test")
        pipeline.start()
        pipeline.current_position = "invalid_stage"
        with pytest.raises(icontract.errors.ViolationError):
            pipeline.update_stage_findings(["finding"])

    def test_increment_iteration_missing_stage_raises(self) -> None:
        """INV-016: corrupting current_position must trip the aggregate invariant."""
        import icontract

        pipeline = Pipeline(pipeline_id="test")
        pipeline.start()
        pipeline.current_position = "invalid_stage"
        with pytest.raises(icontract.errors.ViolationError):
            pipeline.increment_stage_iteration()

    def test_increment_iteration_not_pending(self) -> None:
        """Cover 108->exit (if stage.status == StageStatus.PENDING is False)."""
        pipeline = Pipeline(pipeline_id="test")
        pipeline.start()
        # First increment moves it to ITERATING
        pipeline.increment_stage_iteration()
        assert pipeline.stages["phase0"].status == StageStatus.ITERATING

        # Second increment should not transition status again
        pipeline.increment_stage_iteration()
        assert pipeline.stages["phase0"].status == StageStatus.ITERATING
        assert pipeline.stages["phase0"].iteration_count == 2
