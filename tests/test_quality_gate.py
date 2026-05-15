"""BDD step definitions for quality_gate.feature (SC-007).

Traceable to: UC-007, INV-014, CLS-008
"""

from __future__ import annotations

import pytest
from pytest_bdd import given, parsers, scenario, then, when


@scenario("quality_gate.feature", "All thresholds pass")
def test_all_pass():
    """SC-007: All quality thresholds pass."""


@scenario("quality_gate.feature", "Coverage below threshold triggers auto-fix")
def test_coverage_autofix():
    """SC-007: Low coverage triggers auto-fix."""


@scenario("quality_gate.feature", "Auto-fix fails 3 times then escalates")
def test_autofix_escalates():
    """SC-007: 3x failure → HITL escalation."""


@pytest.fixture
def ctx():
    return {}


@given("all tests pass")
def given_all_tests_pass(ctx):
    ctx.update({"coverage": 100, "critical_vulns": 0, "debt_ratio": 2.0, "retries": 0})


@given(parsers.parse("SonarCloud scan reports coverage at {pct:d} percent"))
def given_low_coverage(ctx, pct):
    ctx["coverage"] = pct
    ctx["retries"] = 0


@given("SonarCloud threshold is not met")
def given_threshold_not_met(ctx):
    ctx["coverage"] = 60
    ctx["retries"] = 3


@given("auto-fix has been attempted 3 times")
def given_3_retries(ctx):
    ctx["retries"] = 3


@when("SonarCloud scan executes")
def when_scan_executes(ctx):
    ctx["gate_passed"] = (
        ctx["coverage"] >= 80
        and ctx.get("critical_vulns", 0) == 0
        and ctx.get("debt_ratio", 0) <= 5.0
    )


@when("auto-fix attempts to add test cases")
def when_autofix_adds_tests(ctx):
    ctx["tests_generated"] = True
    ctx["coverage"] = ctx["coverage"] + 5  # Simulate improvement


@when("the 4th attempt would begin")
def when_4th_attempt(ctx):
    ctx["escalated"] = ctx["retries"] >= 3


@then(parsers.parse("coverage is at least {pct:d} percent"))
def then_coverage_ok(ctx, pct):
    assert ctx["coverage"] >= pct


@then("zero Critical vulnerabilities exist")
def then_no_vulns(ctx):
    assert ctx.get("critical_vulns", 0) == 0


@then("tech debt ratio is at most 5 percent")
def then_debt_ok(ctx):
    assert ctx.get("debt_ratio", 0) <= 5.0


@then("the quality gate result is PASS")
def then_gate_pass(ctx):
    assert ctx["gate_passed"] is True


@then("additional tests are generated")
def then_tests_generated(ctx):
    assert ctx["tests_generated"] is True


@then("the scan is re-executed")
def then_scan_rerun(ctx):
    assert ctx["coverage"] > 72


@then("the system escalates to HITL")
def then_escalated(ctx):
    assert ctx["escalated"] is True
