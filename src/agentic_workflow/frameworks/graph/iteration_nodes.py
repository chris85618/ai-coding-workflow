"""Frameworks Layer — Iteration Loop Graph Node Functions.

Module-level functions wrapped inside helper class for LangGraph node registration.
"""

from __future__ import annotations

from agentic_workflow.domain.algorithms.convergence import ConvergenceDetector
from agentic_workflow.domain.algorithms.iter_loop import IterationLoop
from agentic_workflow.frameworks.langgraph.state_mapper import WorkflowState


class IterationNodes:
    """Class containing iteration loop node functions for LangGraph."""

    @staticmethod
    def agent_alpha_critique(state: WorkflowState) -> WorkflowState:
        """Agent Alpha: Critique and problem discovery."""
        from agentic_workflow.adapters.langgraph.nodes import node_agent_alpha_critique

        return node_agent_alpha_critique(state)

    @staticmethod
    def check_fixed_point(state: WorkflowState) -> str:
        """Route convergence outcome: continue (beta), align (exit_loop), or degrade (rollback)."""
        it, hist = state.get("iteration_count", 0), state.get("findings_history", [])
        curr = state.get("current_findings", [])
        res = ConvergenceDetector.check_convergence(iteration_count=it, findings_per_iter=hist, current_findings=curr)
        return ConvergenceDetector.route_fixed_point(res)

    @staticmethod
    def agent_beta_resolve(state: WorkflowState) -> WorkflowState:
        """Agent Beta: Resolution and integration."""
        from agentic_workflow.adapters.langgraph.nodes import node_agent_beta_resolve

        return node_agent_beta_resolve(state)

    @staticmethod
    def root_cause_leftshift(state: WorkflowState) -> WorkflowState:
        """Root Cause Analysis: Left-shift feedback loop."""
        from agentic_workflow.adapters.langgraph.nodes import node_root_cause_leftshift

        return node_root_cause_leftshift(state)

    @staticmethod
    def hitl_gate_choice(state: WorkflowState) -> str:
        """Human-in-the-loop decision routing using domain IterationLoop policy."""
        gate_decision = state.get("gate_decision", "pass")
        return IterationLoop.route_hitl_gate(gate_decision)

    @staticmethod
    def iterate_stage(state: WorkflowState) -> WorkflowState:
        """Perform stage iteration progression in the domain."""
        from agentic_workflow.adapters.langgraph.nodes import node_iterate_stage

        return node_iterate_stage(state)

    @staticmethod
    def align_stage(state: WorkflowState) -> WorkflowState:
        """Alignment check: diverge → converge → align closure (ADR-STR-029)."""
        from agentic_workflow.adapters.langgraph.nodes import node_align_check

        return node_align_check(state)

    @staticmethod
    def rollback_universal_base(state: WorkflowState) -> WorkflowState:
        """Degradation path: roll back to the universal base on DIVERGING."""
        from agentic_workflow.adapters.langgraph.nodes import node_rollback

        return node_rollback(state)


# Backward compatibility facades (delegated by __init__.py)
agent_alpha_critique = IterationNodes.agent_alpha_critique
check_fixed_point = IterationNodes.check_fixed_point
agent_beta_resolve = IterationNodes.agent_beta_resolve
root_cause_leftshift = IterationNodes.root_cause_leftshift
hitl_gate_choice = IterationNodes.hitl_gate_choice
iterate_stage = IterationNodes.iterate_stage
align_stage = IterationNodes.align_stage
rollback_universal_base = IterationNodes.rollback_universal_base
