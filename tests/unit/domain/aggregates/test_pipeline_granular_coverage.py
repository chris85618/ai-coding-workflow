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


def test_pipeline_empty_stages_corruption_rejected() -> None:
    """INV-016: deal.inv validates at mutation time, so emptying stages is rejected outright."""
    import deal

    pipeline = Pipeline(pipeline_id="no-stage-test")

    with pytest.raises(deal.InvContractError):
        pipeline.stages = {}


def test_pipeline_with_prefilled_stages() -> None:
    """Cover the path where a complete stages mapping is provided to the constructor."""
    from agentic_workflow.domain.aggregates.pipeline import _STAGE_ORDER
    from agentic_workflow.domain.entities.stage import Stage

    stage_order = _STAGE_ORDER
    stages = {stage_id: Stage(stage_id=stage_id, name=stage_id.title()) for stage_id in stage_order}
    stages["phase0"] = Stage(stage_id="phase0", name="Custom")
    pipeline = Pipeline(pipeline_id="custom", stages=stages)
    assert pipeline.stages["phase0"].name == "Custom"
    # Should not have re-initialized the supplied stages
    assert len(pipeline.stages) == len(stage_order)


def test_pipeline_rejects_incomplete_stages() -> None:
    """Aggregate consistency: constructing with a partial stages mapping must fail."""
    from agentic_workflow.domain.entities.stage import Stage

    stages = {"phase0": Stage(stage_id="phase0", name="Only One")}
    with pytest.raises(ValueError, match="Stages missing required ids"):
        Pipeline(pipeline_id="partial", stages=stages)


def test_pipeline_partial_stages_corruption_rejected() -> None:
    """INV-016: a stages mapping that drops the current position must trip the invariant."""
    import deal

    pipeline = Pipeline(pipeline_id="no-stage-fail")
    pipeline.start()
    pipeline.record_gate(GateDecision.PASS)
    pipeline.advance()

    without_current = {sid: stage for sid, stage in pipeline.stages.items() if sid != pipeline.current_position}
    with pytest.raises(deal.InvContractError):
        pipeline.stages = without_current
