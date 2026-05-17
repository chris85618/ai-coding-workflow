"""Tests for UrllibHttpClient concrete implementation (frameworks/mcp/urllib_http_client.py).

Traceable to: FR-028, ADR-STR-004, ADR-STR-027.
All network I/O is mocked via unittest.mock.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from agentic_workflow.frameworks.mcp.urllib_http_client import UrllibHttpClient


class TestUrllibHttpClientPostJson:
    """Tests for UrllibHttpClient.post_json."""

    def _make_client(self) -> UrllibHttpClient:
        return UrllibHttpClient()

    def test_post_json_success(self) -> None:
        """post_json returns parsed dict on success."""
        client = self._make_client()
        response_data = {"result": "ok"}
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(response_data).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = client.post_json("https://example.com", {"key": "value"})

        assert result == {"result": "ok"}

    def test_post_json_url_error_raises_runtime_error(self) -> None:
        """post_json wraps urllib.error.URLError in RuntimeError."""
        import urllib.error

        client = self._make_client()
        with (
            patch("urllib.request.urlopen", side_effect=urllib.error.URLError("connection refused")),
            pytest.raises(RuntimeError, match="HTTP POST to"),
        ):
            client.post_json("https://example.com", {})

    def test_post_json_os_error_raises_runtime_error(self) -> None:
        """post_json wraps OSError in RuntimeError."""
        client = self._make_client()
        with (
            patch("urllib.request.urlopen", side_effect=OSError("timeout")),
            pytest.raises(RuntimeError, match="HTTP POST to"),
        ):
            client.post_json("https://example.com", {})


class TestUrllibHttpClientIsReachable:
    """Tests for UrllibHttpClient.is_reachable."""

    def _make_client(self) -> UrllibHttpClient:
        return UrllibHttpClient()

    def test_is_reachable_returns_true_on_success(self) -> None:
        """is_reachable returns True when urlopen succeeds."""
        client = self._make_client()
        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            assert client.is_reachable("https://example.com") is True

    def test_is_reachable_returns_false_on_error(self) -> None:
        """is_reachable returns False on any exception."""
        client = self._make_client()
        with patch("urllib.request.urlopen", side_effect=Exception("unreachable")):
            assert client.is_reachable("https://example.com") is False
