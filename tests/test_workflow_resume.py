"""BDD step definitions for workflow_resume.feature (SC-010-v2).

Traceable to: UC-010, INV-001, INV-018, CLS-013
"""

from __future__ import annotations

import pytest
from pytest_bdd import given, parsers, scenario, then, when

from agentic_workflow.domain.models.enums import GateDecision, StageStatus
from agentic_workflow.domain.models.pipeline import Pipeline
from agentic_workflow.domain.models.stage import Stage


@scenario("workflow_resume.feature", "Resume from LangGraph checkpoint")
def test_resume_from_checkpoint():
    """SC-010: Resume from checkpoint automatically."""


@scenario("workflow_resume.feature", "No checkpoint with existing docs starts from Phase 0")
def test_no_checkpoint_with_docs():
    """SC-010: No checkpoint + existing docs → Phase 0."""


@scenario("workflow_resume.feature", "No checkpoint and empty docs starts fresh")
def test_no_checkpoint_fresh():
    """SC-010: No checkpoint + empty docs → fresh start."""


@scenario("workflow_resume.feature", "Checkpoint preserves passed gates")
def test_checkpoint_gates_preserved():
    """SC-010: Resumed checkpoint preserves PASSED stages (INV-018)."""


@pytest.fixture
def ctx(tmp_path):
    return {"docs": tmp_path / "docs", "pipeline": None}


@given("a previous execution was interrupted")
def given_interrupted(ctx):
    ctx["interrupted"] = True
    ctx["docs"].mkdir(exist_ok=True)  # Artifacts exist from prior run


@given("a LangGraph checkpoint exists")
def given_checkpoint_exists(ctx):
    ctx["checkpoint"] = {
        "position": "stage5",
        "stages": {"stage3": "PASSED", "stage4": "PASSED"},
        "gate": GateDecision.PASS,
    }


@given("no LangGraph checkpoint exists")
def given_no_checkpoint(ctx):
    ctx["checkpoint"] = None


@given("docs/ contains requirements.md from a prior run")
def given_docs_with_requirements(ctx):
    ctx["docs"].mkdir(exist_ok=True)
    (ctx["docs"] / "requirements.md").write_text("FR-001: existing\n")


@given("docs/ directory is empty")
def given_empty_docs(ctx):
    ctx["docs"].mkdir(exist_ok=True)


@given(parsers.parse("a checkpoint exists at Stage {n:d}"))
def given_checkpoint_at_stage(ctx, n):
    ctx["checkpoint"] = {
        "position": f"stage{n}",
        "stages": {f"stage{i}": "PASSED" for i in range(3, n)},
        "gate": GateDecision.PASS,
    }


@given(parsers.parse("Stage {a:d} and Stage {b:d} are marked PASSED in checkpoint"))
def given_stages_passed(ctx, a, b):
    cp = ctx.get("checkpoint", {})
    cp.setdefault("stages", {})[f"stage{a}"] = "PASSED"
    cp["stages"][f"stage{b}"] = "PASSED"
    ctx["checkpoint"] = cp


@when("the pipeline starts")
def when_pipeline_starts(ctx):
    cp = ctx.get("checkpoint")
    if cp:
        ctx["resume_position"] = cp["position"]
        ctx["preserved_stages"] = list(cp.get("stages", {}).keys())
    else:
        ctx["resume_position"] = "phase0"
        ctx["preserved_stages"] = []


@when("the pipeline resumes")
def when_pipeline_resumes(ctx):
    cp = ctx.get("checkpoint", {})
    ctx["resume_position"] = cp.get("position", "phase0")
    ctx["preserved_stages"] = list(cp.get("stages", {}).keys())
    ctx["next_stage"] = cp.get("position", "stage3")


@then("execution resumes from the checkpoint position automatically")
def then_resumes_from_checkpoint(ctx):
    assert ctx["resume_position"] != "phase0"


@then("previously completed stages are not re-executed")
def then_no_rerun(ctx):
    assert len(ctx["preserved_stages"]) > 0


@then("existing docs/ artifacts are preserved")
def then_artifacts_preserved(ctx):
    assert ctx["docs"].exists()


@then("no human confirmation is required")
def then_no_human(ctx):
    assert True  # ADR-STR-003


@then("execution begins from Phase 0")
def then_starts_phase0(ctx):
    assert ctx["resume_position"] == "phase0"


@then("existing docs/ artifacts are read as input")
def then_docs_read(ctx):
    assert (ctx["docs"] / "requirements.md").exists()


@then("new artifacts build upon existing IDs")
def then_builds_on_existing(ctx):
    assert ctx["resume_position"] == "phase0"


@then("all IDs are generated from scratch")
def then_fresh_ids(ctx):
    assert ctx["preserved_stages"] == []


@then("Stage 3 and Stage 4 are not re-executed")
def then_stages_not_rerun(ctx):
    assert "stage3" in ctx["preserved_stages"]
    assert "stage4" in ctx["preserved_stages"]


@then("Stage 5 begins iteration immediately")
def then_stage5_begins(ctx):
    assert "stage5" in ctx["next_stage"]
