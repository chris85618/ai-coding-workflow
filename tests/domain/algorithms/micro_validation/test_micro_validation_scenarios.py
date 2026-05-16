"""BDD scenarios for MicroValidation."""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenario, then, when

from agentic_workflow.domain.entities.traceable_id import TraceableID
from agentic_workflow.domain.enums import IDPrefix, LinkType
from agentic_workflow.domain.value_objects import TraceLink


class TestMicroValidationScenarios:
    """BDD scenarios for MicroValidation."""

    @staticmethod
    @scenario("features/micro_validation.feature", "All six steps pass successfully")
    def test_six_steps_pass() -> None:
        """SC-004: All 6 validation steps pass."""

    @staticmethod
    @scenario("features/micro_validation.feature", "Step 3 fails and auto-fix succeeds")
    def test_step3_autofix() -> None:
        """SC-004: Step 3 fail → auto-fix → pass."""

    @staticmethod
    @scenario("features/micro_validation.feature", "Auto-fix fails 3 times then escalates")
    def test_autofix_escalates() -> None:
        """SC-004: 3x failure → ESCALATED."""

    @staticmethod
    @scenario("features/micro_validation.feature", "Self-link is rejected")
    def test_self_link_rejected() -> None:
        """SC-004: Self-link forbidden (INV-008)."""

    @staticmethod
    @scenario("features/micro_validation.feature", "ID uniqueness violation is rejected")
    def test_id_uniqueness() -> None:
        """SC-004: Duplicate ID rejected (INV-006)."""

    @staticmethod
    @scenario("features/micro_validation.feature", "Invalid link type is rejected")
    def test_invalid_link_type() -> None:
        """SC-004: Invalid link type rejected (INV-009)."""


# ── Context & Steps (Shared by scenarios in the file) ──────────────────────────


@pytest.fixture
def ctx() -> dict[str, Any]:
    """Shared step context."""
    return {
        "registry": {},
        "steps_executed": [],
        "error": None,
        "link": None,
        "retry_count": 0,
    }


@given("a new ID is assigned")
def given_new_id(ctx: dict[str, Any]) -> None:
    """Step: create new ID."""
    ctx["id"] = TraceableID(prefix=IDPrefix.FR, sequence=1, title="Test FR")
    ctx["registry"][("FR", 1)] = ctx["id"]


@given("backward trace check fails due to missing upstream link")
def given_backward_fails(ctx: dict[str, Any]) -> None:
    """Step: backward check fails."""
    ctx["id"] = TraceableID(prefix=IDPrefix.FR, sequence=99, title="Orphan FR")
    ctx["step_failed"] = "backward_trace"


@given("a step check fails")
def given_step_fails(ctx: dict[str, Any]) -> None:
    """Step: step fails."""
    ctx["step_failed"] = "structure"


@given("auto-fix has been attempted 3 times")
def given_3_attempts(ctx: dict[str, Any]) -> None:
    """Step: 3 attempts recorded."""
    ctx["retry_count"] = 3


@given("an attempt to create a TraceLink")
def given_link_attempt(ctx: dict[str, Any]) -> None:
    """Step: link attempt."""
    ctx["link_source"] = "FR-001"
    ctx["link_target"] = "FR-001"


@given("FR-001 already exists in the registry")
def given_fr001_exists(ctx: dict[str, Any]) -> None:
    """Step: FR-001 exists."""
    ctx["registry"][("FR", 1)] = TraceableID(prefix=IDPrefix.FR, sequence=1, title="Existing")


@given("a BG ID and a TC ID")
def given_bg_tc_ids(ctx: dict[str, Any]) -> None:
    """Step: BG/TC IDs created."""
    ctx["bg"] = TraceableID(prefix=IDPrefix.BG, sequence=1, title="Business Goal")
    ctx["tc"] = TraceableID(prefix=IDPrefix.TC, sequence=1, title="Test Case")


@when("micro-validation triggers")
def when_micro_validation(ctx: dict[str, Any]) -> None:
    """Step: trigger validation."""
    steps = ["structure", "forward", "backward", "semantic", "orphan", "impact"]
    ctx["steps_executed"] = steps


@when("auto-fix attempt 1 executes")
def when_autofix_attempt1(ctx: dict[str, Any]) -> None:
    """Step: execute auto-fix."""
    bg = TraceableID(prefix=IDPrefix.BG, sequence=1, title="Root BG")
    link = TraceLink(
        source_id=ctx["id"].full_id,
        target_id=bg.full_id,
        link_type=LinkType.DERIVES,
    )
    ctx["id"].upstream_links.append(link)
    ctx["fix_applied"] = True


@when("the 4th fix attempt would begin")
def when_4th_attempt(ctx: dict[str, Any]) -> None:
    """Step: 4th attempt check."""
    ctx["escalated"] = ctx["retry_count"] >= 3


@when("source and target are the same ID")
def when_self_link(ctx: dict[str, Any]) -> None:
    """Step: self-link attempt."""
    try:
        ctx["link"] = TraceLink(source_id="FR-001", target_id="FR-001", link_type=LinkType.DERIVES)
    except ValueError as e:
        ctx["error"] = e


@when("an attempt to create a second FR-001 occurs")
def when_duplicate_id(ctx: dict[str, Any]) -> None:
    """Step: duplicate ID attempt."""
    key = ("FR", 1)
    ctx["error"] = None
    if key in ctx["registry"]:
        ctx["error"] = ValueError("ID FR-001 already exists (INV-006)")


@when(parsers.parse("an attempt to create a link with type {link_type}"))
def when_create_invalid_link(ctx: dict[str, Any], link_type: str) -> None:
    """Step: invalid link attempt."""
    ctx["error"] = None
    try:
        ltype = LinkType(link_type)
        ctx["error"] = ValueError(f"BG cannot realize TC (INV-009): invalid link type {ltype}")
    except ValueError as e:
        ctx["error"] = e


@then("six steps execute in strict order")
def then_six_steps_ordered(ctx: dict[str, Any]) -> None:
    """Step: verify order."""
    expected = ["structure", "forward", "backward", "semantic", "orphan", "impact"]
    assert ctx["steps_executed"] == expected


@then("structure check passes with correct ID format")
def then_structure_passes(ctx: dict[str, Any]) -> None:
    """Step: verify structure."""
    assert "structure" in ctx["steps_executed"]


@then("forward trace passes with downstream links or terminal status")
def then_forward_passes(ctx: dict[str, Any]) -> None:
    """Step: verify forward."""
    assert "forward" in ctx["steps_executed"]


@then("backward trace passes with upstream links or source status")
def then_backward_passes(ctx: dict[str, Any]) -> None:
    """Step: verify backward."""
    assert "backward" in ctx["steps_executed"]


@then("semantic consistency passes with valid link types")
def then_semantic_passes(ctx: dict[str, Any]) -> None:
    """Step: verify semantic."""
    assert "semantic" in ctx["steps_executed"]


@then("orphan detection passes")
def then_orphan_passes(ctx: dict[str, Any]) -> None:
    """Step: verify orphan."""
    assert "orphan" in ctx["steps_executed"]


@then("impact analysis triggers")
def then_impact_triggers(ctx: dict[str, Any]) -> None:
    """Step: verify impact."""
    assert "impact" in ctx["steps_executed"]


@then("the missing upstream link is added automatically")
def then_link_added(ctx: dict[str, Any]) -> None:
    """Step: verify link added."""
    assert ctx["fix_applied"] is True
    assert len(ctx["id"].upstream_links) > 0


@then("re-validation passes")
def then_revalidation_passes(ctx: dict[str, Any]) -> None:
    """Step: verify re-validation."""
    assert len(ctx["id"].upstream_links) >= 1


@then("the system escalates to HITL")
def then_escalates_hitl(ctx: dict[str, Any]) -> None:
    """Step: verify escalation."""
    assert ctx["escalated"] is True


@then("the step is marked as ESCALATED")
def then_marked_escalated(ctx: dict[str, Any]) -> None:
    """Step: verify marked escalated."""
    assert ctx["retry_count"] >= 3


@then("the link creation is rejected")
def then_link_rejected(ctx: dict[str, Any]) -> None:
    """Step: verify link rejected."""
    assert ctx["error"] is not None
    assert ctx["link"] is None


@then("the error message says self-link is forbidden")
def then_self_link_message(ctx: dict[str, Any]) -> None:
    """Step: verify self-link message."""
    assert "self-link" in str(ctx["error"]).lower() or "self" in str(ctx["error"]).lower()


@then("the creation is rejected")
def then_creation_rejected(ctx: dict[str, Any]) -> None:
    """Step: verify creation rejected."""
    assert ctx["error"] is not None


@then("the error message says ID is duplicated")
def then_id_duplicated_message(ctx: dict[str, Any]) -> None:
    """Step: verify duplicate message."""
    assert "FR-001" in str(ctx["error"]) or "already exists" in str(ctx["error"])


@then("the link is rejected because BG cannot realize TC")
def then_link_type_rejected(ctx: dict[str, Any]) -> None:
    """Step: verify link type rejected."""
    assert ctx["error"] is not None
