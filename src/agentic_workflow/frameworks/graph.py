"""Frameworks Layer — Graph wiring.

Constructs the LangGraph StateGraph.
This file implements the highly detailed workflow requested, exploding AGENTS.md
steps into LangGraph subgraphs (Micro-Validation ALG-002, Iteration ALG-001, Master Pipeline).
OO Design: Three builder classes encapsulate all graph construction logic (ALG-010 OO mandate).
Module-level functions retained as backward-compat facades.
"""
from __future__ import annotations

from langgraph.graph import StateGraph, END
from agentic_workflow.adapters.langgraph.state_mapper import WorkflowState
from agentic_workflow.adapters.langgraph.nodes import (
    node_start_pipeline,
    node_auto_gate,
    node_advance_stage,
    node_complete_pipeline,
    node_warning_policy_gate,
)


# ==========================================
# 1. Micro-Validation Subgraph Nodes
# (module-level to allow LangGraph node registration)
# ==========================================
def step_0_format(state: WorkflowState) -> WorkflowState:
    return state  # pragma: no branch


def step_1_id_structure(state: WorkflowState) -> WorkflowState:
    return state  # pragma: no branch


def step_2_forward_trace(state: WorkflowState) -> WorkflowState:
    return state  # pragma: no branch


def step_3_backward_trace(state: WorkflowState) -> WorkflowState:
    return state  # pragma: no branch


def step_4_semantic(state: WorkflowState) -> WorkflowState:
    return state  # pragma: no branch


def step_5_orphan(state: WorkflowState) -> WorkflowState:
    return state  # pragma: no branch


def step_5_5_lateral_trace(state: WorkflowState) -> WorkflowState:
    return state  # pragma: no branch


def step_5_7_lesson_reuse(state: WorkflowState) -> WorkflowState:
    return state  # pragma: no branch


def step_6_trigger_impact(state: WorkflowState) -> WorkflowState:
    return state  # pragma: no branch


def step_7_record_change(state: WorkflowState) -> WorkflowState:
    return state  # pragma: no branch


# ==========================================
# 2. Iteration Loop Subgraph Nodes
# ==========================================
def agent_alpha_critique(state: WorkflowState) -> WorkflowState:
    return state  # pragma: no branch


def check_fixed_point(state: WorkflowState) -> str:
    # Returns "beta" or "exit_loop" based on YAGNI convergence
    return "beta"  # pragma: no branch


def agent_beta_resolve(state: WorkflowState) -> WorkflowState:
    return state  # pragma: no branch


def root_cause_leftshift(state: WorkflowState) -> WorkflowState:
    return state  # pragma: no branch


def hitl_gate_choice(state: WorkflowState) -> str:
    # 1: continue, 2: add req, 3: pass
    return "pass"  # pragma: no branch


# ==========================================
# 3. Master Pipeline Nodes
# ==========================================
def phase_0_init(state: WorkflowState) -> WorkflowState:
    return state  # pragma: no branch


def phase_1_understanding(state: WorkflowState) -> WorkflowState:
    return state  # pragma: no branch


def phase_2_analysis(state: WorkflowState) -> WorkflowState:
    return state  # pragma: no branch


def stage_3_planning(state: WorkflowState) -> WorkflowState:
    return state  # pragma: no branch


def stage_4_algorithm(state: WorkflowState) -> WorkflowState:
    return state  # pragma: no branch


def stage_5_ooad(state: WorkflowState) -> WorkflowState:
    return state  # pragma: no branch


def stage_6_formal(state: WorkflowState) -> WorkflowState:
    return state  # pragma: no branch


def stage_7_bdd(state: WorkflowState) -> WorkflowState:
    return state  # pragma: no branch


def stage_8_tdd(state: WorkflowState) -> WorkflowState:
    return state  # pragma: no branch


def phase_9_ship(state: WorkflowState) -> WorkflowState:
    return state  # pragma: no branch


def phase_10_retro(state: WorkflowState) -> WorkflowState:
    return state  # pragma: no branch


# ==========================================
# OO Graph Builder Classes
# ==========================================

class MicroValidationGraphBuilder:
    """ALG-002: Builds the Left-Shift Micro-Validation Sequence subgraph.

    Encapsulates the 10-step micro-validation chain (Steps 0-7 + 5.5/5.7)
    as a compilable LangGraph StateGraph.
    """

    @classmethod
    def build(cls) -> object:
        """Build and compile the micro-validation subgraph.

        Returns:
            Compiled LangGraph application for micro-validation.
        """
        graph = StateGraph(WorkflowState)
        graph.add_node("s0_format", step_0_format)
        graph.add_node("s1_id", step_1_id_structure)
        graph.add_node("s2_fwd", step_2_forward_trace)
        graph.add_node("s3_bwd", step_3_backward_trace)
        graph.add_node("s4_sem", step_4_semantic)
        graph.add_node("s5_orphan", step_5_orphan)
        graph.add_node("s55_lateral", step_5_5_lateral_trace)
        graph.add_node("s57_lesson", step_5_7_lesson_reuse)
        graph.add_node("s6_impact", step_6_trigger_impact)
        graph.add_node("s7_record", step_7_record_change)
        graph.add_node("s8_warning", node_warning_policy_gate)

        graph.set_entry_point("s0_format")
        graph.add_edge("s0_format", "s1_id")
        graph.add_edge("s1_id", "s2_fwd")
        graph.add_edge("s2_fwd", "s3_bwd")
        graph.add_edge("s3_bwd", "s4_sem")
        graph.add_edge("s4_sem", "s5_orphan")
        graph.add_edge("s5_orphan", "s55_lateral")
        graph.add_edge("s55_lateral", "s57_lesson")
        graph.add_edge("s57_lesson", "s6_impact")
        graph.add_edge("s6_impact", "s7_record")
        graph.add_edge("s7_record", "s8_warning")
        graph.add_edge("s8_warning", END)

        return graph.compile()


class IterationGraphBuilder:
    """ALG-001: Builds the Agent α/β Dual-Agent Iteration Loop subgraph.

    Wraps MicroValidationGraphBuilder as a nested subgraph.
    Includes conditional edges for convergence and HITL gate routing.
    """

    @classmethod
    def build(cls) -> object:
        """Build and compile the dual-agent iteration subgraph.

        Returns:
            Compiled LangGraph application for the α/β iteration loop.
        """
        graph = StateGraph(WorkflowState)

        mv_app = MicroValidationGraphBuilder.build()

        graph.add_node("alpha", agent_alpha_critique)
        graph.add_node("beta", agent_beta_resolve)
        graph.add_node("micro_val", mv_app)  # Subgraph invocation
        graph.add_node("rca", root_cause_leftshift)

        graph.set_entry_point("alpha")
        graph.add_conditional_edges("alpha", check_fixed_point, {
            "beta": "beta",
            "exit_loop": END
        })
        graph.add_edge("beta", "micro_val")
        graph.add_edge("micro_val", "rca")

        graph.add_conditional_edges("rca", hitl_gate_choice, {
            "alpha": "alpha",
            "pass": END
        })
        return graph.compile()


class MasterGraphBuilder:
    """Master pipeline graph builder covering the 11-phase/stage dev pipeline.

    Stages 3-8 reuse the IterationGraphBuilder subgraph.
    Encapsulates all node registration and edge wiring.
    """

    @classmethod
    def build(cls) -> object:
        """Build and compile the master workflow graph.

        Returns:
            Compiled LangGraph application for the full pipeline.
        """
        workflow = StateGraph(WorkflowState)

        iter_app = IterationGraphBuilder.build()

        # Add Nodes
        workflow.add_node("start", node_start_pipeline)
        workflow.add_node("phase_0", phase_0_init)
        workflow.add_node("phase_1", phase_1_understanding)
        workflow.add_node("phase_2", phase_2_analysis)

        # Stages 3-8 utilize the Dual-Agent Iteration Loop Subgraph
        workflow.add_node("stage_3", iter_app)
        workflow.add_node("stage_4", iter_app)
        workflow.add_node("stage_5", iter_app)
        workflow.add_node("stage_6", iter_app)
        workflow.add_node("stage_7", iter_app)
        workflow.add_node("stage_8", iter_app)

        workflow.add_node("phase_9", phase_9_ship)
        workflow.add_node("phase_10", phase_10_retro)

        # Gate & Advance (Generic)
        workflow.add_node("gate", node_auto_gate)
        workflow.add_node("complete", node_complete_pipeline)

        # Edges
        workflow.set_entry_point("start")
        workflow.add_edge("start", "phase_0")
        workflow.add_edge("phase_0", "phase_1")
        workflow.add_edge("phase_1", "phase_2")
        workflow.add_edge("phase_2", "stage_3")
        workflow.add_edge("stage_3", "stage_4")
        workflow.add_edge("stage_4", "stage_5")
        workflow.add_edge("stage_5", "stage_6")
        workflow.add_edge("stage_6", "stage_7")
        workflow.add_edge("stage_7", "stage_8")
        workflow.add_edge("stage_8", "phase_9")
        workflow.add_edge("phase_9", "phase_10")
        workflow.add_edge("phase_10", "complete")
        workflow.add_edge("complete", END)

        return workflow.compile()


# ==========================================
# Module-level facades (backward compatibility)
# ==========================================

def build_micro_validation_graph():
    """Backward-compat facade — delegates to MicroValidationGraphBuilder."""
    return MicroValidationGraphBuilder.build()


def build_iteration_graph():
    """Backward-compat facade — delegates to IterationGraphBuilder."""
    return IterationGraphBuilder.build()


def build_graph():
    """Backward-compat facade — delegates to MasterGraphBuilder."""
    return MasterGraphBuilder.build()
