"""Frameworks Layer — Git implementation of the version-control gateway.

Traceable to: FR-069, ADR-STR-029
Thin git wrapper over the registered SubprocessExecutor (DIP, ADR-STR-027).
"""

from __future__ import annotations

from agentic_workflow.adapters.subprocess import get_executor
from agentic_workflow.application.ports.gateways.version_control_gateway import (
    IVersionControlGateway,
)

_UNIVERSAL_BASE_TAG = "universal-base"


class GitVersionControl(IVersionControlGateway):
    """Git-backed rollback gateway used by the Pipeline v2 degradation path."""

    def current_ref(self) -> str:
        """Return the current commit reference."""
        _, stdout, _ = get_executor().run_cmd_list(["git", "rev-parse", "HEAD"])
        return stdout.strip()

    def rollback_to(self, ref: str) -> bool:
        """Hard-reset the working tree to ref; True on success."""
        code, _, _ = get_executor().run_cmd_list(["git", "reset", "--hard", ref])
        return code == 0

    def tag_universal_base(self) -> str:
        """Tag the current commit as the universal base and return the tag name."""
        tag = _UNIVERSAL_BASE_TAG
        get_executor().run_cmd_list(["git", "tag", "-f", tag])
        return tag
