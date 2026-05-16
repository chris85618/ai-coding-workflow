"""Cover the subprocess.TimeoutExpired path (L108-111)."""

from typing import Any

import pytest

from agentic_workflow.domain.enums import HookEvent
from agentic_workflow.domain.services.hook_runner import HookDef, HookRunner


class TestHookRunnerTimeout:
    """Cover the subprocess.TimeoutExpired path (L108-111)."""

    def test_timeout_hook_proceeds(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Timed-out hook gets exit_code=1 ->proceed=True (L108-111)."""
        import subprocess

        def fake_run(*args: Any, **kwargs: Any) -> Any:
            raise subprocess.TimeoutExpired(cmd="fake", timeout=30)

        monkeypatch.setattr(subprocess, "run", fake_run)

        runner = HookRunner()
        hook = HookDef(
            event=HookEvent.PRE_STAGE_START,
            command="sleep 999",
            blocking=True,
        )
        runner.register(hook)
        results = runner.execute(HookEvent.PRE_STAGE_START)
        assert len(results) == 1
        assert results[0].exit_code == 1
        assert "timed out" in results[0].stderr.lower()
        assert results[0].proceed is True
