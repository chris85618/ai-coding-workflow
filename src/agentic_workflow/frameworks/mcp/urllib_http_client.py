"""Concrete urllib-based HTTP client for MCP adapter communication.

Implements: HttpClientPort (adapters/http.py)
Traceable to: FR-028 (MCP tool invocation), ADR-STR-004, ADR-STR-027
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from agentic_workflow.adapters.http import HttpClientPort


class UrllibHttpClientMapper(HttpClientPort):
    """Concrete HTTP client backed by Python's stdlib urllib and json."""

    @staticmethod
    def _make_req(url: str, payload: dict[str, Any]) -> urllib.request.Request:
        """Create a JSON POST request."""
        return urllib.request.Request(
            url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST"
        )

    @staticmethod
    def _send_req(req: urllib.request.Request, url: str) -> dict[str, Any]:
        """Send HTTP request and decode JSON response."""
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                res = dict(json.loads(resp.read()))
        except OSError as exc:
            raise RuntimeError(f"HTTP POST to {url!r} failed: {exc}") from exc
        return res

    @staticmethod
    def _probe_url(url: str, timeout: int) -> bool:
        """Probe url to check reachability."""
        try:
            with urllib.request.urlopen(urllib.request.Request(url, method="GET"), timeout=timeout):
                res = True
        except Exception:
            res = False
        return res

    def post_json(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        """POST a JSON payload and return the parsed response.

        Args:
            url: Target URL.
            payload: Python dict sent as JSON body.

        Returns:
            Parsed JSON response dict.

        Raises:
            RuntimeError: On any network or decoding error.
        """
        return self._send_req(self._make_req(url, payload), url)

    def is_reachable(self, url: str, timeout: int = 3) -> bool:
        """Check if a URL responds to a GET request.

        Args:
            url: Target URL to probe.
            timeout: Maximum wait time in seconds.

        Returns:
            True if reachable, False on any error.
        """
        return self._probe_url(url, timeout)


# Backward compatibility facades
UrllibHttpClient = UrllibHttpClientMapper
