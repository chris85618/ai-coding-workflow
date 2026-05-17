"""Unit tests for DependencyContainer."""

from unittest.mock import MagicMock

import pytest

from agentic_workflow.application.ports.doc_io.document_io_gateway import DocumentIOGateway
from agentic_workflow.application.ports.gateways.agent_reasoner import IAgentReasoner
from agentic_workflow.application.ports.repositories.checkpoint_repository import CheckpointRepository
from agentic_workflow.application.ports.repositories.pipeline_repository import IPipelineRepository
from agentic_workflow.application.use_cases.advance_pipeline import AdvancePipelineUseCase
from agentic_workflow.application.use_cases.run_iteration import RunIterationUseCase
from agentic_workflow.application.use_cases.start_pipeline import StartPipelineUseCase
from agentic_workflow.domain.services.orchestrator_service import OrchestratorService
from agentic_workflow.domain.services.security_audit_service import SecurityAuditService
from agentic_workflow.frameworks.dependency_container import DependencyContainer


class TestDependencyContainer:
    """Test suite for DependencyContainer wiring."""

    @pytest.fixture
    def mock_repo(self) -> MagicMock:
        """Create a mock pipeline repository."""
        return MagicMock(spec=IPipelineRepository)

    @pytest.fixture
    def mock_io(self) -> MagicMock:
        """Create a mock document IO gateway."""
        return MagicMock(spec=DocumentIOGateway)

    @pytest.fixture
    def mock_reasoner(self) -> MagicMock:
        """Create a mock agent reasoner."""
        return MagicMock(spec=IAgentReasoner)

    @pytest.fixture
    def mock_checkpoint_repo(self) -> MagicMock:
        """Create a mock checkpoint repository."""
        return MagicMock(spec=CheckpointRepository)

    def test_container_initialization(
        self,
        mock_repo: MagicMock,
        mock_io: MagicMock,
        mock_reasoner: MagicMock,
        mock_checkpoint_repo: MagicMock,
    ) -> None:
        """Verify the container correctly stores dependencies."""
        container = DependencyContainer(
            pipeline_repo=mock_repo,
            checkpoint_repo=mock_checkpoint_repo,
            doc_io=mock_io,
            reasoner=mock_reasoner,
        )
        assert container.pipeline_repo == mock_repo
        assert container.checkpoint_repo == mock_checkpoint_repo
        assert container.doc_io == mock_io
        assert container.reasoner == mock_reasoner

    def test_use_case_instantiation(
        self,
        mock_repo: MagicMock,
        mock_io: MagicMock,
        mock_reasoner: MagicMock,
        mock_checkpoint_repo: MagicMock,
    ) -> None:
        """Verify that use cases are correctly instantiated with dependencies."""
        container = DependencyContainer(
            pipeline_repo=mock_repo,
            checkpoint_repo=mock_checkpoint_repo,
            doc_io=mock_io,
            reasoner=mock_reasoner,
        )

        assert isinstance(container.start_pipeline, StartPipelineUseCase)
        assert container.start_pipeline._repo == mock_repo

        assert isinstance(container.advance_pipeline, AdvancePipelineUseCase)
        assert container.advance_pipeline._repo == mock_repo

        assert isinstance(container.run_iteration, RunIterationUseCase)
        assert container.run_iteration._repo == mock_repo

    def test_service_instantiation(
        self,
        mock_repo: MagicMock,
        mock_io: MagicMock,
        mock_reasoner: MagicMock,
        mock_checkpoint_repo: MagicMock,
    ) -> None:
        """Verify that services are correctly instantiated."""
        container = DependencyContainer(
            pipeline_repo=mock_repo,
            checkpoint_repo=mock_checkpoint_repo,
            doc_io=mock_io,
            reasoner=mock_reasoner,
        )

        assert isinstance(container.orchestrator, OrchestratorService)
        assert isinstance(container.security_audit, SecurityAuditService)

    def test_load_default_sonar_config_exception(self) -> None:
        """Verify that default SonarCloudConfig is returned on config load exception."""
        from unittest.mock import patch
        with patch("agentic_workflow.frameworks.config.WorkflowConfigLoader.load", side_effect=ValueError("Test")):
            from agentic_workflow.frameworks.dependency_container import _load_default_sonar_config
            config = _load_default_sonar_config()
            assert config.token is None

