"""Concrete OS Subprocess Executor implementation.

Implements: SubprocessExecutor interface defined in adapters/subprocess.py
Traceable to: FEA-011, UC-013, INV-020
"""

from __future__ import annotations

import shlex
import subprocess

from agentic_workflow.adapters.subprocess import SubprocessExecutor


class OSSubprocessExecutor(SubprocessExecutor):
    """Concrete subprocess execution implementation of SubprocessExecutor port using Python subprocess module."""

    def run_cmd(self, cmd: str) -> tuple[int, str, str]:
        """Execute a command via subprocess."""
        try:
            cmd_list = shlex.split(cmd)
        except ValueError as exc:
            return 1, "", f"Invalid hook command syntax: {exc}"

        return self.run_cmd_list(cmd_list)

    def run_cmd_list(
        self,
        cmd: list[str],
        cwd: str | None = None,
        timeout: int = 30,
    ) -> tuple[int, str, str]:
        """Execute a command list with optional working directory."""
        try:
            proc = subprocess.run(
                cmd,
                shell=False,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=timeout,
            )
            return proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired:
            return 1, "", f"Command timed out after {timeout} seconds"
        except FileNotFoundError:
            return 1, "", f"Command not found: {cmd[0]!r}"
