"""Frameworks Layer — Graph wiring.

Constructs the LangGraph StateGraph.
This file implements the highly detailed workflow requested, exploding AGENTS.md
steps into LangGraph subgraphs (Micro-Validation ALG-002, Iteration ALG-001,
Master Pipeline).
OO Design: Three builder classes encapsulate all graph construction logic
(ALG-010 OO mandate).
Module-level functions retained as backward-compat facades.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    try:
        from langgraph.graph import CompiledGraph  # type: ignore[attr-defined]
    except ImportError:
        from typing import Any as CompiledGraph

from agentic_workflow.frameworks.graph.iteration_graph_builder import (
    IterationGraphBuilder,
)
from agentic_workflow.frameworks.graph.iteration_nodes import (
    agent_alpha_critique,
    agent_beta_resolve,
    check_fixed_point,
    hitl_gate_choice,
    root_cause_leftshift,
)
from agentic_workflow.frameworks.graph.master_graph_builder import MasterGraphBuilder
from agentic_workflow.frameworks.graph.master_pipeline_nodes import (
    phase_0_init,
    phase_1_understanding,
    phase_2_analysis,
    phase_9_ship,
    phase_10_retro,
    stage_3_planning,
    stage_4_algorithm,
    stage_5_ooad,
    stage_6_formal,
    stage_7_bdd,
    stage_8_tdd,
)
from agentic_workflow.frameworks.graph.micro_validation_graph_builder import (
    MicroValidationGraphBuilder,
)
from agentic_workflow.frameworks.graph.micro_validation_nodes import (
    step_0_format,
    step_1_id_structure,
    step_2_forward_trace,
    step_3_backward_trace,
    step_4_semantic,
    step_5_5_lateral_trace,
    step_5_7_lesson_reuse,
    step_5_orphan,
    step_6_trigger_impact,
    step_7_record_change,
)

__all__ = [
    "MicroValidationGraphBuilder",
    "IterationGraphBuilder",
    "MasterGraphBuilder",
    "build_micro_validation_graph",
    "build_iteration_graph",
    "build_graph",
    # Node functions (backward compat)
    "step_0_format",
    "step_1_id_structure",
    "step_2_forward_trace",
    "step_3_backward_trace",
    "step_4_semantic",
    "step_5_orphan",
    "step_5_5_lateral_trace",
    "step_5_7_lesson_reuse",
    "step_6_trigger_impact",
    "step_7_record_change",
    "agent_alpha_critique",
    "check_fixed_point",
    "agent_beta_resolve",
    "root_cause_leftshift",
    "hitl_gate_choice",
    "phase_0_init",
    "phase_1_understanding",
    "phase_2_analysis",
    "stage_3_planning",
    "stage_4_algorithm",
    "stage_5_ooad",
    "stage_6_formal",
    "stage_7_bdd",
    "stage_8_tdd",
    "phase_9_ship",
    "phase_10_retro",
]


# ==========================================
# Module-level facades (backward compatibility)
# ==========================================


def build_micro_validation_graph() -> CompiledGraph:
    """Backward-compat facade — delegates to MicroValidationGraphBuilder."""
    return MicroValidationGraphBuilder.build()


def build_iteration_graph() -> CompiledGraph:
    """Backward-compat facade — delegates to IterationGraphBuilder."""
    return IterationGraphBuilder.build()


def build_graph() -> CompiledGraph:
    """Backward-compat facade — delegates to MasterGraphBuilder."""
    return MasterGraphBuilder.build()
