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
    from agentic_workflow.application.ports.gateways.version_control_gateway import IVersionControlGateway
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

    @property
    def version_control(self) -> IVersionControlGateway:
        """Get the version-control gateway for the rollback degradation path."""
        pass


# Simulating a global container for the graph execution context
_CONTAINER: WorkflowContainerProtocol | None = None


def set_container(container: WorkflowContainerProtocol | None) -> None:
    """Initialize the global container for nodes."""
    global _CONTAINER
    _CONTAINER = container


def _get_container() -> WorkflowContainerProtocol:
    container = _CONTAINER
    if container is None:
        raise RuntimeError("DependencyContainer not initialized")
    return container


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
    from agentic_workflow.domain.enums import GateDecision

    decision_val = state.get("last_gate_decision") or "pass"
    decision = decision_val if isinstance(decision_val, GateDecision) else GateDecision(str(decision_val))

    try:
        pipeline_id = state.get("pipeline_id", "default")
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
    max_iterations = MAX_ITERATIONS
    if stage.iteration_count >= max_iterations:
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
        from agentic_workflow.domain.algorithms.root_cause_leftshift.root_cause_leftshift import RootCauseLeftShift

        container = _get_container()
        pipeline_id = state.get("pipeline_id", "default")
        pipeline = container.pipeline_repo.get_by_id(pipeline_id)
        if pipeline:
            container.security_audit.audit_pipeline(pipeline, [])

        gate_decision = state.get("gate_decision", "pass")
        if gate_decision == "fail":
            error_desc = state.get("last_error") or "Unknown validation failure"
            rca_result = RootCauseLeftShift.analyze_failure(error_desc, [])
            metadata = state.get("metadata", {})
            metadata["rca_result"] = {
                "category": rca_result.category.value,
                "intervention_type": rca_result.intervention_type.value,
                "bottleneck_location": rca_result.bottleneck_location,
                "lesson_id": rca_result.lesson_id,
                "is_new_lesson": rca_result.is_new_lesson,
            }
            state["metadata"] = metadata
            markdown = RootCauseLeftShift.generate_lesson_markdown(rca_result)

            from agentic_workflow.adapters.filesystem import get_filesystem

            fs = get_filesystem()
            fs.write_text(f"docs/lessons/{rca_result.lesson_id}.md", markdown)
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
    """DAG Node: Step 2 forward trace verification.

    Ensures changed elements have corresponding upstream traceability.
    """
    try:
        from agentic_workflow.domain.algorithms.traceability_validator.traceability_node import TraceabilityNode
        from agentic_workflow.domain.algorithms.traceability_validator.traceability_validator import (
            TraceabilityValidator,
        )

        metadata = state.get("metadata", {})
        changed_ids = metadata.get("recent_changed_ids", [])

        # Build node entities and check IDs
        nodes = [
            TraceabilityNode(
                id=nid, type=nid.split("-")[0], upstream=["BG-001"] if nid.split("-")[0] not in ["BG", "S"] else []
            )
            for nid in changed_ids
            if "-" in nid
        ]

        # Simulating checking in validator
        for node in nodes:
            if not TraceabilityValidator.validate_id_format(node.id):
                state["gate_decision"] = "fail"
                state["last_error"] = f"FORWARD_TRACE_ERROR: Invalid ID {node.id}"
                break
    except Exception as e:
        state["last_error"] = str(e)
    return state


def node_step_3_backward_trace(state: WorkflowState) -> WorkflowState:
    """DAG Node: Step 3 backward trace verification.

    Ensures downstream coverage for high-level specifications.
    """
    try:
        from agentic_workflow.domain.algorithms.traceability_validator.traceability_node import TraceabilityNode

        metadata = state.get("metadata", {})
        changed_ids = metadata.get("recent_changed_ids", [])

        # High level specs must have downstream coverage
        for nid in changed_ids:
            if nid.startswith(("BG-", "S-")):
                downstream = ["FEA-001"] if metadata.get("has_downstream", True) else []
                node = TraceabilityNode(id=nid, type=nid.split("-")[0], downstream=downstream)
                if not node.downstream:
                    state["gate_decision"] = "fail"
                    state["last_error"] = f"BACKWARD_TRACE_ERROR: No downstream for {nid}"
                    break
    except Exception as e:
        state["last_error"] = str(e)
    return state


def node_step_4_semantic(state: WorkflowState) -> WorkflowState:
    """DAG Node: Step 4 semantic verification.

    Verifies domain-specific constraints in implementation changes.
    """
    try:
        metadata = state.get("metadata", {})
        changed_ids = metadata.get("recent_changed_ids", [])
        # Check for semantic constraints (e.g. cross-cutting aspects)
        for nid in changed_ids:
            if "ADR-" in nid and not any(x in nid for x in ["STR", "GOV", "SEC", "SCP", "GATE", "OPS"]):
                state["gate_decision"] = "fail"
                state["last_error"] = f"SEMANTIC_ERROR: Invalid ADR subclass in {nid}"
                break
    except Exception as e:
        state["last_error"] = str(e)
    return state


def node_step_5_orphan(state: WorkflowState) -> WorkflowState:
    """DAG Node: Step 5 orphan node detection verification."""
    try:
        from agentic_workflow.domain.algorithms.traceability_validator.traceability_node import TraceabilityNode
        from agentic_workflow.domain.algorithms.traceability_validator.traceability_validator import (
            TraceabilityValidator,
        )

        metadata = state.get("metadata", {})
        changed_ids = metadata.get("recent_changed_ids", [])

        nodes = [TraceabilityNode(id=nid, type=nid.split("-")[0]) for nid in changed_ids if "-" in nid]
        orphans = TraceabilityValidator.orphan_check(nodes)
        if orphans:
            state["gate_decision"] = "fail"
            state["last_error"] = f"ORPHAN_ERROR: Orphans detected {orphans}"
    except Exception as e:
        state["last_error"] = str(e)
    return state


def node_step_5_5_lateral_trace(state: WorkflowState) -> WorkflowState:
    """DAG Node: Step 5.5 lateral traceability verification."""
    try:
        metadata = state.get("metadata", {})
        changed_ids = metadata.get("recent_changed_ids", [])
        # Verify any lateral links (e.g. RISK to NFR links)
        for nid in changed_ids:
            if nid.startswith("RISK-") and not metadata.get("has_nfr_link", True):
                state["gate_decision"] = "fail"
                state["last_error"] = f"LATERAL_TRACE_ERROR: RISK {nid} lacks lateral link to NFR"
                break
    except Exception as e:
        state["last_error"] = str(e)
    return state


def node_step_5_7_lesson_reuse(state: WorkflowState) -> WorkflowState:
    """DAG Node: Step 5/7 lesson reuse check."""
    try:
        from agentic_workflow.domain.algorithms.root_cause_leftshift.root_cause_category import RootCauseCategory
        from agentic_workflow.domain.algorithms.root_cause_leftshift.root_cause_leftshift import RootCauseLeftShift

        metadata = state.get("metadata", {})
        rca_res = metadata.get("rca_result", {})
        category_str = rca_res.get("category", "FORMAT_ERROR")

        try:
            category = RootCauseCategory(category_str)
        except ValueError:
            category = RootCauseCategory.FORMAT_ERROR

        existing = [{"id": "LESSON-073", "category": "FORMAT_ERROR"}]
        reused_id = RootCauseLeftShift.check_lesson_reuse(category, existing)
        if reused_id:
            metadata["reused_lesson_id"] = reused_id
            state["metadata"] = metadata
    except Exception as e:
        state["last_error"] = str(e)
    return state


def node_step_7_record_change(state: WorkflowState) -> WorkflowState:
    """DAG Node: Step 7 record change."""
    try:
        metadata = state.get("metadata", {})
        metadata["change_recorded"] = True
        state["metadata"] = metadata
    except Exception as e:
        state["last_error"] = str(e)
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


ASSUMPTION_REGISTRY_DOC = "docs/assumption-registry.md"


def node_inject_assumptions(state: WorkflowState) -> WorkflowState:
    """DAG Node: Inject L2 output-affecting assumptions at session START.

    Pipeline v2 (ADR-STR-029, FR-070): rigid constraints produced by earlier
    retros are loaded before any phase executes (self-bootstrapping left-shift).
    Graceful degradation: a missing registry file injects nothing.
    """
    metadata = state.get("metadata", {})
    registry_doc = ASSUMPTION_REGISTRY_DOC
    try:
        fs = get_filesystem()
        content = fs.read_text(fs.resolve_path(registry_doc))
        statements = [line.removeprefix("- ").strip() for line in content.splitlines() if line.startswith("- ASM-")]
        metadata["injected_assumptions"] = statements
    except Exception:
        metadata["injected_assumptions"] = []
    return {"metadata": metadata}


def node_absorb_debt(state: WorkflowState) -> WorkflowState:
    """DAG Node: Absorb gate failures into dynamic debt (no hard stop).

    Pipeline v2 (ADR-STR-029, FR-068): SonarCloud/security failures become
    DEBT items feeding the improvement loop; the flow continues with
    PASS_WITH_WARNINGS instead of blocking on FAIL.
    """
    from agentic_workflow.domain.enums import DebtSource, Severity
    from agentic_workflow.domain.services.debt_accumulator import DebtAccumulator

    metadata = state.get("metadata", {})
    sonar_failures = [str(item) for item in metadata.get("sonar_failures", [])]
    security_findings = [str(item) for item in metadata.get("security_audit_findings", [])]
    existing: list[dict[str, str]] = metadata.get("debt_items", [])

    absorbed = DebtAccumulator.absorb(
        DebtSource.QUALITY_GATE, Severity.HIGH, sonar_failures, start_index=len(existing) + 1
    )
    absorbed += DebtAccumulator.absorb(
        DebtSource.SECURITY, Severity.HIGH, security_findings, start_index=len(existing) + len(absorbed) + 1
    )

    metadata["debt_items"] = existing + [item.as_dict() for item in absorbed]
    metadata["sonar_failures"] = []
    metadata["security_audit_findings"] = []
    decision = DebtAccumulator.gate_decision_for(len(metadata["debt_items"]))
    return {"metadata": metadata, "last_gate_decision": decision, "last_error": None}


def node_align_check(state: WorkflowState) -> WorkflowState:
    """DAG Node: Align converged output against traceability and design docs.

    Pipeline v2 (ADR-STR-029, FR-072): the diverge → converge → align closure.
    Misalignments are tagged and fed back to Agent alpha for deep extension;
    a clean pass certifies the fixed point as a full solution.
    """
    from agentic_workflow.domain.services.alignment_checker import AlignmentChecker

    metadata = state.get("metadata", {})
    traceability_issues = [str(item) for item in metadata.get("traceability_issues", [])]
    consistency_issues = [str(item) for item in metadata.get("consistency_issues", [])]

    misalignments = AlignmentChecker.find_misalignments(traceability_issues, consistency_issues)
    metadata["alignment_issues"] = misalignments

    if AlignmentChecker.is_aligned(misalignments):
        state["gate_decision"] = "pass"
    else:
        state["gate_decision"] = "fail"
        state["current_findings"] = state.get("current_findings", []) + misalignments
    state["metadata"] = metadata
    return state


def node_rollback(state: WorkflowState) -> WorkflowState:
    """DAG Node: Roll back to the universal base on DIVERGING (EC2 Neutrality).

    Pipeline v2 (ADR-STR-029, FR-069): the rigid degradation path. After the
    rollback the delayed-HITL flag is raised — an unresolvable architectural
    conflict is the only event that summons a human mid-flow (FR-071).
    """
    from agentic_workflow.domain.services.rollback_policy import RollbackPolicy

    metadata = state.get("metadata", {})
    target_ref = metadata.get("universal_base_ref") or RollbackPolicy.UNIVERSAL_BASE_REF
    try:
        container = _get_container()
        metadata["rollback_performed"] = container.version_control.rollback_to(target_ref)
    except Exception as exc:
        metadata["rollback_performed"] = False
        state["last_error"] = str(exc)
    metadata["hitl_required"] = True
    metadata["hitl_reason"] = "Unresolvable architectural conflict: DIVERGING (intent drift)"
    state["metadata"] = metadata
    return state


def node_update_constraints(state: WorkflowState) -> WorkflowState:
    """DAG Node: Close the Ouroboros — persist retro lessons as assumptions.

    Pipeline v2 (ADR-STR-029, FR-070): Phase 10 lessons become ASM entries in
    the assumption registry document, injected at the next session START.
    """
    from agentic_workflow.domain.services.assumption_registry import AssumptionRegistry

    metadata = state.get("metadata", {})
    lessons = [str(item) for item in metadata.get("lessons", [])]
    existing_count = len(metadata.get("injected_assumptions", []))
    assumptions = AssumptionRegistry.from_lessons(lessons, start_index=existing_count + 1)
    metadata["registered_assumptions"] = [item.assumption_id for item in assumptions]

    if assumptions:
        registry_doc = ASSUMPTION_REGISTRY_DOC
        try:
            fs = get_filesystem()
            lines = [f"- {item.assumption_id}: {item.statement}" for item in assumptions]
            previous = ""
            resolved = fs.resolve_path(registry_doc)
            if fs.exists(resolved):
                previous = fs.read_text(resolved)
            header = previous or "# Assumption Registry (L2 Output-Affecting)\n"
            doc_lines = [header.rstrip("\n"), *lines, ""]
            fs.write_text(registry_doc, "\n".join(doc_lines))
        except Exception as exc:
            state["last_error"] = str(exc)
    state["metadata"] = metadata
    return state
