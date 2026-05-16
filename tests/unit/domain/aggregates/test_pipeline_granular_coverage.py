"""Additional coverage for Pipeline aggregate."""

import pytest

from agentic_workflow.domain.aggregates.pipeline import Pipeline
from agentic_workflow.domain.enums import GateDecision, PipelineStatus, StageStatus


def test_pipeline_advance_failure() -> None:
    """Cover the failure path of advance_stage."""
    pipeline = Pipeline(pipeline_id="fail-test")
    pipeline.start()

    pipeline.advance_stage(GateDecision.FAIL)

    assert pipeline.status == PipelineStatus.FAILED
    assert pipeline.current_stage.status == StageStatus.FAILED
    assert any("Validation Error" in f for f in pipeline.current_stage.findings.items)


def test_pipeline_increment_iteration_no_stage() -> None:
    """Cover error path when current stage is missing (unlikely but for coverage)."""
    pipeline = Pipeline(pipeline_id="no-stage-test")
    pipeline.stages = {}  # Force empty

    with pytest.raises(ValueError, match="Current stage phase0 not found"):
        pipeline.increment_stage_iteration()


def test_pipeline_with_prefilled_stages() -> None:
    """Cover the path where stages are already provided to constructor."""
    from agentic_workflow.domain.entities.stage import Stage

    stages = {"phase0": Stage(stage_id="phase0", name="Custom")}
    pipeline = Pipeline(pipeline_id="custom", stages=stages)
    assert pipeline.stages["phase0"].name == "Custom"
    # Should not have initialized other default stages
    assert len(pipeline.stages) == 1


def test_pipeline_fail_validation_no_stage() -> None:
    """Cover the path where fail_validation is called but stage is missing."""
    pipeline = Pipeline(pipeline_id="no-stage-fail")
    pipeline.stages = {}  # Force empty
    pipeline.fail_validation("Critical error")
    assert pipeline.status == PipelineStatus.FAILED
