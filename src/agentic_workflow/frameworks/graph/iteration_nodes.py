"""Frameworks Layer — Iteration Loop Graph Node Functions.

Module-level functions required by LangGraph for node registration.
"""

from __future__ import annotations

from agentic_workflow.domain.algorithms.convergence import ConvergenceDetector
from agentic_workflow.domain.algorithms.iter_loop import IterationLoop
from agentic_workflow.frameworks.langgraph.state_mapper import WorkflowState


def agent_alpha_critique(state: WorkflowState) -> WorkflowState:
    """Agent Alpha: Critique and problem discovery."""
    return state


def check_fixed_point(state: WorkflowState) -> str:
    """Checks for convergence or YAGNI termination using domain ConvergenceDetector."""
    it, hist = state.get("iteration_count", 0), state.get("findings_history", [])
    curr = state.get("current_findings", [])
    res = ConvergenceDetector.check_convergence(iteration_count=it, findings_per_iter=hist, current_findings=curr)
    return "exit_loop" if ConvergenceDetector.should_auto_pass(res) else "beta"


def agent_beta_resolve(state: WorkflowState) -> WorkflowState:
    """Agent Beta: Resolution and integration."""
    return state


def root_cause_leftshift(state: WorkflowState) -> WorkflowState:
    """Root Cause Analysis: Left-shift feedback loop."""
    return state


def hitl_gate_choice(state: WorkflowState) -> str:
    """Human-in-the-loop decision routing using domain IterationLoop policy."""
    gate_decision = state.get("gate_decision", "pass")
    return IterationLoop.route_hitl_gate(gate_decision)
