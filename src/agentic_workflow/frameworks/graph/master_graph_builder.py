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

        iter_app = IterationGraphBuilder.build()

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
        workflow.add_node("sonar_gate", node_sonarcloud_gate)

        workflow.add_node("phase_9", phase_9_ship)
        workflow.add_node("phase_10", phase_10_retro)
        workflow.add_node("security_audit", node_security_audit)

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
        workflow.add_edge("stage_8", "sonar_gate")
        workflow.add_edge("sonar_gate", "security_audit")
        workflow.add_edge("security_audit", "phase_9")
        workflow.add_edge("phase_9", "phase_10")
        workflow.add_edge("phase_10", "complete")
        workflow.add_edge("complete", END)

        return workflow.compile(checkpointer=checkpointer)
