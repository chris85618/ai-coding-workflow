"""TC-126, TC-127: SequentialThinkingMCPAdapter tests."""

from unittest.mock import MagicMock

from agentic_workflow.adapters.mcp.sequential_adapter import (
    SequentialThinkingMCPAdapter,
)


class TestSequentialThinkingMCPAdapter:
    """TC-126, TC-127: MCP adapter tests."""

    def test_sequential_adapter_success_call(self) -> None:
        """TC-126: MCP adapter call tool success."""
        mock_http = MagicMock()
        mock_http.post_json.return_value = {"result": "ok"}

        adapter = SequentialThinkingMCPAdapter("http://localhost:3000", http_client=mock_http)
        res = adapter.call_tool("sequentialthinking", {})

        assert res["success"] is True
        assert res["output"] == {"result": "ok"}
        mock_http.post_json.assert_called_once()

    def test_sequential_adapter_is_connected_success(self) -> None:
        """TC-127: MCP adapter connection check."""
        mock_http = MagicMock()
        mock_http.is_reachable.return_value = True

        adapter = SequentialThinkingMCPAdapter("http://localhost:3000", http_client=mock_http)
        assert adapter.is_connected() is True
        mock_http.is_reachable.assert_called_once_with("http://localhost:3000")

    def test_sequential_adapter_call_tool_http_error(self) -> None:
        """TC-128: MCP adapter call_tool exception path returns success=False."""
        mock_http = MagicMock()
        mock_http.post_json.side_effect = ConnectionError("connection refused")

        adapter = SequentialThinkingMCPAdapter("http://localhost:3000", http_client=mock_http)
        res = adapter.call_tool("sequentialthinking", {})

        assert res["success"] is False
        assert "connection refused" in res["output"]
