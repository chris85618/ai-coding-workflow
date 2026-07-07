"""Tests for the ArchonOrchestrator frameworks gateway (FR-073, FR-074, ADR-STR-030)."""

from agentic_workflow.adapters.archon.workflow_mapper import ArchonWorkflowMapper
from agentic_workflow.adapters.filesystem import register_filesystem
from agentic_workflow.adapters.subprocess import SubprocessExecutor, register_executor
from agentic_workflow.application.ports.gateways.agent_orchestrator_gateway import (
    IAgentOrchestratorGateway,
)
from agentic_workflow.frameworks.archon_orchestrator import ArchonOrchestrator
from agentic_workflow.frameworks.filesystem_io import OSFilesystemIO
from agentic_workflow.frameworks.subprocess_executor import OSSubprocessExecutor


class RecordingExecutor(SubprocessExecutor):
    """Records commands and replays a canned exit code for archon calls."""

    def __init__(self, code: int = 0) -> None:
        """Store the canned exit code."""
        self.code = code
        self.commands: list[list[str]] = []

    def run_cmd(self, cmd: str) -> tuple[int, str, str]:
        """Unused string-command variant."""
        return (self.code, "", "")

    def run_cmd_list(self, cmd: list[str], cwd: str | None = None, timeout: int = 30) -> tuple[int, str, str]:
        """Record the command and replay the canned result."""
        self.commands.append(cmd)
        return (self.code, "", "")


class RecordingFilesystem(OSFilesystemIO):
    """Captures written documents in memory instead of touching the disk."""

    def __init__(self) -> None:
        """Prepare the write and mkdir journals."""
        super().__init__()
        self.written: dict[str, str] = {}
        self.made_dirs: list[str] = []

    def mkdir(self, path: str, parents: bool = True, exist_ok: bool = True) -> None:
        """Record the directory creation request."""
        self.made_dirs.append(path)

    def write_text(self, path: str, content: str, encoding: str = "utf-8") -> None:
        """Record the written document."""
        self.written[path] = content


class TestArchonOrchestrator:
    """Covers export and dispatch over the filesystem and executor ports."""

    def teardown_method(self) -> None:
        """Restore the OS implementations so other tests keep real registrations."""
        register_filesystem(OSFilesystemIO())
        register_executor(OSSubprocessExecutor())

    def test_export_workflow_matches_mapper_output(self) -> None:
        """TC-ARCHON-005: export_workflow renders exactly the mapper's document."""
        stages = ["phase0", "stage8"]
        expected = ArchonWorkflowMapper().to_workflow_yaml("main", stages)
        assert ArchonOrchestrator().export_workflow("main", stages) == expected

    def test_dispatch_persists_document_and_runs_archon(self) -> None:
        """TC-ARCHON-006: dispatch writes the YAML then invokes archon run on it."""
        fs = RecordingFilesystem()
        executor = RecordingExecutor(code=0)
        register_filesystem(fs)
        register_executor(executor)
        assert ArchonOrchestrator().dispatch("name: wf\n") is True
        assert fs.made_dirs == [".archon"]
        assert fs.written == {".archon/agentic-workflow.yaml": "name: wf\n"}
        assert executor.commands == [["archon", "run", ".archon/agentic-workflow.yaml"]]

    def test_dispatch_degrades_gracefully_without_archon_binary(self) -> None:
        """TC-ARCHON-007: dispatch reports False when the archon CLI is unavailable."""
        register_filesystem(RecordingFilesystem())
        register_executor(RecordingExecutor(code=127))
        assert ArchonOrchestrator().dispatch("name: wf\n") is False

    def test_container_exposes_orchestrator_injection_point(self) -> None:
        """TC-ARCHON-008: DependencyContainer.agent_orchestrator provides the gateway."""
        from unittest.mock import MagicMock

        from agentic_workflow.application.ports.doc_io.document_io_gateway import DocumentIOGateway
        from agentic_workflow.application.ports.gateways.agent_reasoner import IAgentReasoner
        from agentic_workflow.application.ports.repositories.checkpoint_repository import CheckpointRepository
        from agentic_workflow.application.ports.repositories.pipeline_repository import IPipelineRepository
        from agentic_workflow.frameworks.dependency_container import DependencyContainer

        container = DependencyContainer(
            pipeline_repo=MagicMock(spec=IPipelineRepository),
            checkpoint_repo=MagicMock(spec=CheckpointRepository),
            doc_io=MagicMock(spec=DocumentIOGateway),
            reasoner=MagicMock(spec=IAgentReasoner),
        )
        gateway = container.agent_orchestrator
        assert isinstance(gateway, ArchonOrchestrator)
        assert isinstance(gateway, IAgentOrchestratorGateway)
