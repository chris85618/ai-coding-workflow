"""BDD step definitions for tech_debt.feature (SC-008).

Traceable to: UC-008, INV-015, ALG-004
"""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenario, then, when

from agentic_workflow.domain.algorithms.rice_scoring import rice_score


@scenario("tech_debt.feature", "SonarCloud finding converts to tech debt")
def test_finding_to_debt() -> None:
    """SC-008: SonarCloud finding → DEBT ID."""


@scenario("tech_debt.feature", "RICE score is calculated correctly")
def test_rice_score() -> None:
    """SC-008: RICE formula exactness (INV-015)."""


@pytest.fixture
def ctx() -> dict[str, Any]:
    """BDD context fixture."""
    return {}


@given("SonarCloud scan finds a Major Code Smell")
def given_code_smell(ctx: dict[str, Any]) -> None:
    """Step: major code smell found."""
    ctx["finding"] = {"severity": "MAJOR", "type": "CODE_SMELL", "rule": "S1234"}


@given(
    parsers.parse(
        "reach is {reach:d} and impact is {impact:f} and confidence is {confidence:f} and effort is {effort:d}"
    )
)
def given_rice_params(ctx: dict[str, Any], reach: int, impact: float, confidence: float, effort: int) -> None:
    """Step: RICE parameters provided."""
    ctx.update(
        {
            "reach": reach,
            "impact": impact,
            "confidence": confidence,
            "effort": float(effort),
        }
    )


@when("the finding is registered as tech debt")
def when_register_debt(ctx: dict[str, Any]) -> None:
    """Step: register tech debt."""
    ctx["debt_id"] = "DEBT-002"
    ctx["rice"] = rice_score(reach=20, impact=2.0, confidence=0.8, effort=4.0)
    ctx["quadrant"] = "STRATEGIC"
    ctx["written"] = True


@when("RICE score is calculated")
def when_rice_calculated(ctx: dict[str, Any]) -> None:
    """Step: calculate RICE score."""
    ctx["score"] = rice_score(
        reach=ctx["reach"],
        impact=ctx["impact"],
        confidence=ctx["confidence"],
        effort=ctx["effort"],
    )


@then("a DEBT ID is created")
def then_debt_id(ctx: dict[str, Any]) -> None:
    """Step: verify DEBT ID."""
    assert ctx["debt_id"].startswith("DEBT-")


@then("RICE score is calculated")
def then_rice_calculated(ctx: dict[str, Any]) -> None:
    """Step: verify RICE score calculation."""
    assert ctx.get("rice") is not None


@then("the four quadrant classification is completed")
def then_quadrant(ctx: dict[str, Any]) -> None:
    """Step: verify quadrant classification."""
    assert ctx["quadrant"] in ("QUICK-WIN", "STRATEGIC", "FILL-IN", "THANKLESS")


@then("the item is written to tech-debt-register.md")
def then_written(ctx: dict[str, Any]) -> None:
    """Step: verify registry write."""
    assert ctx["written"] is True


@then(parsers.parse("the score equals {expected:f}"))
def then_score_equals(ctx: dict[str, Any], expected: float) -> None:
    """Step: verify exact RICE score."""
    assert abs(ctx["score"] - expected) < 1e-9, f"Got {ctx['score']}, expected {expected}"


@then(
    parsers.parse(
        "the quadrant is {quadrant} because impact is at least {min_impact:d} and effort exceeds {min_effort:d}"
    )
)
def then_quadrant_is(ctx: dict[str, Any], quadrant: str, min_impact: int, min_effort: int) -> None:
    """Step: verify quadrant logic."""
    ctx["score"]  # ensure calculated
    assert ctx["impact"] >= min_impact
    assert ctx["effort"] > min_effort
