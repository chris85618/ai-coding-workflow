"""LangGraph Adapter — DAG Node Functions.

One function per DAG node. Each node reads from WorkflowState,
calls the appropriate use-case/domain service, and returns a
partial WorkflowState update for LangGraph's reducer.

Traceable to: FR-001, FR-012, FR-013, FR-019-v2, ADR-STR-002, ADR-STR-003
Each node is a pure function: (WorkflowState) -> WorkflowState (partial).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentic_workflow.adapters.langgraph.state_mapper import StateMapper, WorkflowState
from agentic_workflow.domain.models.enums import GateDecision, PipelineStatus, StageStatus
from agentic_workflow.domain.models.stage import MAX_ITERATIONS

if TYPE_CHECKING:
    pass


def node_start_pipeline(state: WorkflowState) -> WorkflowState:
    """DAG node: Initialize and start the pipeline.

    Transitions Pipeline from NOT_STARTED → RUNNING.
    Corresponds to UC-001 (start pipeline).

    Args:
        state: Current LangGraph workflow state.

    Returns:
        Partial state update with pipeline_status = "running".
    """
    pipeline = StateMapper.state_to_pipeline(state)
    if pipeline.status == PipelineStatus.NOT_STARTED:
        pipeline.start()
    return StateMapper.pipeline_to_state(pipeline)


def node_auto_gate(state: WorkflowState) -> WorkflowState:
    """DAG node: Evaluate auto-gate and record decision.

    Implements ADR-STR-003 (autonomous gate — no HITL).
    Currently always returns PASS; plug in quality metrics later.

    Args:
        state: Current LangGraph workflow state.

    Returns:
        Partial state update with last_gate_decision populated.
    """
    pipeline = StateMapper.state_to_pipeline(state)
    # Autonomous gate: determine pass/fail from state metadata
    gate_override = state.get("metadata", {}).get("gate_override")
    if gate_override == "pass_with_warnings":
        decision = GateDecision.PASS_WITH_WARNINGS
    else:
        decision = GateDecision.PASS
    pipeline.record_gate(decision)
    return StateMapper.pipeline_to_state(pipeline)


def node_advance_stage(state: WorkflowState) -> WorkflowState:
    """DAG node: Advance pipeline to the next stage.

    Requires last_gate_decision == PASS (INV-002-v2).

    Args:
        state: Current LangGraph workflow state.

    Returns:
        Partial state update with updated current_position.
    """
    pipeline = StateMapper.state_to_pipeline(state)
    pipeline.advance()
    return StateMapper.pipeline_to_state(pipeline)


def node_iterate_stage(state: WorkflowState) -> WorkflowState:
    """DAG node: Perform one α/β iteration on the current stage.

    Increments iteration_count and transitions stage to ITERATING.
    Implements FR-012 (autonomous α/β loop).

    Args:
        state: Current LangGraph workflow state.

    Returns:
        Partial state with incremented iteration_count and stage_status.
    """
    stage = StateMapper.state_to_stage(state)
    if stage is None:
        return WorkflowState(last_error="No active stage in state")
    if stage.status == StageStatus.PENDING:
        stage.transition(StageStatus.ITERATING)
    stage.increment_iteration()
    return StateMapper.stage_to_state(stage)


def node_complete_pipeline(state: WorkflowState) -> WorkflowState:
    """DAG node: Mark pipeline as completed.

    Args:
        state: Current LangGraph workflow state.

    Returns:
        Partial state with pipeline_status = "completed".
    """
    pipeline = StateMapper.state_to_pipeline(state)
    if pipeline.status == PipelineStatus.RUNNING:
        pipeline.complete()
    return StateMapper.pipeline_to_state(pipeline)


def should_continue_iterating(state: WorkflowState) -> str:
    """LangGraph conditional edge: decide whether to iterate or gate.

    Returns "iterate" if the current stage has not converged,
    "gate" if it has reached its fixed point.

    Args:
        state: Current LangGraph workflow state.

    Returns:
        Edge name: "iterate" | "gate"
    """
    stage = StateMapper.state_to_stage(state)
    if stage is None:
        return "gate"
    # Fixed-point reached if max_iterations hit or stage is passed
    if stage.status == StageStatus.PASSED:
        return "gate"
    if stage.iteration_count >= MAX_ITERATIONS:
        return "gate"
    return "iterate"
