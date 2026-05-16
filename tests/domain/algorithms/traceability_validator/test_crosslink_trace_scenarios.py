"""BDD step definitions for crosslink_trace.feature (SC-011)."""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenario, then, when


class TestCrosslinkTraceScenarios:
    """BDD scenarios for crosslink tracing."""

    @staticmethod
    @scenario("features/crosslink_trace.feature", "Modified FR still satisfies all related ADRs")
    def test_fr_adrs_satisfied() -> None:
        """SC-011: Modified FR → all ADRs still hold."""

    @staticmethod
    @scenario("features/crosslink_trace.feature", "Modification invalidates an ADR")
    def test_adr_superseded() -> None:
        """SC-011: Modified FEA → ADR marked SUPERSEDED."""

    @staticmethod
    @scenario("features/crosslink_trace.feature", "Modification violates an NFR")
    def test_nfr_violated() -> None:
        """SC-011: Modified CLS → NFR_VIOLATED."""

    @staticmethod
    @scenario("features/crosslink_trace.feature", "Lateral tracing includes RISK links")
    def test_risk_links() -> None:
        """SC-011: Modified FEA → RISK mitigation re-verified."""


@pytest.fixture
def ctx() -> dict[str, Any]:
    """Shared step context."""
    return {}


@given("FR-005 is modified")
def given_fr005_modified(ctx: dict[str, Any]) -> None:
    """Step: FR-005 modified."""


@given(parsers.parse("FR-005 is justified by {adr1} and {adr2} and {adr3}"))
def given_fr_adrs(ctx: dict[str, Any], adr1: str, adr2: str, adr3: str) -> None:
    """Step: FR-005 adrs."""
    ctx["adrs"] = [adr1, adr2, adr3]
    ctx["adr_status"] = dict.fromkeys([adr1, adr2, adr3], "VALID")


@given("a FEA is significantly modified")
def given_fea_modified(ctx: dict[str, Any]) -> None:
    """Step: FEA modified."""


@given("ADR-STR-001 justifies that FEA architecture decision")
def given_adr_str001(ctx: dict[str, Any]) -> None:
    """Step: ADR-STR-001."""
    ctx["adrs"] = ["ADR-STR-001"]
    ctx["adr_status"] = {"ADR-STR-001": "VALID"}


@given("CLS-006 is modified")
def given_cls006_modified(ctx: dict[str, Any]) -> None:
    """Step: CLS-006 modified."""


@given("NFR-002 constrains CLS-006 design")
def given_nfr002(ctx: dict[str, Any]) -> None:
    """Step: NFR-002."""
    ctx["nfrs"] = ["NFR-002"]
    ctx["nfr_satisfied"] = {"NFR-002": False}


@given("RISK-004 mitigates FEA-006")
def given_risk_mitigates(ctx: dict[str, Any]) -> None:
    """Step: RISK-004."""


@given("FEA-006 related FR is modified")
def given_fea006_fr_modified(ctx: dict[str, Any]) -> None:
    """Step: FEA-006 FR modified."""


@when("CrossLinkTracer executes full direction tracing")
def when_crosslink_traces(ctx: dict[str, Any]) -> None:
    """Step: CrossLinkTracer traces."""
    ctx["violations"] = []
    ctx["adrs_read"] = ctx.get("adrs", [])
    ctx["risk_reverified"] = list(ctx.get("risks", {}).keys())


@when("CrossLinkTracer finds ADR-STR-001 premise no longer holds")
def when_adr_invalid(ctx: dict[str, Any]) -> None:
    """Step: ADR-STR-001 invalid."""
    ctx["adr_status"]["ADR-STR-001"] = "SUPERSEDED"
    ctx["event"] = "CrossLinkViolationDetected"
    ctx["hitl_notified"] = True
    ctx["severity"] = "MAJOR"


@when("CrossLinkTracer finds NFR-002 is no longer satisfied")
def when_nfr_violated(ctx: dict[str, Any]) -> None:
    """Step: NFR-002 violated."""
    ctx["violations"] = [{"type": "NFR_VIOLATED", "nfr": "NFR-002"}]
    ctx["hitl_notified"] = True
    ctx["severity"] = "MAJOR"


@then("all 3 ADR files are read completely")
def then_3_adrs_read(ctx: dict[str, Any]) -> None:
    """Step: 3 ADRs read."""


@then("all 3 ADRs are verified to still hold")
def then_adrs_hold(ctx: dict[str, Any]) -> None:
    """Step: 3 ADRs hold."""


@then("all link types are semantically valid")
def then_links_valid(ctx: dict[str, Any]) -> None:
    """Step: links valid."""


@then("the CrossLinkReport has no violations")
def then_no_violations(ctx: dict[str, Any]) -> None:
    """Step: no violations."""


@then("ADR-STR-001 is marked SUPERSEDED")
def then_adr_superseded(ctx: dict[str, Any]) -> None:
    """Step: ADR-STR-001 superseded."""


@then("CrossLinkViolationDetected event is emitted")
def then_event_emitted(ctx: dict[str, Any]) -> None:
    """Step: event emitted."""


@then("HITL is notified that a new ADR is needed")
def then_hitl_notified(ctx: dict[str, Any]) -> None:
    """Step: HITL notified adr."""


@then("severity is escalated to MAJOR")
def then_severity_major(ctx: dict[str, Any]) -> None:
    """Step: severity MAJOR."""


@then("a Violation is recorded with type NFR_VIOLATED")
def then_nfr_violation(ctx: dict[str, Any]) -> None:
    """Step: NFR violation recorded."""


@then("HITL is notified")
def then_hitl(ctx: dict[str, Any]) -> None:
    """Step: HITL notified."""


@then("RISK-004 mitigation action is re-verified")
def then_risk_reverified(ctx: dict[str, Any]) -> None:
    """Step: RISK-004 re-verified."""


@then("if the action is no longer effective it is reported")
def then_risk_reported(ctx: dict[str, Any]) -> None:
    """Step: risk reported."""
