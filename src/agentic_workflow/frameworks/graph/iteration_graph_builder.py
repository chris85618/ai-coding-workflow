"""Frameworks Layer — IterationGraphBuilder.

ALG-001: Builds the Agent α/β Dual-Agent Iteration Loop subgraph.
"""

from __future__ import annotations

from collections.abc import Hashable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph

from langgraph.graph import END, StateGraph

from agentic_workflow.application.ports.gateways.graph_builder import IIterationGraphBuilder
from agentic_workflow.frameworks.graph.iteration_nodes import (
    agent_alpha_critique,
    agent_beta_resolve,
    align_stage,
    check_fixed_point,
    hitl_gate_choice,
    iterate_stage,
    rollback_universal_base,
    root_cause_leftshift,
)
from agentic_workflow.frameworks.graph.micro_validation_graph_builder import (
    MicroValidationGraphBuilder,
)
from agentic_workflow.frameworks.langgraph.state_mapper import WorkflowState

# Variable binding for constant access (TC-QUALITY-014).
_end = END


class IterationGraphBuilder(IIterationGraphBuilder):
    """ALG-001: Builds the Agent α/β Dual-Agent Iteration Loop subgraph.

    Wraps MicroValidationGraphBuilder as a nested subgraph.
    Includes conditional edges for convergence and HITL gate routing.
    """

    @staticmethod
    def _setup_loop_nodes(graph: StateGraph[WorkflowState, Any, Any]) -> None:
        """Add the core dual-agent loop nodes."""
        graph.add_node("alpha", agent_alpha_critique)
        graph.add_node("beta", agent_beta_resolve)
        graph.add_node("iterate", iterate_stage)
        graph.add_node("micro_val", MicroValidationGraphBuilder.build())
        graph.add_node("rca", root_cause_leftshift)

    @staticmethod
    def _setup_closure_nodes(graph: StateGraph[WorkflowState, Any, Any]) -> None:
        """Add the align and rollback closure nodes (ADR-STR-029)."""
        graph.add_node("align", align_stage)
        graph.add_node("rollback", rollback_universal_base)

    @classmethod
    def _setup_graph_nodes(cls, graph: StateGraph[WorkflowState, Any, Any]) -> None:
        """Add nodes to iteration graph."""
        cls._setup_loop_nodes(graph)
        cls._setup_closure_nodes(graph)

    @staticmethod
    def _setup_loop_edges(graph: StateGraph[WorkflowState, Any, Any]) -> None:
        """Add the diverge → converge loop edges."""
        routes: dict[Hashable, str] = {"beta": "beta", "exit_loop": "align", "rollback": "rollback"}
        graph.set_entry_point("alpha")
        graph.add_conditional_edges("alpha", check_fixed_point, routes)
        graph.add_edge("beta", "iterate")
        graph.add_edge("iterate", "micro_val")
        graph.add_edge("micro_val", "rca")

    @staticmethod
    def _setup_closure_edges(graph: StateGraph[WorkflowState, Any, Any]) -> None:
        """Add the align feedback and rollback degradation edges (ADR-STR-029)."""
        graph.add_conditional_edges("rca", hitl_gate_choice, {"alpha": "alpha", "pass": "align"})
        graph.add_conditional_edges("align", hitl_gate_choice, {"alpha": "alpha", "pass": _end})
        graph.add_edge("rollback", _end)

    @classmethod
    def _setup_graph_edges(cls, graph: StateGraph[WorkflowState, Any, Any]) -> None:
        """Add edges and conditional routing (diverge → converge → align, ADR-STR-029)."""
        cls._setup_loop_edges(graph)
        cls._setup_closure_edges(graph)

    @classmethod
    def build(cls) -> CompiledStateGraph[WorkflowState, Any, Any, Any]:
        """Build and compile the dual-agent iteration subgraph.

        Returns:
            Compiled LangGraph application for the α/β iteration loop.
        """
        graph = StateGraph(WorkflowState)
        cls._setup_graph_nodes(graph)
        cls._setup_graph_edges(graph)
        return graph.compile()
