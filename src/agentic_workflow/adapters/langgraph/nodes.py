"""LangGraph Adapter — DAG Node Functions.

One function per DAG node. Each node reads from WorkflowState,
calls the appropriate use-case/domain service, and returns a
partial WorkflowState update for LangGraph's reducer.

Traceable to: FR-001, FR-012, FR-013, FR-019-v2, ADR-STR-002, ADR-STR-003
Each node is a pure function: (WorkflowState) -> WorkflowState (partial).
"""

from __future__ import annotations

from pathlib import Path

from agentic_workflow.adapters.langgraph.state_mapper import StateMapper, WorkflowState
from agentic_workflow.adapters.sonarcloud.sonar_adapter import SonarCloudAdapter
from agentic_workflow.domain.algorithms.impact_analysis import ImpactAnalysis
from agentic_workflow.domain.algorithms.micro_validation import MicroValidation
from agentic_workflow.domain.algorithms.pipeline_completeness import (
    PipelineCompletenessChecker,
)
from agentic_workflow.domain.algorithms.sonarcloud_gate import SonarCloudGate
from agentic_workflow.domain.entities.stage import MAX_ITERATIONS
from agentic_workflow.domain.enums import (
    GateDecision,
    PipelineStatus,
    StageStatus,
)
from agentic_workflow.domain.value_objects.sonarcloud_config import SonarCloudConfig
from agentic_workflow.frameworks.config import WorkflowConfigLoader
from agentic_workflow.frameworks.dependency_container import DependencyContainer

# Simulating a global container for the graph execution context
_CONTAINER: DependencyContainer | None = None


def set_container(container: DependencyContainer | None) -> None:
    """Initialize the global container for nodes."""
    global _CONTAINER
    _CONTAINER = container


def _get_container() -> DependencyContainer:
    if _CONTAINER is None:
        raise RuntimeError("DependencyContainer not initialized")
    return _CONTAINER


def node_start_pipeline(state: WorkflowState) -> WorkflowState:
    """DAG node: Initialize and start the pipeline.

    Transitions Pipeline from NOT_STARTED → RUNNING.
    Corresponds to UC-001 (start pipeline).
    """
    if state.get("pipeline_status") == "running":
        return state

    pipeline_id = state.get("pipeline_id", "default")
    try:
        container = _get_container()
        use_case = container.start_pipeline
        pipeline = use_case.execute(pipeline_id)
        return StateMapper.pipeline_to_state(pipeline)
    except Exception as e:
        state["last_error"] = str(e)
        return state


def node_pipeline_completeness(state: WorkflowState) -> WorkflowState:
    """DAG node: Fast scan for pipeline completeness.

    Corresponds to Phase 0 Pipeline Completeness Check (FR-001).
    """
    completeness_data = PipelineCompletenessChecker(Path()).calculate()

    # Store the results into state metadata
    metadata = state.get("metadata", {})
    metadata["completeness"] = completeness_data

    return {"metadata": metadata}


def node_auto_gate(state: WorkflowState) -> WorkflowState:
    """DAG node: Evaluate auto-gate and record decision.

    Implements ADR-STR-003 (autonomous gate — no HITL).
    """
    pipeline = StateMapper.state_to_pipeline(state)
    # Autonomous gate: determine pass/fail from state metadata
    gate_override = state.get("metadata", {}).get("gate_override")
    decision = GateDecision.PASS_WITH_WARNINGS if gate_override == "pass_with_warnings" else GateDecision.PASS
    pipeline.record_gate(decision)
    return StateMapper.pipeline_to_state(pipeline)


def node_advance_stage(state: WorkflowState) -> WorkflowState:
    """DAG node: Advance pipeline to next stage.

    Implements FR-001 (ordered phase progression).
    """
    pipeline_id = state.get("pipeline_id", "default")
    decision_str = str(state.get("last_gate_decision", "pass"))
    from agentic_workflow.domain.enums import GateDecision

    decision = GateDecision(decision_str)

    try:
        container = _get_container()
        use_case = container.advance_pipeline
        pipeline = use_case.execute(pipeline_id, decision)
        return StateMapper.pipeline_to_state(pipeline)
    except Exception as e:
        state["last_error"] = str(e)
        return state


def node_iterate_stage(state: WorkflowState) -> WorkflowState:
    """DAG node: Perform one α/β iteration on the current stage.

    Implements FR-012 (autonomous α/β loop).
    """
    pipeline_id = state.get("pipeline_id", "default")
    metadata = state.get("metadata", {})
    alpha_findings = metadata.get("recent_findings", [])

    try:
        container = _get_container()
        use_case = container.run_iteration
        pipeline = use_case.execute(pipeline_id, alpha_findings)
        return StateMapper.pipeline_to_state(pipeline)
    except Exception as e:
        state["last_error"] = str(e)
        return state


def node_complete_pipeline(state: WorkflowState) -> WorkflowState:
    """DAG node: Mark pipeline as completed.

    Args:
        state: Current LangGraph workflow state.

    Returns:
        Partial state with pipeline_status = "completed".
    """
    pipeline = StateMapper.state_to_pipeline(state)
    if pipeline.status != PipelineStatus.COMPLETED:
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
    Uses OrchestratorService to validate and prepare context.
    """
    pipeline = StateMapper.state_to_pipeline(state)
    metadata = state.get("metadata", {})

    container = _get_container()
    service = container.orchestrator

    # Semantic domain logic
    is_valid = service.validate_phase_execution(pipeline, 0)
    domain_context = service.prepare_stage_context(pipeline)

    metadata["orchestrator_is_valid"] = is_valid
    metadata["domain_context"] = domain_context

    return {"metadata": metadata}


def node_security_audit(state: WorkflowState) -> WorkflowState:
    """DAG node: Execute 3-layer security audit.

    Corresponds to FR-016.
    Uses SecurityAuditService to process findings and update the aggregate.
    """
    pipeline = StateMapper.state_to_pipeline(state)
    container = _get_container()
    service = container.security_audit

    # Mocking tool execution
    layer_results = [
        {"layer": "app_security", "findings": []},
        {"layer": "agent_security", "findings": []},
        {"layer": "supply_chain", "findings": []},
    ]

    findings = service.audit_pipeline(pipeline, layer_results)
    decision = service.decide_gate_impact(findings)

    # In a real DDD scenario, we might update the aggregate findings
    # for stage in pipeline.stages.values():
    #     if stage.status == StageStatus.RUNNING:
    #         pipeline.update_stage_findings(findings.items)

    return {
        "metadata": {"security_audit_findings": list(findings)},
        "last_gate_decision": decision,
    }


def node_sonarcloud_gate(state: WorkflowState) -> WorkflowState:
    """DAG node: Verify SonarCloud results and apply closed-loop feedback.

    Implements FR-015, FR-035, FR-036.
    Checks for required config, evaluates results, and converts failures to DEBT.
    """
    metadata = state.get("metadata", {})
    # 1. Verify Configuration (from centralized config system)
    wf_config = WorkflowConfigLoader.load()
    sonar_config_raw = wf_config.sonarcloud
    # Map frameworks config to domain config
    sonar_config = SonarCloudConfig(
        token=sonar_config_raw.token,
        project_key=sonar_config_raw.project_key,
        organization=sonar_config_raw.organization,
        auto_convert_to_debt=sonar_config_raw.feedback.auto_convert_to_debt,
        default_debt_priority=sonar_config_raw.feedback.default_debt_priority,
        on_missing_config=sonar_config_raw.on_missing_config,
    )
    config_check = SonarCloudGate.verify_configuration(sonar_config)

    if not config_check["valid"]:
        metadata["sonar_status"] = "disabled"
        metadata["sonar_warning"] = f"Missing SonarCloud parameters: {config_check['missing_vars']}"
        # ADR-OPS-001: 參數缺失時自動降級為 WARNING 並繼續
        return {
            "metadata": metadata,
            "last_gate_decision": GateDecision.PASS_WITH_WARNINGS,
        }

    # 2. Fetch Data if not already in metadata
    sonar_metrics = metadata.get("sonar_metrics")
    sonar_issues = metadata.get("sonar_issues")

    if sonar_metrics is None or sonar_issues is None:
        try:
            adapter = SonarCloudAdapter(sonar_config_raw)
            if sonar_metrics is None:
                sonar_metrics = adapter.get_metrics()
            if sonar_issues is None:
                sonar_issues = adapter.get_issues()
            metadata["sonar_metrics"] = sonar_metrics
            metadata["sonar_issues"] = sonar_issues
        except Exception as exc:
            metadata["sonar_status"] = "error"
            metadata["sonar_warning"] = f"SonarCloud API error: {exc}"
            return {
                "metadata": metadata,
                "last_gate_decision": GateDecision.PASS_WITH_WARNINGS,
            }

    # 3. Evaluate Results
    eval_result = SonarCloudGate.evaluate(sonar_metrics, sonar_issues)

    # 4. Closed Loop: Feed back tech debts to state/docs
    if not eval_result["passed"]:
        # Record tech debts for systematic improvement
        debts = eval_result["tech_debts"]
        metadata["pending_sonar_debts"] = debts
        metadata["sonar_failures"] = eval_result["failures"]
        metadata["sonar_status"] = "failed"

        return {
            "metadata": metadata,
            "last_gate_decision": GateDecision.FAIL,
            "last_error": f"SonarCloud Quality Gate Failed: {eval_result['failures']}",
        }

    metadata["sonar_status"] = "passed"
    return {"metadata": metadata, "last_gate_decision": GateDecision.PASS}
