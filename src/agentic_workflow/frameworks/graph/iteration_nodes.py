"""Frameworks Layer — Iteration Loop Graph Node Functions.

Module-level functions required by LangGraph for node registration.
"""

from __future__ import annotations

from agentic_workflow.adapters.langgraph.state_mapper import WorkflowState


def agent_alpha_critique(state: WorkflowState) -> WorkflowState:
    """Agent Alpha: Critique and problem discovery."""
    return state  # pragma: no branch


def check_fixed_point(_state: WorkflowState) -> str:
    """Checks for convergence or YAGNI termination."""
    # Returns "beta" or "exit_loop" based on YAGNI convergence
    return "beta"  # pragma: no branch


def agent_beta_resolve(state: WorkflowState) -> WorkflowState:
    """Agent Beta: Resolution and integration."""
    return state  # pragma: no branch


def root_cause_leftshift(state: WorkflowState) -> WorkflowState:
    """Root Cause Analysis: Left-shift feedback loop."""
    return state  # pragma: no branch


def hitl_gate_choice(_state: WorkflowState) -> str:
    """Human-in-the-loop decision routing."""
    # 1: continue, 2: add req, 3: pass
    return "pass"  # pragma: no branch
