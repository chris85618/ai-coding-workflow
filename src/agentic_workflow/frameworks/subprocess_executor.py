"""Concrete OS Subprocess Executor implementation.

Implements: SubprocessExecutor interface defined in adapters/subprocess.py
Traceable to: FEA-011, UC-013, INV-020
"""

from __future__ import annotations

import shlex
import subprocess

from agentic_workflow.adapters.subprocess import SubprocessExecutor


class OSSubprocessExecutorMapper(SubprocessExecutor):
    """Concrete subprocess execution implementation of SubprocessExecutor port using Python subprocess module."""

    @staticmethod
    def _handle_run_error(exc: Exception, timeout: int, cmd: list[str]) -> tuple[int, str, str]:
        """Handle command timeouts or file-not-found exceptions."""
        msg = f"Command not found: {cmd[0]!r}"
        if isinstance(exc, subprocess.TimeoutExpired):
            msg = f"Command timed out after {timeout} seconds"
        return 1, "", msg

    @staticmethod
    def _execute_run(cmd: list[str], cwd: str | None, timeout: int) -> subprocess.CompletedProcess[str]:
        """Execute the command in a subprocess."""
        return subprocess.run(cmd, shell=False, capture_output=True, text=True, cwd=cwd, timeout=timeout)

    def run_cmd(self, cmd: str) -> tuple[int, str, str]:
        """Execute a command via subprocess."""
        res = None
        try:
            res = self.run_cmd_list(shlex.split(cmd))
        except ValueError as exc:
            res = (1, "", f"Invalid hook command syntax: {exc}")
        return res

    def run_cmd_list(
        self,
        cmd: list[str],
        cwd: str | None = None,
        timeout: int = 30,
    ) -> tuple[int, str, str]:
        """Execute a command list with optional working directory."""
        try:
            proc = self._execute_run(cmd, cwd, timeout)
            res = (proc.returncode, proc.stdout, proc.stderr)
        except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
            res = self._handle_run_error(exc, timeout, cmd)
        return res


# Backward compatibility facades
OSSubprocessExecutor = OSSubprocessExecutorMapper
