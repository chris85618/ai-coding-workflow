"""Composition Root: Dependency Injection Container."""

from __future__ import annotations

from dataclasses import dataclass

from agentic_workflow.application.ports.doc_io.document_io_gateway import DocumentIOGateway
from agentic_workflow.application.ports.gateways.agent_reasoner import IAgentReasoner
from agentic_workflow.application.ports.repositories.checkpoint_repository import CheckpointRepository
from agentic_workflow.application.ports.repositories.pipeline_repository import IPipelineRepository
from agentic_workflow.application.use_cases.advance_pipeline import AdvancePipelineUseCase
from agentic_workflow.application.use_cases.run_iteration import RunIterationUseCase
from agentic_workflow.application.use_cases.start_pipeline import StartPipelineUseCase
from agentic_workflow.domain.services.orchestrator_service import OrchestratorService
from agentic_workflow.domain.services.security_audit_service import SecurityAuditService


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
    def orchestrator(self) -> OrchestratorService:
        """Get the OrchestratorService instance."""
        return OrchestratorService()

    @property
    def security_audit(self) -> SecurityAuditService:
        """Get the SecurityAuditService instance."""
        return SecurityAuditService()
