"""Port Interfaces — Gateway Contracts.

Traceable to: FR-015, FR-016, FR-026, FR-027, FR-028, ADR-STR-001
Clean Architecture: domain/application depend only on these abstractions.
Adapters in adapters/llm/, adapters/mcp/ implement these interfaces.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agentic_workflow.domain.models.enums import TaskType
    from agentic_workflow.domain.models.model_config import ModelConfig


class LLMGateway(ABC):
    """Abstract gateway for LLM provider calls.

    Traceable to: FR-026 (LLM inference), FR-027 (model selection),
    FR-029 (strategy pattern), UC-003 (iteration convergence)
    """

    @abstractmethod
    def complete(
        self,
        prompt: str,
        task_type: TaskType,
        max_tokens: int = 4096,
    ) -> str:
        """Send a prompt to the LLM and return the completion.

        Args:
            prompt: The prompt string to send.
            task_type: Task type used for model selection (ALG-008).
            max_tokens: Maximum tokens for the completion.

        Returns:
            LLM completion string.
        """

    @abstractmethod
    def get_model_config(self, task_type: TaskType) -> ModelConfig:
        """Return the ModelConfig that will be used for this task type.

        Args:
            task_type: The task type to look up.

        Returns:
            ModelConfig for the selected model.
        """

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM provider is currently reachable.

        Returns:
            True if the provider API is accessible.
        """


class MCPGateway(ABC):
    """Abstract gateway for MCP (Model Context Protocol) servers.

    Traceable to: FR-028 (MCP tool invocation), INV-023 (atomic commits),
    EVT-009 (GitCommitCreated), UC-003
    """

    @abstractmethod
    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Invoke an MCP tool and return its result.

        Args:
            tool_name: Name of the MCP tool to invoke.
            arguments: Tool arguments as a dictionary.

        Returns:
            Tool result dictionary.
        """

    @abstractmethod
    def auto_commit(
        self,
        message: str,
        files: list[str],
        repo_path: str = ".",
    ) -> str:
        """Create an atomic git commit via MCP.

        Implements INV-023 (atomic commit completeness).
        EVT-009 (GitCommitCreated) is emitted on success.

        Args:
            message: Commit message.
            files: List of file paths to stage and commit.
            repo_path: Path to the git repository root.

        Returns:
            Commit SHA string.
        """

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the MCP server is currently connected.

        Returns:
            True if MCP connection is active.
        """


class SecurityGateway(ABC):
    """Abstract gateway for security scanning tools.

    Traceable to: FR-016 (security audit), DEBT-004
    """

    @abstractmethod
    def scan(self, target_path: str) -> dict[str, Any]:
        """Run a security scan on the target path.

        Args:
            target_path: Directory or file path to scan.

        Returns:
            Scan results dictionary with findings.
        """

    @abstractmethod
    def generate_sbom(self, target_path: str) -> dict[str, Any]:
        """Generate a Software Bill of Materials (SBOM).

        Args:
            target_path: Directory to analyse.

        Returns:
            SBOM dictionary in CycloneDX format.
        """


class QualityGateway(ABC):
    """Abstract gateway for external quality tools (SonarCloud, etc.).

    Traceable to: FR-015 (SonarCloud gate), DEBT-005
    """

    @abstractmethod
    def get_quality_metrics(self, project_key: str) -> dict[str, Any]:
        """Fetch quality metrics for a project.

        Args:
            project_key: Project identifier in the quality tool.

        Returns:
            Dictionary of metric names to values.
        """

    @abstractmethod
    def passes_gate(self, project_key: str) -> bool:
        """Check if the project passes the quality gate.

        Args:
            project_key: Project identifier.

        Returns:
            True if all quality thresholds are met.
        """
