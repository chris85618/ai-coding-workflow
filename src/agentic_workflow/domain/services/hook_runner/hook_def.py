"""HookDef — Definition of a single lifecycle hook.

Traceable to: FEA-011, UC-013, INV-020, EVT-008
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_workflow.domain.models.enums.hook_event import HookEvent


@dataclass(frozen=True)
class HookDef:
    """Definition of a single lifecycle hook.

    Attributes:
        event: The lifecycle event this hook fires on.
        command: Shell command to execute.
        blocking: If True, exit_code 2 blocks pipeline progression.
        matcher: Optional regex pattern to filter when hook applies.
    """

    event: HookEvent
    command: str
    blocking: bool = True
    matcher: str = ""
