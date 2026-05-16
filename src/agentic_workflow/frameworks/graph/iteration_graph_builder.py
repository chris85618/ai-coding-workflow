"""Frameworks Layer — IterationGraphBuilder.

ALG-001: Builds the Agent α/β Dual-Agent Iteration Loop subgraph.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    try:
        from langgraph.graph import CompiledGraph  # type: ignore[attr-defined]
    except ImportError:
        from typing import Any as CompiledGraph

from langgraph.graph import END, StateGraph

from agentic_workflow.adapters.langgraph.state_mapper import WorkflowState
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


class IterationGraphBuilder:
    """ALG-001: Builds the Agent α/β Dual-Agent Iteration Loop subgraph.

    Wraps MicroValidationGraphBuilder as a nested subgraph.
    Includes conditional edges for convergence and HITL gate routing.
    """

    @classmethod
    def build(cls) -> CompiledGraph:
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
        graph.add_conditional_edges("alpha", check_fixed_point, {"beta": "beta", "exit_loop": END})
        graph.add_edge("beta", "micro_val")
        graph.add_edge("micro_val", "rca")

        graph.add_conditional_edges("rca", hitl_gate_choice, {"alpha": "alpha", "pass": END})
        return graph.compile()
