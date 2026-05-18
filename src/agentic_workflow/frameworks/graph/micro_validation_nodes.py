"""Frameworks Layer — Micro-Validation Graph Node Functions.

Module-level functions wrapped inside a helper class for LangGraph node registration.
"""

from __future__ import annotations

from agentic_workflow.frameworks.langgraph.state_mapper import WorkflowState


class MicroValidationNodes:
    """Class containing micro-validation node functions for LangGraph."""

    @staticmethod
    def step_0_format(state: WorkflowState) -> WorkflowState:
        """Format check node."""
        from agentic_workflow.adapters.langgraph.nodes import node_step_0_format

        return node_step_0_format(state)

    @staticmethod
    def step_1_id_structure(state: WorkflowState) -> WorkflowState:
        """ID structure check node."""
        from agentic_workflow.adapters.langgraph.nodes import node_step_1_id_structure

        return node_step_1_id_structure(state)

    @staticmethod
    def step_2_forward_trace(state: WorkflowState) -> WorkflowState:
        """Forward traceability check node."""
        from agentic_workflow.adapters.langgraph.nodes import node_step_2_forward_trace

        return node_step_2_forward_trace(state)

    @staticmethod
    def step_3_backward_trace(state: WorkflowState) -> WorkflowState:
        """Backward traceability check node."""
        from agentic_workflow.adapters.langgraph.nodes import node_step_3_backward_trace

        return node_step_3_backward_trace(state)

    @staticmethod
    def step_4_semantic(state: WorkflowState) -> WorkflowState:
        """Semantic consistency check node."""
        from agentic_workflow.adapters.langgraph.nodes import node_step_4_semantic

        return node_step_4_semantic(state)

    @staticmethod
    def step_5_orphan(state: WorkflowState) -> WorkflowState:
        """Orphan node detection node."""
        return state

    @staticmethod
    def step_5_5_lateral_trace(state: WorkflowState) -> WorkflowState:
        """Lateral traceability check node."""
        return state

    @staticmethod
    def step_5_7_lesson_reuse(state: WorkflowState) -> WorkflowState:
        """Lesson reuse check node."""
        from agentic_workflow.adapters.langgraph.nodes import node_step_5_7_lesson_reuse

        return node_step_5_7_lesson_reuse(state)

    @staticmethod
    def step_6_trigger_impact(state: WorkflowState) -> WorkflowState:
        """Impact analysis trigger node."""
        from agentic_workflow.adapters.langgraph.nodes import node_step_6_trigger_impact

        return node_step_6_trigger_impact(state)

    @staticmethod
    def step_7_record_change(state: WorkflowState) -> WorkflowState:
        """Change record node."""
        from agentic_workflow.adapters.langgraph.nodes import node_step_7_record_change

        return node_step_7_record_change(state)


# Backward compatibility facades (delegated by __init__.py)
step_0_format = MicroValidationNodes.step_0_format
step_1_id_structure = MicroValidationNodes.step_1_id_structure
step_2_forward_trace = MicroValidationNodes.step_2_forward_trace
step_3_backward_trace = MicroValidationNodes.step_3_backward_trace
step_4_semantic = MicroValidationNodes.step_4_semantic
step_5_orphan = MicroValidationNodes.step_5_orphan
step_5_5_lateral_trace = MicroValidationNodes.step_5_5_lateral_trace
step_5_7_lesson_reuse = MicroValidationNodes.step_5_7_lesson_reuse
step_6_trigger_impact = MicroValidationNodes.step_6_trigger_impact
step_7_record_change = MicroValidationNodes.step_7_record_change
