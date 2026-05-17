"""HTTP Client Port — Abstract interface for HTTP JSON calls.

Decouples adapters layer from urllib/requests implementation.
Traceable to: ADR-STR-027 (DIP enforcement), FR-028 (MCP tool invocation)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class HttpClientPort(ABC):
    """Abstract HTTP client for JSON RPC calls."""

    @abstractmethod
    def post_json(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        """POST a JSON payload to the given URL and return the parsed response.

        Args:
            url: Target URL.
            payload: Python dict to send as JSON body.

        Returns:
            Parsed JSON response dict.

        Raises:
            RuntimeError: On network or HTTP error.
        """

    @abstractmethod
    def is_reachable(self, url: str, timeout: int = 3) -> bool:
        """Check if a URL is reachable via GET request.

        Args:
            url: Target URL to probe.
            timeout: Maximum seconds to wait.

        Returns:
            True if the URL responds, False otherwise.
        """
