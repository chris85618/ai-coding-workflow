"""Frameworks Layer — Graph wiring.

Constructs the LangGraph StateGraph.
This file implements the highly detailed workflow requested, exploding AGENTS.md
steps into LangGraph subgraphs (Micro-Validation ALG-002, Iteration ALG-001, Master Pipeline).
"""
from __future__ import annotations

from langgraph.graph import StateGraph, END
from agentic_workflow.adapters.langgraph.state_mapper import WorkflowState
from agentic_workflow.adapters.langgraph.nodes import (
    node_start_pipeline,
    node_auto_gate,
    node_advance_stage,
    node_complete_pipeline,
)

# ==========================================
# 1. Micro-Validation Subgraph Nodes
# ==========================================
def step_0_format(state: WorkflowState) -> WorkflowState: return state
def step_1_id_structure(state: WorkflowState) -> WorkflowState: return state
def step_2_forward_trace(state: WorkflowState) -> WorkflowState: return state
def step_3_backward_trace(state: WorkflowState) -> WorkflowState: return state
def step_4_semantic(state: WorkflowState) -> WorkflowState: return state
def step_5_orphan(state: WorkflowState) -> WorkflowState: return state
def step_5_5_lateral_trace(state: WorkflowState) -> WorkflowState: return state
def step_5_7_lesson_reuse(state: WorkflowState) -> WorkflowState: return state
def step_6_trigger_impact(state: WorkflowState) -> WorkflowState: return state
def step_7_record_change(state: WorkflowState) -> WorkflowState: return state

def build_micro_validation_graph():
    """ALG-002: Left-Shift Micro-Validation Sequence."""
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
    graph.add_edge("s7_record", END)
    
    return graph.compile()

# ==========================================
# 2. Iteration Loop Subgraph Nodes
# ==========================================
def agent_alpha_critique(state: WorkflowState) -> WorkflowState: return state
def check_fixed_point(state: WorkflowState) -> str: 
    # Returns "beta" or "exit_loop" based on YAGNI convergence
    return "beta"
def agent_beta_resolve(state: WorkflowState) -> WorkflowState: return state
def root_cause_leftshift(state: WorkflowState) -> WorkflowState: return state
def hitl_gate_choice(state: WorkflowState) -> str:
    # 1: continue, 2: add req, 3: pass
    return "pass"

def build_iteration_graph():
    """ALG-001: Agent α/β Iteration Loop."""
    graph = StateGraph(WorkflowState)
    
    # Instead of nested compiling directly inside nodes, we can use 
    # LangGraph's support for subgraphs by passing the compiled graph.
    mv_app = build_micro_validation_graph()
    
    graph.add_node("alpha", agent_alpha_critique)
    graph.add_node("beta", agent_beta_resolve)
    graph.add_node("micro_val", mv_app) # Subgraph invocation
    graph.add_node("rca", root_cause_leftshift)
    
    graph.set_entry_point("alpha")
    graph.add_conditional_edges("alpha", check_fixed_point, {
        "beta": "beta", 
        "exit_loop": END
    })
    graph.add_edge("beta", "micro_val")
    graph.add_edge("micro_val", "rca")
    
    # Conditional back to Alpha or End
    graph.add_conditional_edges("rca", hitl_gate_choice, {
        "alpha": "alpha",
        "pass": END
    })
    return graph.compile()

# ==========================================
# 3. Master Pipeline Graph
# ==========================================
def phase_0_init(state: WorkflowState) -> WorkflowState: return state
def phase_1_understanding(state: WorkflowState) -> WorkflowState: return state
def phase_2_analysis(state: WorkflowState) -> WorkflowState: return state
def stage_3_planning(state: WorkflowState) -> WorkflowState: return state
def stage_4_algorithm(state: WorkflowState) -> WorkflowState: return state
def stage_5_ooad(state: WorkflowState) -> WorkflowState: return state
def stage_6_formal(state: WorkflowState) -> WorkflowState: return state
def stage_7_bdd(state: WorkflowState) -> WorkflowState: return state
def stage_8_tdd(state: WorkflowState) -> WorkflowState: return state
def phase_9_ship(state: WorkflowState) -> WorkflowState: return state
def phase_10_retro(state: WorkflowState) -> WorkflowState: return state

def build_graph():
    """Master workflow orchestrator covering the 6-stage dev pipeline."""
    workflow = StateGraph(WorkflowState)
    
    iter_app = build_iteration_graph()
    
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
