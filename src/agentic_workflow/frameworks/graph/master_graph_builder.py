"""Frameworks Layer — MasterGraphBuilder.

Master pipeline graph builder covering the 11-phase/stage dev pipeline.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph

from agentic_workflow.application.ports.gateways.graph_builder import IMasterGraphBuilder
from agentic_workflow.frameworks.graph.iteration_graph_builder import (
    IterationGraphBuilder,
)
from agentic_workflow.frameworks.graph.master_pipeline_nodes import (
    phase_0_init,
    phase_1_understanding,
    phase_2_analysis,
    phase_9_ship,
    phase_10_retro,
)
from agentic_workflow.frameworks.langgraph.nodes import (
    node_auto_gate,
    node_complete_pipeline,
    node_security_audit,
    node_sonarcloud_gate,
    node_start_pipeline,
)
from agentic_workflow.frameworks.langgraph.state_mapper import WorkflowState


class MasterGraphBuilder(IMasterGraphBuilder):
    """Master pipeline graph builder covering the 11-phase/stage dev pipeline.

    Stages 3-8 reuse the IterationGraphBuilder subgraph.
    Encapsulates all node registration and edge wiring.
    """

    @staticmethod
    def _setup_master_stages(wf: StateGraph[WorkflowState, Any, Any], iter_app: Any) -> None:
        """Add stages to master graph."""
        wf.add_node("stage_3", iter_app)
        wf.add_node("stage_4", iter_app)
        wf.add_node("stage_5", iter_app)
        wf.add_node("stage_6", iter_app)
        wf.add_node("stage_7", iter_app)
        wf.add_node("stage_8", iter_app)

    @staticmethod
    def _setup_master_final_nodes(wf: StateGraph[WorkflowState, Any, Any]) -> None:
        """Add final nodes to master graph."""
        wf.add_node("sonar_gate", node_sonarcloud_gate)
        wf.add_node("phase_9", phase_9_ship)
        wf.add_node("phase_10", phase_10_retro)
        wf.add_node("security_audit", node_security_audit)
        wf.add_node("gate", node_auto_gate)
        wf.add_node("complete", node_complete_pipeline)

    @classmethod
    def _setup_master_nodes(cls, wf: StateGraph[WorkflowState, Any, Any]) -> None:
        """Add nodes to master graph."""
        wf.add_node("start", node_start_pipeline)
        wf.add_node("phase_0", phase_0_init)
        wf.add_node("phase_1", phase_1_understanding)
        wf.add_node("phase_2", phase_2_analysis)
        cls._setup_master_stages(wf, IterationGraphBuilder.build())
        cls._setup_master_final_nodes(wf)

    @staticmethod
    def _setup_edges_stages(wf: StateGraph[WorkflowState, Any, Any]) -> None:
        """Add stage transition edges."""
        wf.add_edge("phase_2", "stage_3")
        wf.add_edge("stage_3", "stage_4")
        wf.add_edge("stage_4", "stage_5")
        wf.add_edge("stage_5", "stage_6")
        wf.add_edge("stage_6", "stage_7")
        wf.add_edge("stage_7", "stage_8")

    @staticmethod
    def _setup_edges_final(wf: StateGraph[WorkflowState, Any, Any]) -> None:
        """Add final node edges."""
        wf.add_edge("stage_8", "sonar_gate")
        wf.add_edge("sonar_gate", "security_audit")
        wf.add_edge("security_audit", "phase_9")
        wf.add_edge("phase_9", "phase_10")
        wf.add_edge("phase_10", "complete")
        wf.add_edge("complete", END)

    @classmethod
    def _setup_master_edges(cls, wf: StateGraph[WorkflowState, Any, Any]) -> None:
        """Add master edges."""
        wf.set_entry_point("start")
        wf.add_edge("start", "phase_0")
        wf.add_edge("phase_0", "phase_1")
        wf.add_edge("phase_1", "phase_2")
        cls._setup_edges_stages(wf)
        cls._setup_edges_final(wf)

    @classmethod
    def build(
        cls, checkpointer: BaseCheckpointSaver[Any] | None = None
    ) -> CompiledStateGraph[WorkflowState, Any, Any, Any]:
        """Build and compile the master workflow graph.

        Args:
            checkpointer: Optional LangGraph checkpointer for state persistence.

        Returns:
            Compiled LangGraph application for the full pipeline.
        """
        workflow = StateGraph(WorkflowState)
        cls._setup_master_nodes(workflow)
        cls._setup_master_edges(workflow)
        return workflow.compile(checkpointer=checkpointer)
