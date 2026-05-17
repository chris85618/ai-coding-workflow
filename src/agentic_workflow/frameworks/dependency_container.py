"""Composition Root: Dependency Injection Container."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_workflow.adapters.langgraph.nodes import SonarAdapterProtocol


from agentic_workflow.application.ports.doc_io.document_io_gateway import DocumentIOGateway
from agentic_workflow.application.ports.gateways.agent_reasoner import IAgentReasoner
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


def _load_default_sonar_config() -> SonarCloudConfig:
    """Helper to load default sonar configuration for container field initialization."""
    try:
        raw = WorkflowConfigLoader.load().sonarcloud
        return SonarCloudConfig(
            token=raw.token,
            project_key=raw.project_key,
            organization=raw.organization,
            auto_convert_to_debt=raw.feedback.auto_convert_to_debt,
            default_debt_priority=raw.feedback.default_debt_priority,
            on_missing_config=raw.on_missing_config,
        )
    except Exception:
        return SonarCloudConfig()


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
    sonar_config: SonarCloudConfig = field(default_factory=_load_default_sonar_config)

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
    def sonar_adapter(self) -> SonarAdapterProtocol:
        """Get the SonarCloudAdapter for the current sonar_config."""
        from agentic_workflow.frameworks.sonarcloud.sonar_adapter import SonarCloudAdapter

        return SonarCloudAdapter(self.sonar_config)
