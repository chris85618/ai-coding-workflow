"""Persistence Adapter — Hook Configuration Loader.

Loads HookDef objects from a YAML or JSON configuration file.
Traceable to: CLS-016 (HookRunner), FEA-011, UC-013
Configuration format follows Claude Code hook patterns (ADR-STR-004).
"""

from __future__ import annotations

import json
from pathlib import Path

from agentic_workflow.domain.models.enums import HookEvent
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

    def __init__(self, config_path: str) -> None:
        self._path = Path(config_path)

    def load(self) -> list[HookDef]:
        """Parse and return hook definitions from the config file.

        Returns:
            List of HookDef objects ready for registration.

        Raises:
            FileNotFoundError: If the config file does not exist.
            KeyError: If a hook entry references an unknown event name.
            json.JSONDecodeError: If the file contains invalid JSON.
        """
        raw = json.loads(self._path.read_text(encoding="utf-8"))
        hooks: list[HookDef] = []
        for entry in raw.get("hooks", []):
            hooks.append(
                HookDef(
                    event=HookEvent(entry["event"]),
                    command=entry["command"],
                    blocking=entry.get("blocking", True),
                    matcher=entry.get("matcher", ""),
                )
            )
        return hooks

    @staticmethod
    def from_dict(config: dict) -> list[HookDef]:
        """Parse hook definitions from a dictionary (no file I/O).

        Useful for testing or inline configuration.

        Args:
            config: Dictionary with a ``"hooks"`` key containing hook entries.

        Returns:
            List of HookDef objects.
        """
        hooks: list[HookDef] = []
        for entry in config.get("hooks", []):
            hooks.append(
                HookDef(
                    event=HookEvent(entry["event"]),
                    command=entry["command"],
                    blocking=entry.get("blocking", True),
                    matcher=entry.get("matcher", ""),
                )
            )
        return hooks
