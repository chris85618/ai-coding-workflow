"""Tests for the single-node registry (FR-077, FR-078, ADR-STR-033)."""

import re
from unittest.mock import patch

from agentic_workflow.adapters.archon.workflow_mapper import ArchonWorkflowMapper
from agentic_workflow.adapters.orchestration import node_registry
from agentic_workflow.adapters.orchestration.node_registry import (
    NODE_REGISTRY,
    ROUTER_REGISTRY,
    check_fixed_point,
    hitl_gate_choice,
    positioned_advance,
    route_debt,
    stage_3_planning,
    stage_4_algorithm,
    stage_5_ooad,
    stage_6_formal,
    stage_7_bdd,
    stage_8_tdd,
)
from agentic_workflow.adapters.orchestration.state_mapper import WorkflowState
from agentic_workflow.domain.aggregates.pipeline import Pipeline


class TestRegistryCompleteness:
    """Covers TC-ARCHON-013: workflow document and registry stay aligned."""

    def test_every_workflow_document_node_is_registered(self) -> None:
        """TC-ARCHON-013: Every --node in the exported document resolves in a registry."""
        positions = list(Pipeline(pipeline_id="align").stages)
        doc = ArchonWorkflowMapper().to_workflow_yaml("align", positions)
        referenced = set(re.findall(r"--node (\S+)", doc))
        assert referenced
        node_registry_table = NODE_REGISTRY
        router_registry_table = ROUTER_REGISTRY
        registered = set(node_registry_table) | set(router_registry_table)
        assert referenced <= registered

    def test_registries_are_disjoint(self) -> None:
        """TC-ARCHON-014: A name is either a state node or a router, never both."""
        node_registry_table = NODE_REGISTRY
        router_registry_table = ROUTER_REGISTRY
        assert not set(node_registry_table) & set(router_registry_table)


class TestStageWrappers:
    """Covers TC-ARCHON-015: positioned advance keeps the canonical ALG-001 order."""

    def test_positioned_advance_sets_position_then_delegates(self) -> None:
        """positioned_advance stamps the canonical position before advancing."""
        state = WorkflowState(pipeline_id="p")
        with patch.object(node_registry, "node_advance_stage", side_effect=lambda s: s) as advance:
            result = positioned_advance("stage4", state)
        assert result["current_position"] == "stage4"
        advance.assert_called_once_with(state)

    def test_each_stage_wrapper_targets_its_canonical_position(self) -> None:
        """Every stage wrapper advances to its own canonical position."""
        wrappers = {
            "stage3": stage_3_planning,
            "stage4": stage_4_algorithm,
            "stage5": stage_5_ooad,
            "stage7": stage_7_bdd,
            "stage8": stage_8_tdd,
        }
        for position, wrapper in wrappers.items():
            state = WorkflowState(pipeline_id="p")
            with patch.object(node_registry, "node_advance_stage", side_effect=lambda s: s):
                result = wrapper(state)
            assert result["current_position"] == position

    def test_stage_6_wrapper_also_runs_formal_verification(self) -> None:
        """stage_6_formal composes advance with the formal verification node."""
        state = WorkflowState(pipeline_id="p")
        with (
            patch.object(node_registry, "node_advance_stage", side_effect=lambda s: s),
            patch.object(node_registry, "node_stage_6_formal", side_effect=lambda s: s) as formal,
        ):
            result = stage_6_formal(state)
        assert result["current_position"] == "stage6"
        formal.assert_called_once()


class TestRouters:
    """Covers TC-ARCHON-016~017: deterministic routing stays in-process."""

    def test_check_fixed_point_routes_to_beta_when_not_converged(self) -> None:
        """CRITICAL findings keep the α/β loop running (ALG-001)."""
        state = WorkflowState(pipeline_id="p", current_findings=["CRITICAL: missing validation"])
        assert check_fixed_point(state) == "beta"

    def test_check_fixed_point_routes_to_exit_loop_when_converged(self) -> None:
        """YAGNI-only findings reach the fixed point and exit the loop."""
        state = WorkflowState(pipeline_id="p", current_findings=["YAGNI: unnecessary log"])
        assert check_fixed_point(state) == "exit_loop"

    def test_hitl_gate_choice_passes_by_default(self) -> None:
        """TC-ARCHON-016: The HITL gate passes unless the decision is fail."""
        assert hitl_gate_choice(WorkflowState(pipeline_id="p")) == "pass"

    def test_hitl_gate_choice_returns_alpha_on_fail(self) -> None:
        """A failed gate decision re-enters the α critique."""
        assert hitl_gate_choice(WorkflowState(pipeline_id="p", gate_decision="fail")) == "alpha"

    def test_route_debt_on_fail(self) -> None:
        """TC-ARCHON-017: A FAIL gate routes into debt absorption, never hard-stop."""
        assert route_debt(WorkflowState(pipeline_id="p", last_gate_decision="fail")) == "debt"

    def test_route_debt_on_pass(self) -> None:
        """A passing gate skips debt absorption."""
        assert route_debt(WorkflowState(pipeline_id="p", last_gate_decision="pass")) == "pass"
