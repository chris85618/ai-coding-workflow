"""Frameworks Layer — IterationGraphBuilder.

ALG-001: Builds the Agent α/β Dual-Agent Iteration Loop subgraph.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph

from langgraph.graph import END, StateGraph

from agentic_workflow.application.ports.gateways.graph_builder import IIterationGraphBuilder
from agentic_workflow.frameworks.graph.iteration_nodes import (
    agent_alpha_critique,
    agent_beta_resolve,
    check_fixed_point,
    hitl_gate_choice,
    root_cause_leftshift,
)
from agentic_workflow.frameworks.graph.micro_validation_graph_builder import (
    MicroValidationGraphBuilder,
)
from agentic_workflow.frameworks.langgraph.state_mapper import WorkflowState


class IterationGraphBuilder(IIterationGraphBuilder):
    """ALG-001: Builds the Agent α/β Dual-Agent Iteration Loop subgraph.

    Wraps MicroValidationGraphBuilder as a nested subgraph.
    Includes conditional edges for convergence and HITL gate routing.
    """

    @staticmethod
    def _setup_graph_nodes(graph: StateGraph[WorkflowState, Any, Any]) -> None:
        """Add nodes to iteration graph."""
        graph.add_node("alpha", agent_alpha_critique)
        graph.add_node("beta", agent_beta_resolve)
        graph.add_node("micro_val", MicroValidationGraphBuilder.build())
        graph.add_node("rca", root_cause_leftshift)

    @staticmethod
    def _setup_graph_edges(graph: StateGraph[WorkflowState, Any, Any]) -> None:
        """Add edges and conditional routing to iteration graph."""
        graph.set_entry_point("alpha")
        graph.add_conditional_edges("alpha", check_fixed_point, {"beta": "beta", "exit_loop": END})
        graph.add_edge("beta", "micro_val")
        graph.add_edge("micro_val", "rca")
        graph.add_conditional_edges("rca", hitl_gate_choice, {"alpha": "alpha", "pass": END})

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
