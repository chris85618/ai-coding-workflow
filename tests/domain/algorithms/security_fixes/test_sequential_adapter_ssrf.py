"""Verify SSRF protection in SequentialThinkingMCPAdapter (SEC-004)."""

import pytest

from agentic_workflow.adapters.mcp.sequential_adapter import SequentialThinkingMCPAdapter


class TestSequentialAdapterSSRF:
    """Verify SSRF protection in SequentialThinkingMCPAdapter (SEC-004)."""

    def test_localhost_http_allowed(self) -> None:
        """Verify localhost HTTP is allowed."""
        adapter = SequentialThinkingMCPAdapter(server_url="http://localhost:3000")
        assert adapter is not None

    def test_127_http_allowed(self) -> None:
        """Verify 127.0.0.1 HTTP is allowed."""
        adapter = SequentialThinkingMCPAdapter(server_url="http://127.0.0.1:9000")
        assert adapter is not None

    def test_https_remote_allowed(self) -> None:
        """Verify HTTPS remote is allowed."""
        adapter = SequentialThinkingMCPAdapter(server_url="https://mcp.example.com")
        assert adapter is not None

    def test_http_remote_rejected(self) -> None:
        """Verify HTTP remote is rejected."""
        with pytest.raises(ValueError, match="SEC-004"):
            SequentialThinkingMCPAdapter(server_url="http://evil.com/steal")

    def test_file_scheme_rejected(self) -> None:
        """Verify file scheme is rejected."""
        with pytest.raises(ValueError, match="SEC-004"):
            SequentialThinkingMCPAdapter(server_url="file:///etc/passwd")

    def test_ftp_scheme_rejected(self) -> None:
        """Verify FTP scheme is rejected."""
        with pytest.raises(ValueError, match="SEC-004"):
            SequentialThinkingMCPAdapter(server_url="ftp://attacker.com")
