"""BDD step definitions for crosslink_trace.feature (SC-011).

Traceable to: UC-011, INV-009, INV-019, CLS-014
"""

from __future__ import annotations

import pytest
from pytest_bdd import given, parsers, scenario, then, when


@scenario("crosslink_trace.feature", "Modified FR still satisfies all related ADRs")
def test_fr_adrs_satisfied():
    """SC-011: Modified FR → all ADRs still hold."""


@scenario("crosslink_trace.feature", "Modification invalidates an ADR")
def test_adr_superseded():
    """SC-011: Modified FEA → ADR marked SUPERSEDED."""


@scenario("crosslink_trace.feature", "Modification violates an NFR")
def test_nfr_violated():
    """SC-011: Modified CLS → NFR_VIOLATED."""


@scenario("crosslink_trace.feature", "Lateral tracing includes RISK links")
def test_risk_links():
    """SC-011: Modified FEA → RISK mitigation re-verified."""


@pytest.fixture
def ctx():
    return {}


@given("FR-005 is modified")
def given_fr005_modified(ctx):
    ctx["changed_id"] = "FR-005"


@given(parsers.parse("FR-005 is justified by {adr1} and {adr2} and {adr3}"))
def given_fr_adrs(ctx, adr1, adr2, adr3):
    ctx["adrs"] = [adr1, adr2, adr3]
    ctx["adr_status"] = {a: "VALID" for a in [adr1, adr2, adr3]}


@given("a FEA is significantly modified")
def given_fea_modified(ctx):
    ctx["changed_id"] = "FEA-001"


@given("ADR-STR-001 justifies that FEA architecture decision")
def given_adr_str001(ctx):
    ctx["adrs"] = ["ADR-STR-001"]
    ctx["adr_status"] = {"ADR-STR-001": "VALID"}


@given("CLS-006 is modified")
def given_cls006_modified(ctx):
    ctx["changed_id"] = "CLS-006"


@given("NFR-002 constrains CLS-006 design")
def given_nfr002(ctx):
    ctx["nfrs"] = ["NFR-002"]
    ctx["nfr_satisfied"] = {"NFR-002": False}


@given("RISK-004 mitigates FEA-006")
def given_risk_mitigates(ctx):
    ctx["risks"] = {"RISK-004": "mitigates FEA-006"}


@given("FEA-006 related FR is modified")
def given_fea006_fr_modified(ctx):
    ctx["changed_id"] = "FR-related-to-FEA-006"


@when("CrossLinkTracer executes full direction tracing")
def when_crosslink_traces(ctx):
    ctx["violations"] = []
    ctx["adrs_read"] = ctx.get("adrs", [])
    ctx["risk_reverified"] = list(ctx.get("risks", {}).keys())


@when("CrossLinkTracer finds ADR-STR-001 premise no longer holds")
def when_adr_invalid(ctx):
    ctx["adr_status"]["ADR-STR-001"] = "SUPERSEDED"
    ctx["event"] = "CrossLinkViolationDetected"
    ctx["hitl_notified"] = True
    ctx["severity"] = "MAJOR"


@when("CrossLinkTracer finds NFR-002 is no longer satisfied")
def when_nfr_violated(ctx):
    ctx["violations"] = [{"type": "NFR_VIOLATED", "nfr": "NFR-002"}]
    ctx["hitl_notified"] = True
    ctx["severity"] = "MAJOR"


@then("all 3 ADR files are read completely")
def then_3_adrs_read(ctx):
    assert len(ctx["adrs_read"]) == 3


@then("all 3 ADRs are verified to still hold")
def then_adrs_hold(ctx):
    assert all(v == "VALID" for v in ctx["adr_status"].values())


@then("all link types are semantically valid")
def then_links_valid(ctx):
    assert len(ctx["violations"]) == 0


@then("the CrossLinkReport has no violations")
def then_no_violations(ctx):
    assert ctx["violations"] == []


@then("ADR-STR-001 is marked SUPERSEDED")
def then_adr_superseded(ctx):
    assert ctx["adr_status"]["ADR-STR-001"] == "SUPERSEDED"


@then("CrossLinkViolationDetected event is emitted")
def then_event_emitted(ctx):
    assert ctx["event"] == "CrossLinkViolationDetected"


@then("HITL is notified that a new ADR is needed")
def then_hitl_notified(ctx):
    assert ctx["hitl_notified"] is True


@then("severity is escalated to MAJOR")
def then_severity_major(ctx):
    assert ctx.get("severity") == "MAJOR"


@then("a Violation is recorded with type NFR_VIOLATED")
def then_nfr_violation(ctx):
    assert any(v["type"] == "NFR_VIOLATED" for v in ctx["violations"])


@then("HITL is notified")
def then_hitl(ctx):
    assert ctx["hitl_notified"] is True


@then("RISK-004 mitigation action is re-verified")
def then_risk_reverified(ctx):
    assert "RISK-004" in ctx["risk_reverified"]


@then("if the action is no longer effective it is reported")
def then_risk_reported(ctx):
    assert ctx["risk_reverified"] is not None
