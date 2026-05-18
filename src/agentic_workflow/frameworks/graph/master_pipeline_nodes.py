"""Frameworks Layer — Master Pipeline Graph Node Functions.

Module-level functions wrapped inside a helper class for LangGraph node registration.
"""

from __future__ import annotations

from agentic_workflow.frameworks.langgraph.state_mapper import WorkflowState


class MasterPipelineNodes:
    """Class containing master pipeline node functions for LangGraph."""

    @staticmethod
    def phase_0_init(state: WorkflowState) -> WorkflowState:
        """Phase 0: Environment and State initialization."""
        from agentic_workflow.adapters.langgraph.nodes import node_phase_0_init
        return node_phase_0_init(state)

    @staticmethod
    def phase_1_understanding(state: WorkflowState) -> WorkflowState:
        """Phase 1: Codebase comprehension and Knowledge Graph."""
        from agentic_workflow.adapters.langgraph.nodes import node_phase_1_understanding
        return node_phase_1_understanding(state)

    @staticmethod
    def phase_2_analysis(state: WorkflowState) -> WorkflowState:
        """Phase 2: Project Analysis and FEA generation."""
        from agentic_workflow.adapters.langgraph.nodes import node_phase_2_analysis
        return node_phase_2_analysis(state)

    @staticmethod
    def stage_3_planning(state: WorkflowState) -> WorkflowState:
        """Stage 3: Technical Planning and Requirements."""
        state["current_position"] = "stage3"
        return state

    @staticmethod
    def stage_4_algorithm(state: WorkflowState) -> WorkflowState:
        """Stage 4: Algorithm Design and Complexity."""
        state["current_position"] = "stage4"
        return state

    @staticmethod
    def stage_5_ooad(state: WorkflowState) -> WorkflowState:
        """Stage 5: Object-Oriented Analysis and Design."""
        state["current_position"] = "stage5"
        return state

    @staticmethod
    def stage_6_formal(state: WorkflowState) -> WorkflowState:
        """Stage 6: Formal Verification and Invariants."""
        from agentic_workflow.adapters.langgraph.nodes import node_stage_6_formal
        return node_stage_6_formal(state)

    @staticmethod
    def stage_7_bdd(state: WorkflowState) -> WorkflowState:
        """Stage 7: Behavior-Driven Development and Scenarios."""
        state["current_position"] = "stage7"
        return state

    @staticmethod
    def stage_8_tdd(state: WorkflowState) -> WorkflowState:
        """Stage 8: Test-Driven Development and Implementation."""
        state["current_position"] = "stage8"
        return state

    @staticmethod
    def phase_9_ship(state: WorkflowState) -> WorkflowState:
        """Phase 9: Deployment and Shipping."""
        from agentic_workflow.adapters.langgraph.nodes import node_phase_9_ship
        return node_phase_9_ship(state)

    @staticmethod
    def phase_10_retro(state: WorkflowState) -> WorkflowState:
        """Phase 10: Retrospective and Learning Extraction."""
        from agentic_workflow.adapters.langgraph.nodes import node_phase_10_retro
        return node_phase_10_retro(state)


# Backward compatibility facades (delegated by __init__.py)
phase_0_init = MasterPipelineNodes.phase_0_init
phase_1_understanding = MasterPipelineNodes.phase_1_understanding
phase_2_analysis = MasterPipelineNodes.phase_2_analysis
stage_3_planning = MasterPipelineNodes.stage_3_planning
stage_4_algorithm = MasterPipelineNodes.stage_4_algorithm
stage_5_ooad = MasterPipelineNodes.stage_5_ooad
stage_6_formal = MasterPipelineNodes.stage_6_formal
stage_7_bdd = MasterPipelineNodes.stage_7_bdd
stage_8_tdd = MasterPipelineNodes.stage_8_tdd
phase_9_ship = MasterPipelineNodes.phase_9_ship
phase_10_retro = MasterPipelineNodes.phase_10_retro
