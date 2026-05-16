"""TC-126, TC-127: SequentialThinkingMCPAdapter tests."""

from unittest.mock import MagicMock, patch

from agentic_workflow.adapters.mcp.sequential_adapter import (
    SequentialThinkingMCPAdapter,
)


class TestSequentialThinkingMCPAdapter:
    """TC-126, TC-127: MCP adapter tests."""

    def test_sequential_adapter_success_call(self) -> None:
        """TC-126: MCP adapter call tool success."""
        adapter = SequentialThinkingMCPAdapter("http://localhost:3000")
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = b'{"result": "ok"}'
            mock_urlopen.return_value.__enter__.return_value = mock_resp

            res = adapter.call_tool("sequentialthinking", {})
            assert res["success"] is True
            assert res["output"] == {"result": "ok"}

    def test_sequential_adapter_is_connected_success(self) -> None:
        """TC-127: MCP adapter connection check."""
        adapter = SequentialThinkingMCPAdapter("http://localhost:3000")
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_urlopen.return_value.__enter__.return_value = mock_resp
            assert adapter.is_connected() is True
