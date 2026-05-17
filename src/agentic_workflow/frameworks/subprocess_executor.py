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

        try:
            proc = subprocess.run(
                cmd_list,
                shell=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Hook timed out after 30 seconds"
        except FileNotFoundError:
            return 1, "", f"Hook command not found: {cmd_list[0]!r}"
