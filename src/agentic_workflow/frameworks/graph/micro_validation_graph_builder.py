"""Frameworks Layer — MicroValidationGraphBuilder.

ALG-002: Builds the Left-Shift Micro-Validation Sequence subgraph.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph

from langgraph.graph import END, StateGraph

from agentic_workflow.application.ports.gateways.graph_builder import IMicroValidationGraphBuilder
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
from agentic_workflow.frameworks.langgraph.state_mapper import WorkflowState


def _setup_mv_nodes_rest(graph: StateGraph[WorkflowState, Any, Any]) -> None:
    graph.add_node("s4_sem", step_4_semantic)
    graph.add_node("s5_orphan", step_5_orphan)
    graph.add_node("s55_lateral", step_5_5_lateral_trace)
    graph.add_node("s57_lesson", step_5_7_lesson_reuse)
    graph.add_node("s6_impact", step_6_trigger_impact)
    graph.add_node("s7_record", step_7_record_change)


def _setup_mv_nodes(graph: StateGraph[WorkflowState, Any, Any]) -> None:
    graph.add_node("s0_format", step_0_format)
    graph.add_node("s1_id", step_1_id_structure)
    graph.add_node("s2_fwd", step_2_forward_trace)
    graph.add_node("s3_bwd", step_3_backward_trace)
    _setup_mv_nodes_rest(graph)


def _setup_mv_edges_final(graph: StateGraph[WorkflowState, Any, Any]) -> None:
    graph.add_edge("s57_lesson", "s6_impact")
    graph.add_edge("s6_impact", "s7_record")
    graph.add_edge("s7_record", END)


def _setup_mv_edges_rest(graph: StateGraph[WorkflowState, Any, Any]) -> None:
    graph.add_edge("s3_bwd", "s4_sem")
    graph.add_edge("s4_sem", "s5_orphan")
    graph.add_edge("s5_orphan", "s55_lateral")
    graph.add_edge("s55_lateral", "s57_lesson")
    _setup_mv_edges_final(graph)


def _setup_mv_edges(graph: StateGraph[WorkflowState, Any, Any]) -> None:
    graph.set_entry_point("s0_format")
    graph.add_edge("s0_format", "s1_id")
    graph.add_edge("s1_id", "s2_fwd")
    graph.add_edge("s2_fwd", "s3_bwd")
    _setup_mv_edges_rest(graph)


class MicroValidationGraphBuilder(IMicroValidationGraphBuilder):
    """ALG-002: Builds the Left-Shift Micro-Validation Sequence subgraph.

    Encapsulates the 10-step micro-validation chain (Steps 0-7 + 5.5/5.7)
    as a compilable LangGraph StateGraph.
    """

    @classmethod
    def build(cls) -> CompiledStateGraph[WorkflowState, Any, Any, Any]:
        """Build and compile the micro-validation subgraph.

        Returns:
            Compiled LangGraph application for micro-validation.
        """
        graph = StateGraph(WorkflowState)
        _setup_mv_nodes(graph)
        _setup_mv_edges(graph)
        return graph.compile()
