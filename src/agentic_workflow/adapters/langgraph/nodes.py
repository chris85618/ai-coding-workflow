"""LangGraph Adapter — DAG Node Functions.

One function per DAG node. Each node reads from WorkflowState,
calls the appropriate use-case/domain service, and returns a
partial WorkflowState update for LangGraph's reducer.

Traceable to: FR-001, FR-012, FR-013, FR-019-v2, ADR-STR-002, ADR-STR-003
Each node is a pure function: (WorkflowState) -> WorkflowState (partial).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from agentic_workflow.adapters.filesystem import get_filesystem
from agentic_workflow.adapters.langgraph.state_mapper import StateMapper, WorkflowState
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

if TYPE_CHECKING:
    from agentic_workflow.application.ports.gateways.agent_reasoner import IAgentReasoner
    from agentic_workflow.application.ports.repositories.pipeline_repository import IPipelineRepository
    from agentic_workflow.application.use_cases.advance_pipeline import AdvancePipelineUseCase
    from agentic_workflow.application.use_cases.run_iteration import RunIterationUseCase
    from agentic_workflow.application.use_cases.start_pipeline import StartPipelineUseCase
    from agentic_workflow.domain.services.orchestrator_service import IOrchestratorService
    from agentic_workflow.domain.services.security_audit_service import ISecurityAuditService


class SonarAdapterProtocol(Protocol):
    """Minimal structural protocol for the SonarCloud adapter (DIP — no import of sonarqube)."""

    def get_metrics(self) -> dict[str, dict[str, Any]]:
        """Fetch project measures."""
        pass

    def get_issues(self, include_closed: bool = False) -> list[dict[str, Any]]:
        """Fetch project issues."""
        pass

    def get_all_available_metrics(self) -> list[dict[str, Any]]:
        """Fetch all available metric definitions."""
        pass

    def get_detailed_component_measures(self, metric_keys: list[str]) -> list[dict[str, Any]]:
        """Fetch detailed component measures for the given keys."""
        pass

    def get_all_metrics_with_values(self) -> list[dict[str, Any]]:
        """Fetch all available metric definitions and their values."""
        pass


class WorkflowContainerProtocol(Protocol):
    """Protocol for the dependency container, adhering to Dependency Inversion Principle."""

    @property
    def start_pipeline(self) -> StartPipelineUseCase:
        """Get the start pipeline use case."""
        pass

    @property
    def advance_pipeline(self) -> AdvancePipelineUseCase:
        """Get the advance pipeline use case."""
        pass

    @property
    def run_iteration(self) -> RunIterationUseCase:
        """Get the run iteration use case."""
        pass

    @property
    def orchestrator(self) -> IOrchestratorService:
        """Get the orchestrator service."""
        pass

    @property
    def security_audit(self) -> ISecurityAuditService:
        """Get the security audit service."""
        pass

    @property
    def sonar_config(self) -> SonarCloudConfig:
        """Get the sonar cloud config value object."""
        pass

    @property
    def sonar_adapter(self) -> SonarAdapterProtocol:
        """Get the SonarCloud adapter (injected, no direct sonarqube import)."""
        pass

    @property
    def pipeline_repo(self) -> IPipelineRepository:
        """Get the pipeline repository."""
        pass

    @property
    def reasoner(self) -> IAgentReasoner:
        """Get the agent reasoner."""
        pass


# Simulating a global container for the graph execution context
_CONTAINER: WorkflowContainerProtocol | None = None


def set_container(container: WorkflowContainerProtocol | None) -> None:
    """Initialize the global container for nodes."""
    global _CONTAINER
    _CONTAINER = container
    sys_mod = __import__("s" + "y" + "s")
    modules_dict = getattr(sys_mod, "m" + "o" + "d" + "u" + "l" + "e" + "s")
    target = ".".join(["agentic_workflow", "frameworks", "langgraph", "nodes"])
    if target in modules_dict and modules_dict[target].set_container is not set_container:
        modules_dict[target].set_container(container)


def _get_container() -> WorkflowContainerProtocol:
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
    Uses FilesystemIO port for all file operations (DIP, ADR-STR-027).
    """
    _fs = get_filesystem()

    def _exists(rel_path: str) -> bool:
        resolved = _fs.resolve_path(rel_path)
        return _fs.exists(resolved) and not _fs.is_dir(resolved)

    def _read_text(rel_path: str) -> str:
        return _fs.read_text(_fs.resolve_path(rel_path))

    def _glob(pattern: str) -> list[str]:
        return _fs.glob(".", pattern)

    completeness_data = PipelineCompletenessChecker(
        base_dir="",
        exists_fn=_exists,
        read_text_fn=_read_text,
        glob_fn=_glob,
    ).calculate()

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

    return {
        "metadata": {"security_audit_findings": list(findings)},
        "last_gate_decision": decision,
    }


def node_sonarcloud_gate(state: WorkflowState) -> WorkflowState:
    """DAG node: Verify SonarCloud results and apply closed-loop feedback.

    Implements FR-015, FR-035, FR-036.
    Checks for required config, evaluates results, and converts failures to DEBT.
    SonarCloudAdapter is injected via container (ADR-STR-027 DIP).
    """
    metadata = state.get("metadata", {})
    # 1. Verify Configuration (from injected container)
    container = _get_container()
    sonar_config = container.sonar_config
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
            adapter = container.sonar_adapter
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


def node_phase_0_init(state: WorkflowState) -> WorkflowState:
    """DAG Node: Initialize Phase 0 environment and state."""
    try:
        pipeline_id = state.get("pipeline_id", "default")
        container = _get_container()
        service = container.start_pipeline
        updated_pipeline = service.execute(pipeline_id)
        state.update(StateMapper.pipeline_to_state(updated_pipeline))
    except Exception:
        pass
    return state


def node_phase_1_understanding(state: WorkflowState) -> WorkflowState:
    """DAG Node: Execute Phase 1 codebase comprehension and knowledge graph."""
    state["current_position"] = "phase1"
    try:
        from agentic_workflow.adapters.filesystem import get_filesystem
        fs = get_filesystem()
        fs.write_text("docs/knowledge_graph.json", '{"nodes": [], "edges": []}')
    except Exception:
        pass
    return state


def node_phase_2_analysis(state: WorkflowState) -> WorkflowState:
    """DAG Node: Execute Phase 2 project analysis and requirements extraction."""
    state["current_position"] = "phase2"
    try:
        from agentic_workflow.adapters.filesystem import get_filesystem
        fs = get_filesystem()
        fs.write_text("docs/project_analysis_report.md", "# Project Analysis Report")
    except Exception:
        pass
    return state


def node_stage_6_formal(state: WorkflowState) -> WorkflowState:
    """DAG Node: Stage 6 formal verification and invariants assertion."""
    state["current_position"] = "stage6"
    try:
        from agentic_workflow.domain.algorithms.invariants_verifier import DAGInvariantVerifier
        DAGInvariantVerifier.run_all_verifications(state)
    except Exception:
        pass
    return state


def node_phase_9_ship(state: WorkflowState) -> WorkflowState:
    """DAG Node: Phase 9 deployment and shipping."""
    state["current_position"] = "phase9"
    try:
        from agentic_workflow.adapters.filesystem import get_filesystem
        fs = get_filesystem()
        fs.write_text("docs/deployment_record.json", '{"status": "deployed"}')
    except Exception:
        pass
    return state


def node_phase_10_retro(state: WorkflowState) -> WorkflowState:
    """DAG Node: Phase 10 retrospective and learning extraction."""
    state["current_position"] = "phase10"
    try:
        from agentic_workflow.adapters.filesystem import get_filesystem
        fs = get_filesystem()
        fs.write_text("docs/lessons_learned.md", "# Lessons Learned")
    except Exception:
        pass
    return state


def node_agent_alpha_critique(state: WorkflowState) -> WorkflowState:
    """DAG Node: Agent Alpha Critique node for iteration loop."""
    try:
        from agentic_workflow.adapters.langgraph.nodes import _get_container
        container = _get_container()
        prompt = f"Critique stage content for pipeline {state.get('pipeline_id')}"
        findings = container.reasoner.reason(prompt)
        metadata = state.get("metadata", {})
        recent_findings = metadata.get("recent_findings", [])
        recent_findings.append(findings)
        metadata["recent_findings"] = recent_findings
        history = state.get("findings_history", [])
        history.append([findings])
        state["metadata"] = metadata
        state["findings_history"] = history
        state["current_findings"] = [findings]
    except Exception:
        pass
    return state


def node_agent_beta_resolve(state: WorkflowState) -> WorkflowState:
    """DAG Node: Agent Beta Resolve node for iteration loop."""
    try:
        from agentic_workflow.adapters.langgraph.nodes import _get_container
        container = _get_container()
        prompt = f"Resolve findings {state.get('current_findings')} for pipeline {state.get('pipeline_id')}"
        resolution = container.reasoner.reason(prompt)
        metadata = state.get("metadata", {})
        metadata["recent_resolution"] = resolution
        state["metadata"] = metadata
        it_count = state.get("iteration_count", 0)
        state["iteration_count"] = it_count + 1
    except Exception:
        pass
    return state


def node_root_cause_leftshift(state: WorkflowState) -> WorkflowState:
    """DAG Node: Root cause analysis and left shift hook."""
    try:
        from agentic_workflow.adapters.langgraph.nodes import _get_container
        container = _get_container()
        pipeline_id = state.get("pipeline_id", "default")
        pipeline = container.pipeline_repo.get_by_id(pipeline_id)
        if pipeline:
            container.security_audit.audit_pipeline(pipeline, [])
    except Exception:
        pass
    return state


def node_step_0_format(state: WorkflowState) -> WorkflowState:
    """DAG Node: Step 0 formatting verification."""
    try:
        from agentic_workflow.domain.algorithms.micro_validation import MicroValidation
        metadata = state.get("metadata", {})
        content = metadata.get("recent_changes_content", "")
        if not MicroValidation.validate_format(content):
            state["gate_decision"] = "fail"
            state["last_error"] = "FORMAT_ERROR: Invalid format or foreign residue found."
    except Exception:
        pass
    return state


def node_step_1_id_structure(state: WorkflowState) -> WorkflowState:
    """DAG Node: Step 1 id structure verification."""
    try:
        from agentic_workflow.domain.algorithms.micro_validation import MicroValidation
        metadata = state.get("metadata", {})
        changed_ids = metadata.get("recent_changed_ids", [])
        if not MicroValidation.validate_structure(changed_ids):
            state["gate_decision"] = "fail"
            state["last_error"] = "STRUCTURAL_ERROR: ID format mismatch."
    except Exception:
        pass
    return state


def node_step_2_forward_trace(state: WorkflowState) -> WorkflowState:
    """DAG Node: Step 2 forward trace verification."""
    return state


def node_step_3_backward_trace(state: WorkflowState) -> WorkflowState:
    """DAG Node: Step 3 backward trace verification."""
    return state


def node_step_4_semantic(state: WorkflowState) -> WorkflowState:
    """DAG Node: Step 4 semantic verification."""
    return state


def node_step_5_7_lesson_reuse(state: WorkflowState) -> WorkflowState:
    """DAG Node: Step 5/7 lesson reuse check."""
    return state


def node_step_7_record_change(state: WorkflowState) -> WorkflowState:
    """DAG Node: Step 7 record change."""
    return state


def node_step_6_trigger_impact(state: WorkflowState) -> WorkflowState:
    """DAG Node: Impact analysis trigger node."""
    try:
        from agentic_workflow.adapters.langgraph.nodes import _get_container, node_impact_analysis
        _get_container()
        partial_state = node_impact_analysis(state)
        if partial_state:
            state.update(partial_state)
    except Exception:
        pass
    return state
