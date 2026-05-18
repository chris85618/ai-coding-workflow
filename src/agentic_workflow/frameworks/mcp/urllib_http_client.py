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


class UrllibHttpClient(HttpClientPort):
    """Concrete HTTP client backed by Python's stdlib urllib and json."""

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
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return dict(json.loads(resp.read()))
        except OSError as exc:
            raise RuntimeError(f"HTTP POST to {url!r} failed: {exc}") from exc

    def is_reachable(self, url: str, timeout: int = 3) -> bool:
        """Check if a URL responds to a GET request.

        Args:
            url: Target URL to probe.
            timeout: Maximum wait time in seconds.

        Returns:
            True if reachable, False on any error.
        """
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=timeout):
                return True
        except Exception:
            return False
