"""Cover missing branches in CLS-016."""

from agentic_workflow.domain.models.enums import HookEvent
from agentic_workflow.domain.services.hook_runner import HookDef, HookRunner


class TestHookRunnerBranches:
    """Cover missing branches in CLS-016."""

    def test_empty_event_returns_empty(self) -> None:
        """No hooks for event returns empty list."""
        runner = HookRunner()
        results = runner.execute(HookEvent.PRE_STAGE_START)
        assert results == []

    def test_all_proceeded_false(self) -> None:
        """all_proceeded returns False if any hook blocked."""
        runner = HookRunner()
        hook = HookDef(
            event=HookEvent.PRE_STAGE_START,
            command='python -c "exit(2)"',
            blocking=True,
        )
        runner.register(hook)
        results = runner.execute(HookEvent.PRE_STAGE_START)
        assert runner.all_proceeded(results) is False

    def test_non_blocking_hook_exit2_proceeds(self) -> None:
        """Non-blocking hook with exit 2 still proceeds."""
        runner = HookRunner()
        hook = HookDef(
            event=HookEvent.PRE_STAGE_START,
            command='python -c "exit(2)"',
            blocking=False,
        )
        runner.register(hook)
        results = runner.execute(HookEvent.PRE_STAGE_START)
        assert results[0].proceed is True

    def test_exit_code_other_than_0_2_proceeds(self) -> None:
        """Exit code 1 (non-blocking kind) still proceeds."""
        runner = HookRunner()
        hook = HookDef(
            event=HookEvent.PRE_STAGE_START,
            command='python -c "exit(1)"',
            blocking=True,
        )
        runner.register(hook)
        results = runner.execute(HookEvent.PRE_STAGE_START)
        assert results[0].proceed is True

    def test_all_proceeded_true(self) -> None:
        """all_proceeded True when all hooks pass."""
        runner = HookRunner()
        hook = HookDef(
            event=HookEvent.PRE_STAGE_START,
            command='python -c "exit(0)"',
            blocking=True,
        )
        runner.register(hook)
        results = runner.execute(HookEvent.PRE_STAGE_START)
        assert runner.all_proceeded(results) is True
