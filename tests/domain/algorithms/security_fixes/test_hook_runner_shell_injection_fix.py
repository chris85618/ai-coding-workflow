"""Verify shell=False and shlex.split prevents injection (SEC-001)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from agentic_workflow.domain.models.enums import HookEvent
from agentic_workflow.domain.services.hook_runner import HookDef, HookRunner


class TestHookRunnerShellInjectionFix:
    """Verify shell=False and shlex.split prevents injection (SEC-001)."""

    def _make_runner(self) -> tuple[HookRunner, HookDef]:
        """Create a runner and a hook for testing."""
        runner = HookRunner()
        hook = HookDef(event=HookEvent.PRE_STAGE_START, command="echo {stage}", blocking=False)
        runner.register(hook)
        return runner, hook

    @patch("subprocess.run")
    def test_shell_false_used(self, mock_run: MagicMock) -> None:
        """subprocess.run must be called with shell=False (SEC-001)."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        runner, _ = self._make_runner()
        runner.execute(HookEvent.PRE_STAGE_START, {"stage": "stage3"})
        call_kwargs = mock_run.call_args
        assert call_kwargs.kwargs.get("shell") is False or call_kwargs[1].get("shell") is False

    @patch("subprocess.run")
    def test_metachar_stripped_from_context(self, mock_run: MagicMock) -> None:
        """With shell=False, injected commands are literal strings (SEC-001)."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        runner, _ = self._make_runner()

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
        runner = HookRunner()
        hook = HookDef(event=HookEvent.PRE_STAGE_START, command="echo 'unclosed", blocking=False)
        runner.register(hook)
        results = runner.execute(HookEvent.PRE_STAGE_START, {})
        assert results[0].exit_code == 1
        assert "syntax" in results[0].stderr.lower() or "Invalid" in results[0].stderr

    def test_command_not_found_returns_error(self) -> None:
        """Non-existent binary returns HookResult with exit_code=1."""
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
