"""Persistence Adapter — Hook Configuration Loader.

Loads HookDef objects from a YAML or JSON configuration file.
Traceable to: CLS-016 (HookRunner), FEA-011, UC-013
Configuration format follows Claude Code hook patterns (ADR-STR-004).
"""

from __future__ import annotations

import json
from typing import Any

from agentic_workflow.adapters.filesystem import get_filesystem
from agentic_workflow.domain.enums import HookEvent
from agentic_workflow.domain.services.hook_runner import HookDef


class HookConfigLoader:
    """Loads hook definitions from a JSON configuration file.

    Configuration file format (JSON):

    .. code-block:: json

        {
          "hooks": [
            {
              "event": "pre_stage_start",
              "command": "echo {stage}",
              "blocking": true,
              "matcher": ""
            }
          ]
        }

    Args:
        config_path: Path to the hook configuration file.
    """

    @staticmethod
    def _parse_entry(entry: dict[str, Any]) -> HookDef:
        """Parse dictionary entry to HookDef object."""
        evt, cmd = HookEvent(entry["event"]), entry["command"]
        blk, mat = entry.get("blocking", True), entry.get("matcher", "")
        return HookDef(event=evt, command=cmd, blocking=blk, matcher=mat)

    def __init__(self, config_path: str) -> None:
        """Initializes the hook configuration loader.

        Args:
            config_path: Path to the hook configuration file.
        """
        self._fs = get_filesystem()
        self._path = self._fs.resolve_path(config_path)

    def load(self) -> list[HookDef]:
        """Parse and return hook definitions from the config file.

        Returns:
            List of HookDef objects ready for registration.

        Raises:
            FileNotFoundError: If the config file does not exist.
            KeyError: If a hook entry references an unknown event name.
            json.JSONDecodeError: If the file contains invalid JSON.
        """
        raw = json.loads(self._fs.read_text(self._path, encoding="utf-8"))
        return [self._parse_entry(e) for e in raw.get("hooks", [])]

    @staticmethod
    def from_dict(config: dict[str, Any]) -> list[HookDef]:
        """Parse hook definitions from a dictionary (no file I/O).

        Useful for testing or inline configuration.

        Args:
            config: Dictionary with a ``"hooks"`` key containing hook entries.

        Returns:
            List of HookDef objects.
        """
        return [HookConfigLoader._parse_entry(e) for e in config.get("hooks", [])]
