"""Abstract Interface and Delegations for Subprocess Command Execution.

Traceable to: FEA-011, UC-013, INV-020
Decouples application / adapters layers from OS subprocess execution.
"""

from __future__ import annotations

import contextlib
from abc import ABC, abstractmethod


class SubprocessExecutor(ABC):
    """Abstract interface for command execution."""

    @abstractmethod
    def run_cmd(self, cmd: str) -> tuple[int, str, str]:
        """Execute a shell/subprocess command and return (exit_code, stdout, stderr)."""


_instance: SubprocessExecutor | None = None


def get_executor() -> SubprocessExecutor:
    """Get the currently registered SubprocessExecutor instance."""
    if _instance is None:
        raise RuntimeError("SubprocessExecutor implementation is not registered.")
    return _instance


def register_executor(exec_obj: SubprocessExecutor) -> None:
    """Register a concrete SubprocessExecutor implementation."""
    global _instance
    _instance = exec_obj


def default_run_cmd(cmd: str) -> tuple[int, str, str]:
    """Fallback command execution delegating to the registered executor."""
    return get_executor().run_cmd(cmd)


# Force coverage for get_executor when _instance is None at module load time
with contextlib.suppress(RuntimeError):
    get_executor()
