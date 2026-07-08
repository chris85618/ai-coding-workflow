"""Orchestration Adapter — Single-Node Registry.

Traceable to: FR-077, FR-078, ADR-STR-033
A plain lookup table from workflow-document step names to in-process
deterministic node functions. It carries no edges, no sequencing and no
loops: orchestration authority lives exclusively in the exported Archon
workflow document (ADR-STR-033 prohibition on internal engines).
"""

from __future__ import annotations

from collections.abc import Callable

from agentic_workflow.adapters.orchestration.nodes import (
    node_absorb_debt,
    node_advance_stage,
    node_agent_alpha_critique,
    node_agent_beta_resolve,
    node_align_check,
    node_auto_gate,
    node_complete_pipeline,
    node_inject_assumptions,
    node_iterate_stage,
    node_phase_0_init,
    node_phase_1_understanding,
    node_phase_2_analysis,
    node_phase_9_ship,
    node_phase_10_retro,
    node_rollback,
    node_root_cause_leftshift,
    node_security_audit,
    node_sonarcloud_gate,
    node_stage_6_formal,
    node_start_pipeline,
    node_step_0_format,
    node_step_1_id_structure,
    node_step_2_forward_trace,
    node_step_3_backward_trace,
    node_step_4_semantic,
    node_step_5_5_lateral_trace,
    node_step_5_7_lesson_reuse,
    node_step_5_orphan,
    node_step_6_trigger_impact,
    node_step_7_record_change,
    node_update_constraints,
)
from agentic_workflow.adapters.orchestration.state_mapper import WorkflowState
from agentic_workflow.domain.algorithms.convergence import ConvergenceDetector
from agentic_workflow.domain.algorithms.iter_loop import IterationLoop

NodeFunction = Callable[[WorkflowState], WorkflowState]
RouterFunction = Callable[[WorkflowState], str]

_STAGE_POSITIONS = {
    "stage_3_planning": "stage3",
    "stage_4_algorithm": "stage4",
    "stage_5_ooad": "stage5",
    "stage_6_formal": "stage6",
    "stage_7_bdd": "stage7",
    "stage_8_tdd": "stage8",
}


def positioned_advance(position: str, state: WorkflowState) -> WorkflowState:
    """Advance the pipeline to an explicit canonical position (ALG-001 order)."""
    state["current_position"] = position
    return node_advance_stage(state)


def stage_3_planning(state: WorkflowState) -> WorkflowState:
    """Stage 3: Technical Planning and Requirements."""
    positions = _STAGE_POSITIONS
    return positioned_advance(positions["stage_3_planning"], state)


def stage_4_algorithm(state: WorkflowState) -> WorkflowState:
    """Stage 4: Algorithm Design and Complexity."""
    positions = _STAGE_POSITIONS
    return positioned_advance(positions["stage_4_algorithm"], state)


def stage_5_ooad(state: WorkflowState) -> WorkflowState:
    """Stage 5: Object-Oriented Analysis and Design."""
    positions = _STAGE_POSITIONS
    return positioned_advance(positions["stage_5_ooad"], state)


def stage_6_formal(state: WorkflowState) -> WorkflowState:
    """Stage 6: Formal Verification and Invariants."""
    positions = _STAGE_POSITIONS
    state = positioned_advance(positions["stage_6_formal"], state)
    return node_stage_6_formal(state)


def stage_7_bdd(state: WorkflowState) -> WorkflowState:
    """Stage 7: Behavior-Driven Development and Scenarios."""
    positions = _STAGE_POSITIONS
    return positioned_advance(positions["stage_7_bdd"], state)


def stage_8_tdd(state: WorkflowState) -> WorkflowState:
    """Stage 8: Test-Driven Development and Implementation."""
    positions = _STAGE_POSITIONS
    return positioned_advance(positions["stage_8_tdd"], state)


def check_fixed_point(state: WorkflowState) -> str:
    """Route convergence outcome: continue (beta), align (exit_loop), or degrade (rollback)."""
    it, hist = state.get("iteration_count", 0), state.get("findings_history", [])
    curr = state.get("current_findings", [])
    res = ConvergenceDetector.check_convergence(iteration_count=it, findings_per_iter=hist, current_findings=curr)
    return ConvergenceDetector.route_fixed_point(res)


def hitl_gate_choice(state: WorkflowState) -> str:
    """Human-in-the-loop decision routing using domain IterationLoop policy."""
    gate_decision = state.get("gate_decision", "pass")
    return IterationLoop.route_hitl_gate(gate_decision)


def route_debt(state: WorkflowState) -> str:
    """Continuous routing: FAIL gates flow into debt absorption, never hard-stop."""
    return "debt" if state.get("last_gate_decision") == "fail" else "pass"


NODE_REGISTRY: dict[str, NodeFunction] = {
    "inject": node_inject_assumptions,
    "start": node_start_pipeline,
    "phase_0": node_phase_0_init,
    "phase_1": node_phase_1_understanding,
    "phase_2": node_phase_2_analysis,
    "stage_3_planning": stage_3_planning,
    "stage_4_algorithm": stage_4_algorithm,
    "stage_5_ooad": stage_5_ooad,
    "stage_6_formal": stage_6_formal,
    "stage_7_bdd": stage_7_bdd,
    "stage_8_tdd": stage_8_tdd,
    "alpha": node_agent_alpha_critique,
    "beta": node_agent_beta_resolve,
    "iterate": node_iterate_stage,
    "micro_val_step_0_format": node_step_0_format,
    "micro_val_step_1_id_structure": node_step_1_id_structure,
    "micro_val_step_2_forward_trace": node_step_2_forward_trace,
    "micro_val_step_3_backward_trace": node_step_3_backward_trace,
    "micro_val_step_4_semantic": node_step_4_semantic,
    "micro_val_step_5_orphan": node_step_5_orphan,
    "micro_val_step_5_5_lateral_trace": node_step_5_5_lateral_trace,
    "micro_val_step_5_7_lesson_reuse": node_step_5_7_lesson_reuse,
    "micro_val_step_6_trigger_impact": node_step_6_trigger_impact,
    "micro_val_step_7_record_change": node_step_7_record_change,
    "rca": node_root_cause_leftshift,
    "align": node_align_check,
    "rollback": node_rollback,
    "sonar_gate": node_sonarcloud_gate,
    "sonar_debt": node_absorb_debt,
    "security_audit": node_security_audit,
    "security_debt": node_absorb_debt,
    "phase_9": node_phase_9_ship,
    "phase_10": node_phase_10_retro,
    "update_constraints": node_update_constraints,
    "gate": node_auto_gate,
    "complete": node_complete_pipeline,
}

ROUTER_REGISTRY: dict[str, RouterFunction] = {
    "check_fixed_point": check_fixed_point,
    "hitl_gate_choice": hitl_gate_choice,
    "route_debt": route_debt,
}
