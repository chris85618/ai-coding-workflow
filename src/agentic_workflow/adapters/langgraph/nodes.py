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
from agentic_workflow.domain.algorithms.pipeline_completeness import calculate_completeness
from agentic_workflow.domain.algorithms.micro_validation import MicroValidation
from agentic_workflow.domain.algorithms.root_cause_leftshift import RootCauseLeftShift
from agentic_workflow.domain.algorithms.impact_analysis import ImpactAnalysis
from agentic_workflow.domain.algorithms.tech_debt_manager import TechDebtManager
from agentic_workflow.domain.algorithms.risk_manager import RiskManager
from agentic_workflow.domain.algorithms.adr_governance import ADRGovernance
from agentic_workflow.domain.algorithms.orchestrator import Orchestrator
from pathlib import Path

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


def node_pipeline_completeness(state: WorkflowState) -> WorkflowState:
    """DAG node: Fast scan for pipeline completeness.

    Corresponds to Phase 0 Pipeline Completeness Check (FR-001).

    Args:
        state: Current LangGraph workflow state.

    Returns:
        Partial state update with completeness metadata.
    """
    completeness_data = calculate_completeness(Path("."))
    
    # Store the results into state metadata
    metadata = state.get("metadata", {})
    metadata["completeness"] = completeness_data
    
    return {"metadata": metadata}


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


def node_micro_validation(state: WorkflowState) -> WorkflowState:
    """DAG node: Execute micro-validation on recent changes.
    
    Corresponds to FR-005, FR-006, FR-007.
    """
    metadata = state.get("metadata", {})
    changes_content = metadata.get("recent_changes_content", "")
    changed_ids = metadata.get("recent_changed_ids", [])
    
    result = MicroValidation.run_all(changes_content, changed_ids)
    metadata["micro_validation_result"] = result
    
    return {"metadata": metadata}


def node_impact_analysis(state: WorkflowState) -> WorkflowState:
    """DAG node: Execute impact analysis for modifications.
    
    Corresponds to FR-008, FR-009, FR-022.
    """
    metadata = state.get("metadata", {})
    changed_ids = metadata.get("recent_changed_ids", [])
    
    impact_results = {}
    for mod_id in changed_ids:
        # Mocking nodes traversal
        impact_results[mod_id] = ImpactAnalysis.calculate_blast_radius(mod_id, [])
        
    metadata["impact_analysis_results"] = impact_results
    return {"metadata": metadata}


def node_orchestrator(state: WorkflowState) -> WorkflowState:
    """DAG node: Master orchestrator entrypoint for phases and stages.
    
    Corresponds to FR-002, FR-017, FR-018.
    """
    pipeline = StateMapper.state_to_pipeline(state)
    metadata = state.get("metadata", {})
    
    # Delegate to Orchestrator based on current state
    if pipeline.status == PipelineStatus.NOT_STARTED:
        result = Orchestrator.execute_phase(0, metadata)
    else:
        pos = pipeline.current_position
        stage = pos.get("stage", 0) if isinstance(pos, dict) else 0
        result = Orchestrator.execute_stage(stage, metadata)
        
    metadata["orchestrator_result"] = result
    return {"metadata": metadata}

