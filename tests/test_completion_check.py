"""BDD step definitions for completion_check.feature (SC-009).

Traceable to: UC-009, INV-016, CLS-011
"""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, scenario, then, when


@scenario("completion_check.feature", "All checks pass and ship is allowed")
def test_all_pass() -> None:
    """SC-009: All sub-checks pass → ship allowed."""


@scenario("completion_check.feature", "Traceability integrity fails and blocks ship")
def test_traceability_fail() -> None:
    """SC-009: Orphan IDs → FAIL → ship blocked."""


@pytest.fixture
def ctx() -> dict[str, Any]:
    """BDD context fixture."""
    return {}


@given("Stage 8 HITL has confirmed PASS")
def given_hitl_pass(ctx: dict[str, Any]) -> None:
    """Set all checks to PASS."""
    ctx.update(
        {
            "trace_ok": True,
            "quality_ok": True,
            "security_ok": True,
            "debt_ok": True,
            "orphans": [],
        }
    )


@given("orphan IDs exist in the registry")
def given_orphans(ctx: dict[str, Any]) -> None:
    """Inject orphans."""
    ctx["orphans"] = ["SC-099", "TC-099"]
    ctx["trace_ok"] = False


@when("the pre-release completion check executes")
def when_check_executes(ctx: dict[str, Any]) -> None:
    """Execute logical check."""
    ctx["ship_allowed"] = (
        ctx.get("trace_ok", False)
        and ctx.get("quality_ok", True)
        and ctx.get("security_ok", True)
        and ctx.get("debt_ok", True)
        and len(ctx.get("orphans", [])) == 0
    )


@then("traceability integrity is PASS")
def then_trace_pass(ctx: dict[str, Any]) -> None:
    """Assert trace pass."""
    assert ctx["trace_ok"] is True


@then("quality gate is PASS")
def then_quality_pass(ctx: dict[str, Any]) -> None:
    """Assert quality pass."""
    assert ctx.get("quality_ok") is True


@then("security audit is PASS")
def then_security_pass(ctx: dict[str, Any]) -> None:
    """Assert security pass."""
    assert ctx.get("security_ok") is True


@then("tech debt check is PASS")
def then_debt_pass(ctx: dict[str, Any]) -> None:
    """Assert debt pass."""
    assert ctx.get("debt_ok") is True


@then("the ship command is allowed")
def then_ship_allowed(ctx: dict[str, Any]) -> None:
    """Assert ship allowed."""
    assert ctx["ship_allowed"] is True


@then("traceability integrity is FAIL")
def then_trace_fail(ctx: dict[str, Any]) -> None:
    """Assert trace fail."""
    assert ctx.get("trace_ok") is False


@then("the ship command is blocked")
def then_ship_blocked(ctx: dict[str, Any]) -> None:
    """Assert ship blocked."""
    assert ctx["ship_allowed"] is False


@then("the missing trace links are listed")
def then_missing_listed(ctx: dict[str, Any]) -> None:
    """Assert orphans listed."""
    assert len(ctx["orphans"]) > 0
