"""Port Interface — MCPGateway Contract.

Traceable to: FR-028, INV-023, EVT-009, ADR-STR-001
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


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
