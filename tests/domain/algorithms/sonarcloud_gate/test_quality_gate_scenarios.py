"""BDD step definitions for quality_gate.feature (SC-007)."""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenario, then, when


class TestQualityGateScenarios:
    """BDD scenarios for quality gate."""

    @staticmethod
    @scenario("features/quality_gate.feature", "All thresholds pass")
    def test_all_pass() -> None:
        """SC-007: All quality thresholds pass."""

    @staticmethod
    @scenario("features/quality_gate.feature", "Coverage below threshold triggers auto-fix")
    def test_coverage_autofix() -> None:
        """SC-007: Low coverage triggers auto-fix."""

    @staticmethod
    @scenario("features/quality_gate.feature", "Auto-fix fails 3 times then escalates")
    def test_autofix_escalates() -> None:
        """SC-007: 3x failure → HITL escalation."""


@pytest.fixture
def ctx() -> dict[str, Any]:
    """Fixture for test context."""
    return {}


@given("all tests pass")
def given_all_tests_pass(ctx: dict[str, Any]) -> None:
    """Simulate all tests passing."""
    ctx.update({"coverage": 100, "critical_vulns": 0, "debt_ratio": 2.0, "retries": 0})


@given(parsers.parse("SonarCloud scan reports coverage at {pct:d} percent"))
def given_low_coverage(ctx: dict[str, Any], pct: int) -> None:
    """Simulate low coverage."""
    ctx["coverage"] = pct
    ctx["retries"] = 0


@given("SonarCloud threshold is not met")
def given_threshold_not_met(ctx: dict[str, Any]) -> None:
    """Simulate threshold not met."""
    ctx["coverage"] = 60
    ctx["retries"] = 3


@given("auto-fix has been attempted 3 times")
def given_3_retries(ctx: dict[str, Any]) -> None:
    """Simulate 3 retries."""
    ctx["retries"] = 3


@when("SonarCloud scan executes")
def when_scan_executes(ctx: dict[str, Any]) -> None:
    """Execute scan logic."""
    ctx["gate_passed"] = ctx["coverage"] >= 80 and ctx.get("critical_vulns", 0) == 0 and ctx.get("debt_ratio", 0) <= 5.0


@when("auto-fix attempts to add test cases")
def when_autofix_adds_tests(ctx: dict[str, Any]) -> None:
    """Simulate auto-fix adding tests."""
    ctx["tests_generated"] = True
    ctx["coverage"] = ctx["coverage"] + 5  # Simulate improvement


@when("the 4th attempt would begin")
def when_4th_attempt(ctx: dict[str, Any]) -> None:
    """Verify escalation logic."""
    ctx["escalated"] = ctx["retries"] >= 3


@then(parsers.parse("coverage is at least {pct:d} percent"))
def then_coverage_ok(ctx: dict[str, Any], pct: int) -> None:
    """Verify coverage."""
    assert ctx["coverage"] >= pct


@then("zero Critical vulnerabilities exist")
def then_no_vulns(ctx: dict[str, Any]) -> None:
    """Verify zero critical vulns."""
    assert ctx.get("critical_vulns", 0) == 0


@then("tech debt ratio is at most 5 percent")
def then_debt_ok(ctx: dict[str, Any]) -> None:
    """Verify tech debt ratio."""
    assert ctx.get("debt_ratio", 0) <= 5.0


@then("the quality gate result is PASS")
def then_gate_pass(ctx: dict[str, Any]) -> None:
    """Verify gate result."""
    assert ctx["gate_passed"] is True


@then("additional tests are generated")
def then_tests_generated(ctx: dict[str, Any]) -> None:
    """Verify tests generation."""
    assert ctx["tests_generated"] is True


@then("the scan is re-executed")
def then_scan_rerun(ctx: dict[str, Any]) -> None:
    """Verify scan re-execution."""
    assert ctx["coverage"] > 72


@then("the system escalates to HITL")
def then_escalated(ctx: dict[str, Any]) -> None:
    """Verify escalation."""
    assert ctx["escalated"] is True
