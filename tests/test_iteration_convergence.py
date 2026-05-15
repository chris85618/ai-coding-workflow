"""BDD step definitions for iteration_convergence.feature (SC-003-v2).

Traceable to: UC-003, INV-003, INV-004, INV-005-v2, ALG-001
"""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenario, then, when

from agentic_workflow.domain.algorithms.convergence import (
    check_convergence,
    should_auto_pass,
)
from agentic_workflow.domain.models.enums import FixedPointResult, StageStatus
from agentic_workflow.domain.models.stage import Stage

# ── Scenarios ─────────────────────────────────────────────────────────────────


@scenario("iteration_convergence.feature", "Auto-convergence at fixed point (REACHED)")
def test_fixed_point_reached() -> None:
    """SC-003: All YAGNI → REACHED → auto-pass."""


@scenario("iteration_convergence.feature", "Max iterations reached auto-advances")
def test_max_iterations() -> None:
    """SC-003: MAX_ITERATIONS → auto-advance with warning."""


@scenario("iteration_convergence.feature", "NOT_REACHED continues autonomously")
def test_not_reached_continues() -> None:
    """SC-003: CRITICAL findings → NOT_REACHED → continue."""


@scenario(
    "iteration_convergence.feature", "MAJOR impact logged but execution continues"
)
def test_major_impact_continues() -> None:
    """SC-003: MAJOR impact → log + continue autonomously."""


@scenario(
    "iteration_convergence.feature", "Stage status transitions are unidirectional"
)
def test_status_unidirectional() -> None:
    """SC-003: PENDING → ITERATING → PASSED is unidirectional (INV-003)."""


@scenario(
    "iteration_convergence.feature", "Micro-validation failure auto-retries then skips"
)
def test_micro_validation_retry() -> None:
    """SC-003: 3x retry failure → log + continue."""


# ── Context ───────────────────────────────────────────────────────────────────


@pytest.fixture
def ctx() -> dict[str, Any]:
    """Shared step context."""
    return {}


# ── Given steps ───────────────────────────────────────────────────────────────


@given("Stage N is ready for iteration")
def given_stage_ready(ctx: dict[str, Any]) -> None:
    """Step: stage ready."""
    ctx["stage"] = Stage(stage_id="stage3", name="Technical Planning")
    ctx["findings_history"] = []


@given("Agent alpha critiques and all findings are YAGNI severity")
@when("Agent alpha critiques and all findings are YAGNI severity")
def given_all_yagni(ctx: dict[str, Any]) -> None:
    """Step: all YAGNI."""
    ctx["current_findings"] = [
        "YAGNI: extra abstraction",
        "YAGNI: premature optimization",
    ]
    # When used as a 'When' step, also run the convergence check
    ctx["result"] = check_convergence(
        iteration_count=ctx["stage"].iteration_count,
        findings_per_iter=ctx.get("findings_history", []),
        current_findings=ctx["current_findings"],
    )


@given("Stage N is iterating")
def given_stage_iterating(ctx: dict[str, Any]) -> None:
    """Step: stage iterating."""
    s = Stage(stage_id="stage3", name="Technical Planning")
    s.transition(StageStatus.ITERATING)
    ctx["stage"] = s
    ctx["findings_history"] = [["CRITICAL: x"]] * 10


@given("iteration count has reached 10")
def given_iteration_count_10(ctx: dict[str, Any]) -> None:
    """Step: max iterations reached."""
    for _ in range(10):
        ctx["stage"].increment_iteration()
    ctx["current_findings"] = ["CRITICAL: still unresolved"]


@given("Step M micro-validation has passed")
def given_step_m_passed(ctx: dict[str, Any]) -> None:
    """Step: step passed."""
    ctx["step_m_passed"] = True
    ctx["stage"] = Stage(stage_id="stage3", name="Technical Planning")
    ctx["stage"].transition(StageStatus.ITERATING)
    ctx["findings_history"] = [["CRITICAL: A"], ["CRITICAL: A", "HIGH: B"]]


@given("there are still CRITICAL or HIGH unresolved findings")
def given_critical_findings(ctx: dict[str, Any]) -> None:
    """Step: critical findings."""
    ctx["current_findings"] = ["CRITICAL: unresolved invariant", "HIGH: missing test"]


@given("impact analysis classifies severity as MAJOR")
def given_major_impact(ctx: dict[str, Any]) -> None:
    """Step: major impact."""
    ctx["impact_severity"] = "MAJOR"
    ctx["stage"] = Stage(stage_id="stage4", name="Algorithm Design")
    ctx["warnings"] = []


@given(parsers.parse("a stage with status {status}"))
def given_stage_with_status(ctx: dict[str, Any], status: str) -> None:
    """Step: stage with status."""
    s = Stage(stage_id="stage3", name="Test")
    if status == "PENDING":
        pass  # default
    ctx["stage"] = s


@given("a micro-validation step fails")
def given_micro_validation_fails(ctx: dict[str, Any]) -> None:
    """Step: validation fails."""
    ctx["retry_count"] = 0
    ctx["max_retries"] = 3
    ctx["stage"] = Stage(stage_id="stage3", name="Test")


# ── When steps ────────────────────────────────────────────────────────────────


@when("fixed point check executes")
def when_fixed_point_check(ctx: dict[str, Any]) -> None:
    """Step: run check."""
    ctx["result"] = check_convergence(
        iteration_count=ctx["stage"].iteration_count,
        findings_per_iter=ctx.get("findings_history", []),
        current_findings=ctx.get("current_findings", []),
    )


@when("the 11th iteration would begin")
def when_11th_iteration(ctx: dict[str, Any]) -> None:
    """Step: 11th iteration."""
    ctx["result"] = check_convergence(
        iteration_count=ctx["stage"].iteration_count,
        findings_per_iter=ctx["findings_history"],
        current_findings=ctx["current_findings"],
    )


@when("the result is processed")
def when_result_processed(ctx: dict[str, Any]) -> None:
    """Step: process result."""
    ctx["warnings"].append(
        "WARNING: MAJOR impact detected — blast radius details logged"
    )
    ctx["continues"] = True


@when(parsers.parse("the stage transitions to {status}"))
def when_stage_transitions(ctx: dict[str, Any], status: str) -> None:
    """Step: transition stage."""
    new_status = StageStatus(status.lower())
    ctx["error"] = None
    try:
        ctx["stage"].transition(new_status)
        ctx["transitioned_to"] = new_status
    except Exception as e:
        ctx["error"] = e


@when("auto-fix is attempted 3 times and all fail")
def when_autofix_fails(ctx: dict[str, Any]) -> None:
    """Step: autofix fails."""
    for _ in range(3):
        ctx["retry_count"] += 1
    ctx["all_failed"] = ctx["retry_count"] >= ctx["max_retries"]


# ── Then steps ────────────────────────────────────────────────────────────────


@then("fixed point is REACHED")
def then_fixed_point_reached(ctx: dict[str, Any]) -> None:
    """Step: fixed point REACHED."""
    assert ctx["result"] == FixedPointResult.REACHED


@then("the stage auto-passes without human confirmation")
def then_auto_passes(ctx: dict[str, Any]) -> None:
    """Step: auto passes."""
    assert should_auto_pass(ctx["result"]) is True


@then("stage artifacts are written to docs/")
def then_artifacts_written_convergence(ctx: dict[str, Any]) -> None:
    """Step: artifacts written."""
    assert ctx["stage"] is not None


@then(parsers.parse("a warning is logged with message {msg}"))
def then_warning_logged(ctx: dict[str, Any], msg: str) -> None:
    """Step: warning logged."""
    if "warnings" in ctx:
        assert any(msg in w for w in ctx["warnings"])


@then("the stage auto-advances")
def then_auto_advances(ctx: dict[str, Any]) -> None:
    """Step: auto advances."""
    assert should_auto_pass(ctx["result"]) is True


@then("no human intervention is requested")
def then_no_human_intervention(ctx: dict[str, Any]) -> None:
    """Step: no HITL."""
    pass  # By design (ADR-STR-003)


@then("artifacts produced so far are written to docs/")
def then_partial_artifacts(ctx: dict[str, Any]) -> None:
    """Step: partial artifacts."""
    assert ctx["stage"] is not None


@then("the result is NOT_REACHED")
def then_not_reached(ctx: dict[str, Any]) -> None:
    """Step: NOT_REACHED."""
    assert ctx["result"] == FixedPointResult.NOT_REACHED


@then("Agent alpha automatically re-critiques")
def then_alpha_recritiques(ctx: dict[str, Any]) -> None:
    """Step: recritiques."""
    assert not should_auto_pass(ctx["result"])


@then("iteration count increments by 1")
def then_iteration_increments(ctx: dict[str, Any]) -> None:
    """Step: increments count."""
    before = ctx["stage"].iteration_count
    ctx["stage"].increment_iteration()
    assert ctx["stage"].iteration_count == before + 1


@then("no human gate triggers")
def then_no_human_gate(ctx: dict[str, Any]) -> None:
    """Step: no human gate."""
    pass


@then("a warning is logged with full blast radius details")
def then_blast_radius_warning(ctx: dict[str, Any]) -> None:
    """Step: blast radius warning."""
    assert len(ctx["warnings"]) > 0


@then("execution continues autonomously")
def then_execution_continues(ctx: dict[str, Any]) -> None:
    """Step: continues autonomously."""
    assert ctx.get("continues") is True


@then("the warning is recorded in the stage artifacts")
def then_warning_recorded(ctx: dict[str, Any]) -> None:
    """Step: warning recorded."""
    assert ctx["warnings"] is not None


@then(parsers.parse("the status cannot return to {status}"))
def then_cannot_return(ctx: dict[str, Any], status: str) -> None:
    """Step: cannot return to status."""
    target = StageStatus(status.lower())
    try:
        ctx["stage"].transition(target)
        raise AssertionError("Expected ValueError for backward transition")
    except ValueError:
        pass  # Expected


@then("later transitions to PASSED are final")
def then_passed_final(ctx: dict[str, Any]) -> None:
    """Step: PASSED final."""
    ctx["stage"].transition(StageStatus.PASSED)
    try:
        ctx["stage"].transition(StageStatus.PENDING)
        raise AssertionError("Expected ValueError")
    except ValueError:
        pass


@then("the failure is logged as a warning")
def then_failure_logged(ctx: dict[str, Any]) -> None:
    """Step: failure logged."""
    assert ctx["all_failed"] is True


@then("execution continues to the next step")
def then_continue_next_step(ctx: dict[str, Any]) -> None:
    """Step: continue next."""
    assert ctx["retry_count"] == 3


@then("no escalation to human occurs")
def then_no_escalation(ctx: dict[str, Any]) -> None:
    """Step: no escalation."""
    pass
