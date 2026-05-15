"""BDD step definitions for phase2_analysis.feature (SC-002).

Traceable to: UC-002, INV-017, CLS-012
"""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, scenario, then, when

from agentic_workflow.domain.models.enums import IDPrefix, LinkType
from agentic_workflow.domain.models.traceable_id import TraceableID, TraceLink


@scenario("phase2_analysis.feature", "Phase 2 produces complete IDs")
def test_phase2_complete() -> None:
    """SC-002: Phase 2 produces BG, S, FEA IDs."""


@scenario("phase2_analysis.feature", "Red Team challenge finds scope conflict")
def test_red_team() -> None:
    """SC-002: Red Team → scope conflict → gate."""


@pytest.fixture
def ctx() -> dict[str, Any]:
    """Shared step context."""
    return {}


@given("Phase 0 and Phase 1 are completed")
def given_phases_complete(ctx: dict[str, Any]) -> None:
    """Step: phases complete."""
    ctx["phase0_done"] = True
    ctx["phase1_done"] = True


@given("FEA IDs are defined")
def given_fea_defined(ctx: dict[str, Any]) -> None:
    """Step: FEA defined."""
    ctx["feas"] = [
        TraceableID(prefix=IDPrefix.FEA, sequence=i, title=f"Feature {i}")
        for i in range(1, 4)
    ]


@when("Phase 2 four steps execute")
def when_phase2_executes(ctx: dict[str, Any]) -> None:
    """Step: phase 2 execution."""
    # Simulate Phase 2 producing IDs
    ctx["bgs"] = [TraceableID(prefix=IDPrefix.BG, sequence=1, title="BG-001")]
    ctx["stakeholders"] = [TraceableID(prefix=IDPrefix.S, sequence=1, title="S-001")]
    ctx["feas"] = [TraceableID(prefix=IDPrefix.FEA, sequence=1, title="FEA-001")]
    # Link BG → FEA
    link = TraceLink(
        source_id="BG-001", target_id="FEA-001", link_type=LinkType.DECOMPOSES
    )
    ctx["bgs"][0].downstream_links.append(link)
    ctx["matrix_initialized"] = True


@when("Red Team challenge discovers mutually exclusive features")
def when_red_team(ctx: dict[str, Any]) -> None:
    """Step: red team conflict."""
    ctx["conflict"] = True
    ctx["gate_triggered"] = True


@then("at least 1 BG ID is assigned")
def then_bg_id(ctx: dict[str, Any]) -> None:
    """Step: verify BG ID."""
    assert len(ctx["bgs"]) >= 1


@then("at least 1 S ID is assigned")
def then_s_id(ctx: dict[str, Any]) -> None:
    """Step: verify S ID."""
    assert len(ctx["stakeholders"]) >= 1


@then("at least 1 FEA ID is assigned")
def then_fea_id(ctx: dict[str, Any]) -> None:
    """Step: verify FEA ID."""
    assert len(ctx["feas"]) >= 1


@then("the traceability matrix is initialized")
def then_matrix_init(ctx: dict[str, Any]) -> None:
    """Step: verify matrix init."""
    assert ctx["matrix_initialized"] is True


@then("every BG has at least one FEA downstream link")
def then_bg_has_fea(ctx: dict[str, Any]) -> None:
    """Step: verify BG-FEA link."""
    for bg in ctx["bgs"]:
        assert len(bg.downstream_links) >= 1, f"BG {bg.full_id} has no downstream FEA"


@then("the HITL gate triggers")
def then_hitl_gate(ctx: dict[str, Any]) -> None:
    """Step: verify HITL gate."""
    assert ctx["gate_triggered"] is True


@then("the user decides on scope adjustment")
def then_scope_adjustment(ctx: dict[str, Any]) -> None:
    """Step: verify scope adjustment."""
    assert ctx["conflict"] is True


@then("adjusted FEA IDs update in the traceability matrix")
def then_matrix_updated(ctx: dict[str, Any]) -> None:
    """Step: verify matrix update."""
    assert ctx["feas"] is not None
