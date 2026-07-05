"""TC for Pipeline aggregate coverage gaps."""

import deal
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

        with pytest.raises(deal.PreContractError, match="Can only start a pipeline that has not started"):
            pipeline.start()

    def test_complete_not_running_raises(self) -> None:
        """Cover line 87."""
        pipeline = Pipeline(pipeline_id="test")
        # Status is NOT_STARTED
        with pytest.raises(deal.PreContractError, match="Can only complete a running pipeline"):
            pipeline.complete()

    def test_corrupting_current_position_raises(self) -> None:
        """INV-016: deal.inv rejects a dangling current_position at mutation time."""
        pipeline = Pipeline(pipeline_id="test")
        pipeline.start()
        with pytest.raises(deal.InvContractError):
            pipeline.current_position = "invalid_stage"

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
