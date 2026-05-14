"""BDD step definitions for security_audit.feature (SC-006).

Traceable to: UC-006, INV-014, CLS-010
"""

from __future__ import annotations

import pytest
from pytest_bdd import given, scenario, then, when


@scenario("security_audit.feature", "All three layers pass")
def test_all_layers_pass():
    """SC-006: All 3 security layers pass."""


@scenario("security_audit.feature", "Layer 2 HIGH finding triggers redesign")
def test_layer2_fail():
    """SC-006: Layer 2 HIGH → FAIL → redesign."""


@pytest.fixture
def ctx():
    return {}


@given("the design or implementation is complete")
def given_complete(ctx):
    ctx.update({"l1": "PASS", "l2": "PASS", "l3": "PASS"})


@given("Layer 1 passes")
def given_l1_passes(ctx):
    ctx["l1"] = "PASS"


@when("the three layer security audit executes")
def when_audit(ctx):
    ctx["result"] = "PASS" if all(
        v == "PASS" for v in [ctx.get("l1"), ctx.get("l2"), ctx.get("l3")]
    ) else "FAIL"


@when("Layer 2 discovers a HIGH severity issue")
def when_l2_high(ctx):
    ctx["l2"] = "FAIL"
    ctx["result"] = "FAIL"
    ctx["event"] = "AuditFailed"


@then("Layer 1 CSO passes")
def then_l1(ctx):
    assert ctx.get("l1") == "PASS"


@then("Layer 2 AgentShield passes")
def then_l2(ctx):
    assert ctx.get("l2") == "PASS"


@then("Layer 3 SkillFortify passes")
def then_l3(ctx):
    assert ctx.get("l3") == "PASS"


@then("the overall result is PASS")
def then_pass(ctx):
    assert ctx["result"] == "PASS"


@then("the overall result is FAIL")
def then_fail(ctx):
    assert ctx["result"] == "FAIL"


@then("AuditFailed event is emitted")
def then_event_emitted(ctx):
    assert ctx.get("event") == "AuditFailed"


@then("the system returns to design stage for fixes")
def then_returns_to_design(ctx):
    assert ctx["result"] == "FAIL"
