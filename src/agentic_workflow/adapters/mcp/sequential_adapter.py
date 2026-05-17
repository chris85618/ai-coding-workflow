"""MCP Adapter — Sequential Thinking MCP Server Gateway.

Implements: MCPGateway port (sequential thinking subset)
Traceable to: FR-028 (MCP tool invocation), ADR-STR-004
Wraps the Sequential Thinking MCP server for structured reasoning chains.
Falls back to a passthrough mode if the MCP server is unavailable.
External I/O is fully injected via HttpClientPort (ADR-STR-027 DIP).
"""

from __future__ import annotations

from typing import Any

from agentic_workflow.adapters.http import HttpClientPort
from agentic_workflow.application.ports.gateways import MCPGateway


class SequentialThinkingMCPAdapter(MCPGateway):
    """Sequential Thinking MCP server adapter.

    Provides structured step-by-step reasoning via the MCP protocol.
    In local/test environments without an active MCP server, the
    ``is_connected()`` check returns False and calls return an error result.

    Args:
        server_url: MCP server URL (e.g., "http://localhost:3000").
        event_bus: Optional DomainEventBus for event publishing.
        http_client: HttpClientPort implementation (injected for DIP).
                     When None, all network calls return failure results.
    """

    def __init__(
        self,
        server_url: str = "http://localhost:3000",
        event_bus: object | None = None,
        http_client: HttpClientPort | None = None,
    ) -> None:
        """Initialize the Sequential Thinking MCP adapter."""
        # SEC-004: SSRF protection — pure string validation (no urllib dependency).
        _scheme, _, _rest = server_url.partition("://")
        if _scheme not in ("http", "https"):
            raise ValueError(
                f"SSRF protection: unsupported URL scheme {_scheme!r}. "
                "Only http (localhost) and https are allowed (SEC-004).",
            )
        if _scheme == "http":
            # Strip port and path to get hostname only
            _host = _rest.partition("/")[0].partition(":")[0].strip("[]")
            if _host not in ("localhost", "127.0.0.1", "::1"):
                msg = (
                    f"SSRF protection: http:// is only allowed for localhost, "
                    f"got {server_url!r}. Use https:// for remote MCP servers (SEC-004)."
                )
                raise ValueError(msg)
        self._server_url = server_url
        self._event_bus = event_bus
        self._http_client = http_client

    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Invoke a Sequential Thinking MCP tool.

        Supported tools: ``sequentialthinking``

        Args:
            tool_name: MCP tool name.
            arguments: Tool arguments (thought, nextThoughtNeeded, etc.).

        Returns:
            Result dictionary from the MCP server.
        """
        if tool_name != "sequentialthinking":
            return {"success": False, "output": f"Unknown tool: {tool_name}"}

        if self._http_client is None:
            return {"success": False, "output": "HTTP client not configured"}

        payload: dict[str, Any] = {
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
            },
        }
        try:
            result = self._http_client.post_json(self._server_url, payload)
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
            "SequentialThinkingMCPAdapter does not support git commits. Use GitKrakenMCPAdapter for auto_commit().",
        )

    def is_connected(self) -> bool:
        """Check if the Sequential Thinking MCP server is reachable.

        Returns:
            True if the server responds; False if no client or unreachable.
        """
        if self._http_client is None:
            return False
        return self._http_client.is_reachable(self._server_url)
