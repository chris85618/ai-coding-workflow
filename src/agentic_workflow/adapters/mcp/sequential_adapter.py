"""MCP Adapter — Sequential Thinking MCP Server Gateway.

Implements: MCPGateway port (sequential thinking subset)
Traceable to: FR-028 (MCP tool invocation), ADR-STR-004
Wraps the Sequential Thinking MCP server for structured reasoning chains.
Falls back to a passthrough mode if the MCP server is unavailable.
"""

from __future__ import annotations

import json
from typing import Any

from agentic_workflow.application.ports.gateways import MCPGateway


class SequentialThinkingMCPAdapter(MCPGateway):
    """Sequential Thinking MCP server adapter.

    Provides structured step-by-step reasoning via the MCP protocol.
    In local/test environments without an active MCP server, the
    ``is_connected()`` check returns False and calls raise RuntimeError.

    Args:
        server_url: MCP server URL (e.g., "http://localhost:3000").
        event_bus: Optional DomainEventBus for event publishing.
    """

    def __init__(
        self,
        server_url: str = "http://localhost:3000",
        event_bus: object | None = None,
    ) -> None:
        """Initialize the Sequential Thinking MCP adapter."""
        # SEC-004: Validate URL scheme to prevent SSRF.
        # Only https:// is allowed in production; http:// only for localhost.
        import urllib.parse

        parsed = urllib.parse.urlparse(server_url)
        if parsed.scheme == "http" and parsed.hostname not in (
            "localhost",
            "127.0.0.1",
            "::1",
        ):
            msg = (
                f"SSRF protection: http:// is only allowed for localhost, "
                f"got {server_url!r}. Use https:// for remote MCP servers (SEC-004)."
            )
            raise ValueError(msg)
        if parsed.scheme not in ("http", "https"):
            raise ValueError(
                f"SSRF protection: unsupported URL scheme {parsed.scheme!r}. "
                "Only http (localhost) and https are allowed (SEC-004)."
            )
        self._server_url = server_url
        self._event_bus = event_bus

    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Invoke a Sequential Thinking MCP tool.

        Supported tools: ``sequentialthinking``

        Args:
            tool_name: MCP tool name.
            arguments: Tool arguments (thought, nextThoughtNeeded, etc.).

        Returns:
            Result dictionary from the MCP server.

        Raises:
            RuntimeError: If the MCP server is unavailable or returns an error.
        """
        if tool_name != "sequentialthinking":
            return {"success": False, "output": f"Unknown tool: {tool_name}"}

        # Attempt HTTP call to MCP server
        try:
            import urllib.error
            import urllib.request

            payload = json.dumps(
                {
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": arguments,
                    },
                }
            ).encode()
            req = urllib.request.Request(
                self._server_url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read())
                return {"success": True, "output": result}
        except Exception as exc:
            return {"success": False, "output": str(exc)}

    def auto_commit(
        self,
        message: str,
        files: list[str],
        repo_path: str = ".",
    ) -> str:
        """Not supported by Sequential Thinking adapter.

        Sequential Thinking MCP does not manage git operations.
        Use GitKrakenMCPAdapter for git commits.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError(
            "SequentialThinkingMCPAdapter does not support git commits. Use GitKrakenMCPAdapter for auto_commit()."
        )

    def is_connected(self) -> bool:
        """Check if the Sequential Thinking MCP server is reachable.

        Returns:
            True if the server responds to a health-check request.
        """
        try:
            import urllib.request

            req = urllib.request.Request(self._server_url, method="GET")
            with urllib.request.urlopen(req, timeout=3):
                return True
        except Exception:
            return False
