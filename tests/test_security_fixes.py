"""Security fix tests — DEBT-004 Layer 1+2+3 audit findings.

SEC-001: shell=True injection fix in hook_runner.py
SEC-002: path traversal fix in markdown_writer.py
SEC-003: path traversal fix in file_repository.py
SEC-004: SSRF URL validation fix in sequential_adapter.py
"""

from __future__ import annotations

import tempfile
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# ===========================================================================
# SEC-001: hook_runner.py — shell injection fix
# ===========================================================================


class TestHookRunnerShellInjectionFix:
    """Verify shell=False and shlex.split prevents injection (SEC-001)."""

    def _make_runner(self) -> tuple[Any, Any]:
        """Create a runner and a hook for testing."""
        from agentic_workflow.domain.models.enums import HookEvent
        from agentic_workflow.domain.services.hook_runner import HookDef, HookRunner

        runner = HookRunner()
        hook = HookDef(event=HookEvent.PRE_STAGE_START, command="echo {stage}", blocking=False)
        runner.register(hook)
        return runner, hook

    @patch("subprocess.run")
    def test_shell_false_used(self, mock_run: MagicMock) -> None:
        """subprocess.run must be called with shell=False (SEC-001)."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        runner, _ = self._make_runner()
        runner.execute(
            __import__("agentic_workflow.domain.models.enums", fromlist=["HookEvent"]).HookEvent.PRE_STAGE_START,
            {"stage": "stage3"},
        )
        call_kwargs = mock_run.call_args
        assert call_kwargs.kwargs.get("shell") is False or call_kwargs[1].get("shell") is False

    @patch("subprocess.run")
    def test_metachar_stripped_from_context(self, mock_run: MagicMock) -> None:
        """With shell=False, injected commands are literal strings (SEC-001).

        e.g., context value 'stage3; rm -rf /' becomes an argument to echo,
        not a shell pipeline. The semicolons and pipes are stripped as an extra
        layer, but the primary protection is shell=False.
        """
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        runner, _ = self._make_runner()
        from agentic_workflow.domain.models.enums import HookEvent

        runner.execute(HookEvent.PRE_STAGE_START, {"stage": "stage3; rm -rf /"})
        call_kwargs = mock_run.call_args
        # Primary assertion: shell must be False regardless of cmd content
        shell_val = call_kwargs.kwargs.get("shell") or (call_kwargs[1].get("shell") if call_kwargs[1] else None)
        assert shell_val is False
        # Secondary: cmd is a list, not a string (shell=False requires list form)
        cmd_arg = call_kwargs[0][0]
        assert isinstance(cmd_arg, list), "Command must be a list with shell=False"

    def test_invalid_command_syntax_returns_error(self) -> None:
        """Malformed command (unclosed quote) returns HookResult with exit_code=1."""
        from agentic_workflow.domain.models.enums import HookEvent
        from agentic_workflow.domain.services.hook_runner import HookDef, HookRunner

        runner = HookRunner()
        hook = HookDef(event=HookEvent.PRE_STAGE_START, command="echo 'unclosed", blocking=False)
        runner.register(hook)
        results = runner.execute(HookEvent.PRE_STAGE_START, {})
        assert results[0].exit_code == 1
        assert "syntax" in results[0].stderr.lower() or "Invalid" in results[0].stderr

    def test_command_not_found_returns_error(self) -> None:
        """Non-existent binary returns HookResult with exit_code=1."""
        from agentic_workflow.domain.models.enums import HookEvent
        from agentic_workflow.domain.services.hook_runner import HookDef, HookRunner

        runner = HookRunner()
        hook = HookDef(
            event=HookEvent.PRE_STAGE_START,
            command="/nonexistent/binary",
            blocking=False,
        )
        runner.register(hook)
        results = runner.execute(HookEvent.PRE_STAGE_START, {})
        assert results[0].exit_code == 1
        assert "not found" in results[0].stderr


# ===========================================================================
# SEC-002: markdown_writer.py — path traversal fix
# ===========================================================================


class TestMarkdownWriterPathTraversal:
    """Verify path traversal protection in MarkdownDocumentIO (SEC-002)."""

    def setup_method(self) -> None:
        """Set up temporary directory and IO for testing."""
        self._tmp = tempfile.mkdtemp()
        from agentic_workflow.adapters.persistence.markdown_writer import (
            MarkdownDocumentIO,
        )

        self.io = MarkdownDocumentIO(repo_root=self._tmp)

    def test_normal_path_works(self) -> None:
        """Verify normal path writing/reading works."""
        self.io.write("docs/test.md", "content")
        assert self.io.read("docs/test.md") == "content"

    def test_traversal_read_raises(self) -> None:
        """Verify path traversal in read is rejected."""
        with pytest.raises(ValueError, match="SEC-002"):
            self.io.read("../../etc/passwd")

    def test_traversal_write_raises(self) -> None:
        """Verify path traversal in write is rejected."""
        with pytest.raises(ValueError, match="SEC-002"):
            self.io.write("../../evil.txt", "malicious")

    def test_traversal_append_raises(self) -> None:
        """Verify path traversal in append is rejected."""
        with pytest.raises(ValueError, match="SEC-002"):
            self.io.append("../../evil.txt", "data")

    def test_traversal_exists_raises(self) -> None:
        """Verify path traversal in exists is rejected."""
        with pytest.raises(ValueError, match="SEC-002"):
            self.io.exists("../../etc/passwd")


# ===========================================================================
# SEC-003: file_repository.py — path traversal fix
# ===========================================================================


class TestFileRepositoryPathTraversal:
    """Verify path traversal protection in FileTraceableIDRepository (SEC-003)."""

    def setup_method(self) -> None:
        """Set up temporary directory and repository for testing."""
        self._tmp = tempfile.mkdtemp()
        from agentic_workflow.adapters.persistence.file_repository import (
            FileTraceableIDRepository,
        )

        self.repo = FileTraceableIDRepository(repo_root=self._tmp)

    def test_normal_id_works(self) -> None:
        """Verify normal ID lookup works."""
        assert self.repo.find_by_id("FR-001") is None  # Not found, but no error

    def test_dotdot_in_id_is_sanitised(self) -> None:
        """.. sequences in ID strings are replaced, not traversed (SEC-003)."""
        # Should not raise; path is sanitised to stay within root
        result = self.repo.find_by_id("../../../etc/passwd")
        assert result is None  # Safe: sanitised path doesn't match any file

    def test_slash_in_id_is_sanitised(self) -> None:
        """Verify slash in ID is sanitised."""
        result = self.repo.find_by_id("FR/001")
        assert result is None


# ===========================================================================
# SEC-004: sequential_adapter.py — SSRF URL validation
# ===========================================================================


class TestSequentialAdapterSSRF:
    """Verify SSRF protection in SequentialThinkingMCPAdapter (SEC-004)."""

    def test_localhost_http_allowed(self) -> None:
        """Verify localhost HTTP is allowed."""
        from agentic_workflow.adapters.mcp.sequential_adapter import (
            SequentialThinkingMCPAdapter,
        )

        # Should not raise
        adapter = SequentialThinkingMCPAdapter(server_url="http://localhost:3000")
        assert adapter is not None

    def test_127_http_allowed(self) -> None:
        """Verify 127.0.0.1 HTTP is allowed."""
        from agentic_workflow.adapters.mcp.sequential_adapter import (
            SequentialThinkingMCPAdapter,
        )

        adapter = SequentialThinkingMCPAdapter(server_url="http://127.0.0.1:9000")
        assert adapter is not None

    def test_https_remote_allowed(self) -> None:
        """Verify HTTPS remote is allowed."""
        from agentic_workflow.adapters.mcp.sequential_adapter import (
            SequentialThinkingMCPAdapter,
        )

        adapter = SequentialThinkingMCPAdapter(server_url="https://mcp.example.com")
        assert adapter is not None

    def test_http_remote_rejected(self) -> None:
        """Verify HTTP remote is rejected."""
        from agentic_workflow.adapters.mcp.sequential_adapter import (
            SequentialThinkingMCPAdapter,
        )

        with pytest.raises(ValueError, match="SEC-004"):
            SequentialThinkingMCPAdapter(server_url="http://evil.com/steal")

    def test_file_scheme_rejected(self) -> None:
        """Verify file scheme is rejected."""
        from agentic_workflow.adapters.mcp.sequential_adapter import (
            SequentialThinkingMCPAdapter,
        )

        with pytest.raises(ValueError, match="SEC-004"):
            SequentialThinkingMCPAdapter(server_url="file:///etc/passwd")

    def test_ftp_scheme_rejected(self) -> None:
        """Verify FTP scheme is rejected."""
        from agentic_workflow.adapters.mcp.sequential_adapter import (
            SequentialThinkingMCPAdapter,
        )

        with pytest.raises(ValueError, match="SEC-004"):
            SequentialThinkingMCPAdapter(server_url="ftp://attacker.com")
