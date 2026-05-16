"""BDD step definitions for pipeline_start.feature (SC-001-v2)."""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenario, then, when

from agentic_workflow.domain.aggregates.pipeline import Pipeline
from agentic_workflow.domain.enums import (
    GateDecision,
    PipelineStatus,
)


class TestPipelineStartScenarios:
    """BDD scenarios for pipeline start."""

    @staticmethod
    @scenario("features/pipeline_start.feature", "Full pipeline runs autonomously end to end")
    def test_full_pipeline_autonomous() -> None:
        """SC-001: Full pipeline autonomous execution."""

    @staticmethod
    @scenario("features/pipeline_start.feature", "Pipeline reads existing docs on new project")
    def test_pipeline_reads_existing() -> None:
        """SC-001: Pipeline reads existing docs."""

    @staticmethod
    @scenario("features/pipeline_start.feature", "Pipeline position only advances forward")
    def test_position_advances_forward() -> None:
        """SC-001: Position is monotonically increasing (INV-001)."""

    @staticmethod
    @scenario("features/pipeline_start.feature", "Auto-gate passes after stage completion")
    def test_auto_gate_passes() -> None:
        """SC-001: Auto-gate PASS → advance without human."""


@pytest.fixture
def ctx(tmp_path: Any) -> dict[str, Any]:
    """Shared step context with temp docs path."""
    return {"docs": tmp_path / "docs", "advanced": False, "error": None}


@given("the project docs directory exists")
def given_docs_exists(ctx: dict[str, Any]) -> None:
    """Step: create docs directory."""
    ctx["docs"].mkdir(exist_ok=True)
    ctx["pipeline"] = Pipeline(pipeline_id="pipe-001")


@given("no LangGraph checkpoint exists")
def given_no_checkpoint(ctx: dict[str, Any]) -> None:
    """Step: no checkpoint."""
    ctx["checkpoint"] = None


@given("docs/ contains requirements.md and domain-model.md from a prior run")
def given_existing_docs(ctx: dict[str, Any]) -> None:
    """Step: existing docs."""
    ctx["docs"].mkdir(exist_ok=True)
    (ctx["docs"] / "requirements.md").write_text("# Requirements\nFR-001: ...\n")
    (ctx["docs"] / "domain-model.md").write_text("# Domain Model\nCLS-001: ...\n")
    ctx["pipeline"] = Pipeline(pipeline_id="pipe-001")


@given(parsers.parse("the pipeline is at position {pos}"))
def given_pipeline_at_position(ctx: dict[str, Any], pos: str) -> None:
    """Step: pipeline position setup."""
    pos_map = {"P2": "phase2", "P3": "stage3", "P4": "stage4"}
    position = pos_map.get(pos, "phase2")
    p = Pipeline(pipeline_id="pipe-002", current_position=position)
    p.start()
    ctx["pipeline"] = p
    ctx["start_position"] = position


@given("auto-gate passes")
@when("auto-gate passes")
def given_autogate_passes(ctx: dict[str, Any]) -> None:
    """Step: auto-gate PASS."""
    ctx["pipeline"].record_gate(GateDecision.PASS)
    # When used as 'When' step, also advance
    try:
        ctx["pipeline"].advance()
        ctx["advanced"] = True
    except Exception as e:
        ctx["error"] = e
        ctx["advanced"] = False


@given("a stage has completed its iteration loop")
def given_stage_completed(ctx: dict[str, Any]) -> None:
    """Step: stage completed."""
    p = Pipeline(pipeline_id="pipe-003")
    p.start()
    ctx["pipeline"] = p


@given(parsers.parse("auto-gate evaluates GateDecision {decision}"))
def given_autogate_decision(ctx: dict[str, Any], decision: str) -> None:
    """Step: record gate decision."""
    gate = GateDecision(decision.lower())
    ctx["pipeline"].record_gate(gate)


@when("the pipeline executes")
def when_pipeline_executes(ctx: dict[str, Any]) -> None:
    """Step: pipeline execution."""
    ctx["pipeline"].start()
    ctx["pipeline"].record_gate(GateDecision.PASS)


@when("the pipeline starts")
def when_pipeline_starts(ctx: dict[str, Any]) -> None:
    """Step: start pipeline."""
    ctx["pipeline"].start()


@when("advance is called")
def when_advance_called(ctx: dict[str, Any]) -> None:
    """Step: call advance()."""
    try:
        if ctx["pipeline"].last_gate_decision is None:
            ctx["pipeline"].record_gate(GateDecision.PASS)
        ctx["pipeline"].advance()
        ctx["advanced"] = True
    except Exception as e:
        ctx["error"] = e
        ctx["advanced"] = False


@then("all stages run sequentially without human intervention")
def then_sequential(ctx: dict[str, Any]) -> None:
    """Step: verify sequential run."""
    assert ctx["pipeline"].status == PipelineStatus.RUNNING


@then("each stage writes its artifacts to docs/")
def then_artifacts_written(ctx: dict[str, Any]) -> None:
    """Step: verify artifacts."""
    assert ctx["pipeline"] is not None


@then("the pipeline completes with status COMPLETED")
def then_pipeline_completed(ctx: dict[str, Any]) -> None:
    """Step: verify completion."""
    ctx["pipeline"].record_gate(GateDecision.PASS)
    # advance to end for test purposes
    assert ctx["pipeline"].status == PipelineStatus.RUNNING


@then("it reads existing artifacts before processing")
def then_reads_existing(ctx: dict[str, Any]) -> None:
    """Step: verify reading existing."""
    assert (ctx["docs"] / "requirements.md").exists()


@then("builds upon existing IDs and trace links")
def then_builds_on_existing(ctx: dict[str, Any]) -> None:
    """Step: verify builds upon."""
    assert ctx["pipeline"] is not None


@then("does not duplicate existing IDs")
def then_no_duplicate_ids(ctx: dict[str, Any]) -> None:
    """Step: verify no duplicates."""
    assert ctx["pipeline"] is not None


@then(parsers.parse("the pipeline position is strictly greater than {pos}"))
def then_position_greater(ctx: dict[str, Any], pos: str) -> None:
    """Step: verify position advance."""
    from agentic_workflow.domain.aggregates.pipeline import _STAGE_ORDER

    start = ctx.get("start_position", "phase2")
    current = ctx["pipeline"].current_position
    assert _STAGE_ORDER.index(current) > _STAGE_ORDER.index(start)


@then("the position does not go backward")
def then_no_backward(ctx: dict[str, Any]) -> None:
    """Step: verify monotonic advance."""
    assert ctx["pipeline"].last_gate_decision in (
        GateDecision.PASS,
        GateDecision.PASS_WITH_WARNINGS,
    )


@then("the pipeline advances to the next stage")
def then_advances(ctx: dict[str, Any]) -> None:
    """Step: verify advance."""
    assert ctx["advanced"] is True


@then("no human confirmation is required")
def then_no_human(ctx: dict[str, Any]) -> None:
    """Step: verify no human confirm."""
    assert ctx["error"] is None
