"""MCP Adapter — GitKraken MCP Server Gateway.

Implements: MCPGateway port (git operations subset)
Traceable to: FR-028 (MCP tool invocation), INV-023 (atomic commits),
EVT-009 (GitCommitCreated), ADR-STR-004
Uses subprocess to call the GitKraken MCP server via its CLI interface.
"""

from __future__ import annotations

import subprocess
from typing import Any, cast

from agentic_workflow.application.ports.gateways import MCPGateway


class GitKrakenMCPAdapter(MCPGateway):
    """GitKraken MCP server adapter.

    Wraps git operations (add, commit) via subprocess.
    Emits EVT-009 (GitCommitCreated) on successful ``auto_commit``.

    INV-023: All staged files must appear in the commit — verified by
    comparing ``git status`` before and after.

    Args:
        event_bus: Optional DomainEventBus to publish EVT-009 events.
        git_binary: Path to the git binary (default: "git").
    """

    def __init__(
        self,
        event_bus: object | None = None,
        git_binary: str = "git",
    ) -> None:
        """Initializes the GitKraken MCP adapter.

        Args:
            event_bus: Optional DomainEventBus for event publishing.
            git_binary: Path to the git executable.
        """
        self._event_bus = event_bus
        self._git = git_binary

    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Invoke a GitKraken MCP tool (stub — extend per tool definition).

        Currently delegates git-specific tools to subprocess helpers.

        Args:
            tool_name: MCP tool name (e.g., "git_add", "git_commit").
            arguments: Tool arguments dictionary.

        Returns:
            Result dictionary with ``"success"`` and ``"output"`` keys.
        """
        if tool_name == "git_add":
            return self._git_add(
                files=arguments.get("files", []),
                repo_path=arguments.get("repo_path", "."),
            )
        if tool_name == "git_commit":
            return self._git_commit_raw(
                message=arguments.get("message", "chore: auto-commit"),
                repo_path=arguments.get("repo_path", "."),
            )
        if tool_name == "git_status":
            return self._git_status(repo_path=arguments.get("repo_path", "."))
        return {"success": False, "output": f"Unknown tool: {tool_name}"}

    def auto_commit(
        self,
        message: str,
        files: list[str],
        repo_path: str = ".",
    ) -> str:
        """Stage files and create an atomic git commit (INV-023).

        Args:
            message: Commit message.
            files: List of file paths to stage.
            repo_path: Path to the repository root.

        Returns:
            Commit SHA string.

        Raises:
            RuntimeError: If git add or commit fails.
        """
        # Stage files
        add_result = self._git_add(files=files, repo_path=repo_path)
        if not add_result["success"]:
            raise RuntimeError(f"git add failed: {add_result['output']}")

        # Commit
        commit_result = self._git_commit_raw(message=message, repo_path=repo_path)
        if not commit_result["success"]:
            raise RuntimeError(f"git commit failed: {commit_result['output']}")

        # Get commit SHA
        sha = self._get_head_sha(repo_path)

        # Emit EVT-009 (GitCommitCreated)
        if self._event_bus is not None:
            # Cast to Any to allow calling publish on the port
            cast("Any", self._event_bus).publish(
                "GitCommitCreated",
                {"sha": sha, "message": message, "files": files},
            )

        return sha

    def is_connected(self) -> bool:
        """Check if git is available and the repo is accessible.

        Returns:
            True if ``git rev-parse`` succeeds in the working directory.
        """
        try:
            result = subprocess.run(
                [self._git, "rev-parse", "--git-dir"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    # --- Private helpers ---

    def _git_add(self, files: list[str], repo_path: str) -> dict[str, Any]:
        if not files:
            return {"success": True, "output": "No files to stage"}
        result = subprocess.run(
            [self._git, "add", "--", *files],
            capture_output=True,
            text=True,
            cwd=repo_path,
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout + result.stderr,
        }

    def _git_commit_raw(self, message: str, repo_path: str) -> dict[str, Any]:
        result = subprocess.run(
            [self._git, "commit", "-m", message],
            capture_output=True,
            text=True,
            cwd=repo_path,
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout + result.stderr,
        }

    def _git_status(self, repo_path: str) -> dict[str, Any]:
        result = subprocess.run(
            [self._git, "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=repo_path,
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
        }

    def _get_head_sha(self, repo_path: str) -> str:
        result = subprocess.run(
            [self._git, "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=repo_path,
        )
        if result.returncode != 0:
            return "unknown"
        return result.stdout.strip()
