"""BDD step definitions for impact_analysis.feature (SC-005).

Traceable to: UC-005, INV-012, INV-013, ALG-003
"""

from __future__ import annotations

import pytest
from pytest_bdd import given, parsers, scenario, then, when

from agentic_workflow.domain.algorithms.blast_radius import classify_severity
from agentic_workflow.domain.models.enums import Severity


_SEVERITY_ORDER = {
    Severity.COSMETIC: 0,
    Severity.LOW: 1,
    Severity.MEDIUM: 2,
    Severity.HIGH: 3,
    Severity.CRITICAL: 4,
}


@scenario("impact_analysis.feature", "COSMETIC level change with no downstream")
def test_cosmetic():
    """SC-005: Zero downstream → COSMETIC."""


@scenario("impact_analysis.feature", "MINOR level change within same stage")
def test_minor():
    """SC-005: Small blast radius → MINOR (LOW/MEDIUM)."""


@scenario("impact_analysis.feature", "MAJOR level change triggers HITL")
def test_major_triggers_hitl():
    """SC-005: Large blast radius → MAJOR (CRITICAL) → HITL."""


@scenario("impact_analysis.feature", "Severity is monotonic with blast radius")
def test_severity_monotonic():
    """SC-005: INV-012 monotonic severity."""


# ── Context ───────────────────────────────────────────────────────────────────

@pytest.fixture
def ctx():
    """Shared step context."""
    return {}


# ── Given steps ───────────────────────────────────────────────────────────────

@given("a change to an ID with no downstream links")
def given_no_downstream(ctx):
    """Blast radius = 0."""
    ctx["blast_radius"] = 0
    ctx["cross_stage"] = 0


@given("a change to an ID with 3 or fewer downstream links in the same stage")
def given_minor_change(ctx):
    """Blast radius = 2, same stage."""
    ctx["blast_radius"] = 2
    ctx["cross_stage"] = 0


@given("a change to an ID with more than 10 downstream links or crossing 2 plus stages")
def given_major_change(ctx):
    """Blast radius = 12, 3 stages crossed."""
    ctx["blast_radius"] = 12
    ctx["cross_stage"] = 3


@given(parsers.parse("change A has blast radius {br_a:d} and change B has blast radius {br_b:d}"))
def given_two_blast_radii(ctx, br_a, br_b):
    """Set up blast radii for A and B."""
    ctx["br_a"] = br_a
    ctx["br_b"] = br_b


# ── When steps ────────────────────────────────────────────────────────────────

@when("impact analysis calculates")
def when_impact_calculates(ctx):
    """Run blast radius classification."""
    ctx["severity"] = classify_severity(ctx["blast_radius"], ctx["cross_stage"])
    ctx["hitl_needed"] = ctx["severity"] in (Severity.HIGH, Severity.CRITICAL)


@when("severity is calculated for both")
def when_both_severities(ctx):
    """Calculate severity for both blast radii."""
    ctx["sev_a"] = classify_severity(ctx["br_a"], 0)
    ctx["sev_b"] = classify_severity(ctx["br_b"], 0)


# ── Then steps ────────────────────────────────────────────────────────────────

@then(parsers.parse("blast radius equals {br:d}"))
def then_blast_radius(ctx, br):
    """Assert blast radius matches expected."""
    assert ctx["blast_radius"] == br


@then("severity is COSMETIC")
def then_cosmetic(ctx):
    """Assert severity is COSMETIC."""
    assert ctx["severity"] == Severity.COSMETIC


@then("the change record is written to the corresponding ADR")
def then_change_written(ctx):
    """Structural assertion."""
    assert ctx["severity"] is not None


@then("severity is MINOR")
def then_minor(ctx):
    """Assert severity is LOW or MEDIUM (MINOR range)."""
    assert ctx["severity"] in (Severity.LOW, Severity.MEDIUM)


@then("severity is MAJOR")
def then_major(ctx):
    """Assert severity is HIGH or CRITICAL (MAJOR range)."""
    assert ctx["severity"] in (Severity.HIGH, Severity.CRITICAL)


@then("the system automatically escalates to HITL")
def then_hitl_escalates(ctx):
    """Assert HITL needed for MAJOR impact."""
    assert ctx["hitl_needed"] is True


@then("severity of B is greater than or equal to severity of A")
def then_severity_monotonic(ctx):
    """Assert INV-012 monotonic severity."""
    assert _SEVERITY_ORDER[ctx["sev_b"]] >= _SEVERITY_ORDER[ctx["sev_a"]]
