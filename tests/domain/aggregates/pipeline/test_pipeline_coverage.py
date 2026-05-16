"""TC for Pipeline aggregate coverage gaps."""

import pytest

from agentic_workflow.domain.aggregates.pipeline import Pipeline
from agentic_workflow.domain.entities.stage import Stage
from agentic_workflow.domain.enums import StageStatus


class TestPipelineCoverage:
    """Covers edge cases and error paths in Pipeline aggregate."""

    def test_pipeline_init_with_stages(self) -> None:
        """Cover 46->exit (if not self.stages is False)."""
        stages = {"phase0": Stage(stage_id="phase0", name="Phase 0")}
        pipeline = Pipeline(pipeline_id="test", stages=stages)
        assert len(pipeline.stages) == 1
        assert "phase0" in pipeline.stages

    def test_start_already_started_raises(self) -> None:
        """Cover line 81."""
        pipeline = Pipeline(pipeline_id="test")
        pipeline.start()
        with pytest.raises(ValueError, match="Can only start a pipeline that has not started"):
            pipeline.start()

    def test_complete_not_running_raises(self) -> None:
        """Cover line 87."""
        pipeline = Pipeline(pipeline_id="test")
        # Status is NOT_STARTED
        with pytest.raises(ValueError, match="Can only complete a running pipeline"):
            pipeline.complete()

    def test_update_findings_missing_stage_raises(self) -> None:
        """Cover line 98."""
        pipeline = Pipeline(pipeline_id="test")
        pipeline.start()
        pipeline.current_position = "invalid_stage"
        with pytest.raises(ValueError, match="Current stage invalid_stage not found"):
            pipeline.update_stage_findings(["finding"])

    def test_increment_iteration_missing_stage_raises(self) -> None:
        """Cover line 106."""
        pipeline = Pipeline(pipeline_id="test")
        pipeline.start()
        pipeline.current_position = "invalid_stage"
        with pytest.raises(ValueError, match="Current stage invalid_stage not found"):
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
