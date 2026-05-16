"""HookResult — Result of a single hook execution.

Traceable to: FEA-011, UC-013, INV-020, EVT-008
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_workflow.domain.services.hook_runner.hook_def import HookDef


@dataclass(frozen=True)
class HookResult:
    """Result of a single hook execution.

    Attributes:
        hook_def: The hook that was executed.
        exit_code: Process exit code.
        stdout: Captured standard output.
        stderr: Captured standard error.
        proceed: Whether pipeline should continue.
    """

    hook_def: HookDef
    exit_code: int
    stdout: str
    stderr: str
    proceed: bool
