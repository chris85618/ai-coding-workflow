"""Tests for SubprocessExecutor port and registry (ADR-STR-027 DIP)."""

from __future__ import annotations

import pytest


class TestSubprocessRegistry:
    """Coverage for adapters.subprocess registry functions."""

    def test_get_executor_raises_when_unregistered(self) -> None:
        """Line 35: RuntimeError when no executor is registered."""
        from agentic_workflow.adapters import subprocess as sub_mod

        original = sub_mod._instance
        sub_mod._instance = None
        try:
            with pytest.raises(RuntimeError, match="SubprocessExecutor implementation is not registered"):
                sub_mod.get_executor()
        finally:
            sub_mod._instance = original
