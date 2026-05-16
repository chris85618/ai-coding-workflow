"""Adapter Layer — StateMapper for LangGraph ↔ Domain Model bridge.

Maps between LangGraph WorkflowState (TypedDict) and domain objects.
Traceable to: FR-019-v2, FR-021-v2, UC-001, UC-010, ADR-STR-002
"""

from __future__ import annotations

from agentic_workflow.adapters.langgraph.state_mapper.workflow_state import WorkflowState
from agentic_workflow.domain.models.enums import GateDecision, PipelineStatus, StageStatus
from agentic_workflow.domain.models.pipeline import Pipeline
from agentic_workflow.domain.models.stage import Stage


class StateMapper:
    """Bidirectional mapper: WorkflowState <-> Domain objects.

    Stateless utility class — all methods are static.
    Traceable to: ADR-STR-002 (Clean Architecture for LangGraph).
    """

    @staticmethod
    def pipeline_to_state(pipeline: Pipeline) -> WorkflowState:
        """Convert a Pipeline domain object to a LangGraph state dict.

        Args:
            pipeline: Domain pipeline aggregate root.

        Returns:
            Partial WorkflowState with pipeline fields populated.
        """
        gate = pipeline.last_gate_decision
        return WorkflowState(
            pipeline_id=pipeline.pipeline_id,
            pipeline_status=pipeline.status.value,
            current_position=pipeline.current_position,
            last_gate_decision=gate.value if gate is not None else None,
        )

    @staticmethod
    def state_to_pipeline(state: WorkflowState) -> Pipeline:
        """Reconstruct a Pipeline domain object from LangGraph state.

        Args:
            state: LangGraph state dictionary.

        Returns:
            Pipeline domain object reflecting the stored state.
        """
        gate_str = state.get("last_gate_decision")
        gate = GateDecision(gate_str) if gate_str else None
        pipeline = Pipeline(
            pipeline_id=state["pipeline_id"],
            current_position=state.get("current_position", "phase0"),
            status=PipelineStatus(state.get("pipeline_status", "not_started")),
            last_gate_decision=gate,
        )
        return pipeline

    @staticmethod
    def stage_to_state(stage: Stage) -> WorkflowState:
        """Convert a Stage domain object to a partial LangGraph state.

        Args:
            stage: Domain stage object.

        Returns:
            Partial WorkflowState with stage fields populated.
        """
        return WorkflowState(
            current_stage_id=stage.stage_id,
            stage_status=stage.status.value,
            iteration_count=stage.iteration_count,
        )

    @staticmethod
    def state_to_stage(state: WorkflowState) -> Stage | None:
        """Reconstruct a Stage from LangGraph state.

        Args:
            state: LangGraph state dictionary.

        Returns:
            Stage domain object, or None if no stage info in state.
        """
        stage_id = state.get("current_stage_id")
        if not stage_id:
            return None
        status_str = str(state.get("stage_status") or "pending")
        return Stage(
            stage_id=stage_id,
            name=state.get("metadata", {}).get("stage_name", stage_id),
            status=StageStatus(status_str),
            iteration_count=state.get("iteration_count", 0),
        )
