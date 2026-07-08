"""Composition Root: Dependency Injection Container."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agentic_workflow.adapters.orchestration.node_executor import NodeExecutor
    from agentic_workflow.adapters.orchestration.nodes import SonarAdapterProtocol
    from agentic_workflow.application.use_cases.verify_invariants import VerifyDAGInvariantsUseCase


from agentic_workflow.application.ports.doc_io.document_io_gateway import DocumentIOGateway
from agentic_workflow.application.ports.gateways.agent_orchestrator_gateway import IAgentOrchestratorGateway
from agentic_workflow.application.ports.gateways.agent_reasoner import IAgentReasoner
from agentic_workflow.application.ports.gateways.prompt_optimizer import IPromptOptimizer
from agentic_workflow.application.ports.gateways.version_control_gateway import IVersionControlGateway
from agentic_workflow.application.ports.repositories.checkpoint_repository import CheckpointRepository
from agentic_workflow.application.ports.repositories.pipeline_repository import IPipelineRepository
from agentic_workflow.application.use_cases.advance_pipeline import AdvancePipelineUseCase
from agentic_workflow.application.use_cases.run_iteration import RunIterationUseCase
from agentic_workflow.application.use_cases.start_pipeline import StartPipelineUseCase
from agentic_workflow.domain.services.orchestrator_service import (
    IOrchestratorService,
    OrchestratorService,
)
from agentic_workflow.domain.services.security_audit_service import (
    ISecurityAuditService,
    SecurityAuditService,
)
from agentic_workflow.domain.value_objects.sonarcloud_config import SonarCloudConfig
from agentic_workflow.frameworks.config import WorkflowConfigLoader


class SonarConfigLoader:
    """Helper class to build and load default sonar config without module level functions."""

    @staticmethod
    def build(raw: Any) -> SonarCloudConfig:
        """Build SonarCloudConfig from raw configuration."""
        fb = raw.feedback
        d = {"token": raw.token, "project_key": raw.project_key, "organization": raw.organization}
        d.update({"auto_convert_to_debt": fb.auto_convert_to_debt, "default_debt_priority": fb.default_debt_priority})
        return SonarCloudConfig(**d, on_missing_config=raw.on_missing_config)

    @classmethod
    def load(cls) -> SonarCloudConfig:
        """Load default sonar configuration."""
        try:
            raw: Any = WorkflowConfigLoader.load().sonarcloud
            cfg = cls.build(raw)
        except Exception:
            cfg = SonarCloudConfig()
        return cfg


@dataclass
class DependencyContainer:
    """Container holding all application dependencies.

    Initialized at the system entry point (Composition Root).
    """

    # Ports/Adapters
    pipeline_repo: IPipelineRepository
    checkpoint_repo: CheckpointRepository
    doc_io: DocumentIOGateway
    reasoner: IAgentReasoner
    orchestrator: IOrchestratorService = field(default_factory=OrchestratorService)
    security_audit: ISecurityAuditService = field(default_factory=SecurityAuditService)
    sonar_config: SonarCloudConfig = field(default_factory=SonarConfigLoader.load)

    def __post_init__(self) -> None:
        """Register the filesystem and executor implementations under frameworks."""
        from agentic_workflow.adapters.filesystem import register_filesystem
        from agentic_workflow.adapters.subprocess import register_executor
        from agentic_workflow.frameworks.filesystem_io import OSFilesystemIO
        from agentic_workflow.frameworks.subprocess_executor import OSSubprocessExecutor

        register_filesystem(OSFilesystemIO())
        register_executor(OSSubprocessExecutor())

    # Use Cases
    @property
    def start_pipeline(self) -> StartPipelineUseCase:
        """Get the StartPipelineUseCase instance."""
        return StartPipelineUseCase(self.pipeline_repo)

    @property
    def advance_pipeline(self) -> AdvancePipelineUseCase:
        """Get the AdvancePipelineUseCase instance."""
        return AdvancePipelineUseCase(self.pipeline_repo)

    @property
    def run_iteration(self) -> RunIterationUseCase:
        """Get the RunIterationUseCase instance."""
        return RunIterationUseCase(self.pipeline_repo)

    @property
    def verify_invariants(self) -> VerifyDAGInvariantsUseCase:
        """Get the VerifyDAGInvariantsUseCase instance."""
        from agentic_workflow.application.use_cases.verify_invariants import VerifyDAGInvariantsUseCase
        from agentic_workflow.domain.algorithms.invariants_verifier import DAGInvariantVerifier

        return VerifyDAGInvariantsUseCase(DAGInvariantVerifier())

    @property
    def sonar_adapter(self) -> SonarAdapterProtocol:
        """Get the SonarCloudAdapter for the current sonar_config."""
        from agentic_workflow.frameworks.sonarcloud.sonar_adapter import SonarCloudAdapter

        return SonarCloudAdapter(self.sonar_config)

    @property
    def version_control(self) -> IVersionControlGateway:
        """Get the version-control gateway for the rollback degradation path."""
        from agentic_workflow.frameworks.git_version_control import GitVersionControl

        return GitVersionControl()

    @property
    def agent_orchestrator(self) -> IAgentOrchestratorGateway:
        """Get the external agent orchestrator gateway (Archon, ADR-STR-030)."""
        from agentic_workflow.frameworks.archon_orchestrator import ArchonOrchestrator

        return ArchonOrchestrator()

    @property
    def prompt_optimizer(self) -> IPromptOptimizer:
        """Get the prompt optimizer gateway (DSPy with few-shot fallback, ADR-STR-031)."""
        from agentic_workflow.frameworks.dspy_prompt_optimizer import DSPyPromptOptimizer

        return DSPyPromptOptimizer()

    @property
    def node_executor(self) -> NodeExecutor:
        """Get the single-node executor invoked by Archon workflow steps (ADR-STR-033)."""
        from agentic_workflow.adapters.orchestration.node_executor import NodeExecutor

        return NodeExecutor(self.checkpoint_repo)


# Backward compatibility facades
_load_default_sonar_config = SonarConfigLoader.load
