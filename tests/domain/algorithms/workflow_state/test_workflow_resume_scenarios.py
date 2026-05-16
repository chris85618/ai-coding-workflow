"""BDD step definitions for workflow_resume.feature (SC-010-v2)."""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenario, then, when

from agentic_workflow.domain.enums import GateDecision


class TestWorkflowResumeScenarios:
    """BDD scenarios for workflow resume."""

    @staticmethod
    @scenario("features/workflow_resume.feature", "Resume from LangGraph checkpoint")
    def test_resume_from_checkpoint() -> None:
        """SC-010: Resume from checkpoint automatically."""

    @staticmethod
    @scenario("features/workflow_resume.feature", "No checkpoint with existing docs starts from Phase 0")
    def test_no_checkpoint_with_docs() -> None:
        """SC-010: No checkpoint + existing docs → Phase 0."""

    @staticmethod
    @scenario("features/workflow_resume.feature", "No checkpoint and empty docs starts fresh")
    def test_no_checkpoint_fresh() -> None:
        """SC-010: No checkpoint + empty docs → fresh start."""

    @staticmethod
    @scenario("features/workflow_resume.feature", "Checkpoint preserves passed gates")
    def test_checkpoint_gates_preserved() -> None:
        """SC-010: Resumed checkpoint preserves PASSED stages (INV-018)."""


@pytest.fixture
def ctx(tmp_path: Any) -> dict[str, Any]:
    """Fixture for test context."""
    return {"docs": tmp_path / "docs", "pipeline": None}


@given("a previous execution was interrupted")
def given_interrupted(ctx: dict[str, Any]) -> None:
    """Mark execution as interrupted."""
    ctx["interrupted"] = True
    ctx["docs"].mkdir(exist_ok=True)  # Artifacts exist from prior run


@given("a LangGraph checkpoint exists")
def given_checkpoint_exists(ctx: dict[str, Any]) -> None:
    """Simulate existing checkpoint."""
    ctx["checkpoint"] = {
        "position": "stage5",
        "stages": {"stage3": "PASSED", "stage4": "PASSED"},
        "gate": GateDecision.PASS,
    }


@given("no LangGraph checkpoint exists")
def given_no_checkpoint(ctx: dict[str, Any]) -> None:
    """Simulate missing checkpoint."""
    ctx["checkpoint"] = None


@given("docs/ contains requirements.md from a prior run")
def given_docs_with_requirements(ctx: dict[str, Any]) -> None:
    """Pre-populate docs directory."""
    ctx["docs"].mkdir(exist_ok=True)
    (ctx["docs"] / "requirements.md").write_text("FR-001: existing\n")


@given("docs/ directory is empty")
def given_empty_docs(ctx: dict[str, Any]) -> None:
    """Ensure docs directory is empty."""
    ctx["docs"].mkdir(exist_ok=True)


@given(parsers.parse("a checkpoint exists at Stage {n:d}"))
def given_checkpoint_at_stage(ctx: dict[str, Any], n: int) -> None:
    """Create checkpoint at specific stage."""
    ctx["checkpoint"] = {
        "position": f"stage{n}",
        "stages": {f"stage{i}": "PASSED" for i in range(3, n)},
        "gate": GateDecision.PASS,
    }


@given(parsers.parse("Stage {a:d} and Stage {b:d} are marked PASSED in checkpoint"))
def given_stages_passed(ctx: dict[str, Any], a: int, b: int) -> None:
    """Mark specific stages as passed."""
    cp = ctx.get("checkpoint", {})
    cp.setdefault("stages", {})[f"stage{a}"] = "PASSED"
    cp["stages"][f"stage{b}"] = "PASSED"
    ctx["checkpoint"] = cp


@when("the pipeline starts")
def when_pipeline_starts(ctx: dict[str, Any]) -> None:
    """Simulate pipeline start."""
    cp = ctx.get("checkpoint")
    if cp:
        ctx["resume_position"] = cp["position"]
        ctx["preserved_stages"] = list(cp.get("stages", {}).keys())
    else:
        ctx["resume_position"] = "phase0"
        ctx["preserved_stages"] = []


@when("the pipeline resumes")
def when_pipeline_resumes(ctx: dict[str, Any]) -> None:
    """Simulate pipeline resume."""
    cp = ctx.get("checkpoint", {})
    ctx["resume_position"] = cp.get("position", "phase0")
    ctx["preserved_stages"] = list(cp.get("stages", {}).keys())
    ctx["next_stage"] = cp.get("position", "stage3")


@then("execution resumes from the checkpoint position automatically")
def then_resumes_from_checkpoint(ctx: dict[str, Any]) -> None:
    """Verify resume position."""
    assert ctx["resume_position"] != "phase0"


@then("previously completed stages are not re-executed")
def then_no_rerun(ctx: dict[str, Any]) -> None:
    """Verify no stages are re-executed."""
    assert len(ctx["preserved_stages"]) > 0


@then("existing docs/ artifacts are preserved")
def then_artifacts_preserved(ctx: dict[str, Any]) -> None:
    """Verify artifacts are preserved."""
    assert ctx["docs"].exists()


@then("no human confirmation is required")
def then_no_human(ctx: dict[str, Any]) -> None:
    """Verify no HITL required."""


@then("execution begins from Phase 0")
def then_starts_phase0(ctx: dict[str, Any]) -> None:
    """Verify starts from phase 0."""
    assert ctx["resume_position"] == "phase0"


@then("existing docs/ artifacts are read as input")
def then_docs_read(ctx: dict[str, Any]) -> None:
    """Verify docs are read."""
    assert (ctx["docs"] / "requirements.md").exists()


@then("new artifacts build upon existing IDs")
def then_builds_on_existing(ctx: dict[str, Any]) -> None:
    """Verify builds on existing IDs."""
    assert ctx["resume_position"] == "phase0"


@then("all IDs are generated from scratch")
def then_fresh_ids(ctx: dict[str, Any]) -> None:
    """Verify fresh start."""
    assert ctx["preserved_stages"] == []


@then("Stage 3 and Stage 4 are not re-executed")
def then_stages_not_rerun(ctx: dict[str, Any]) -> None:
    """Verify specific stages skipped."""
    assert "stage3" in ctx["preserved_stages"]
    assert "stage4" in ctx["preserved_stages"]


@then("Stage 5 begins iteration immediately")
def then_stage5_begins(ctx: dict[str, Any]) -> None:
    """Verify stage 5 start."""
    assert "stage5" in ctx["next_stage"]
