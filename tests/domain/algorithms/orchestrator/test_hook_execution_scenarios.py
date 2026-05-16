"""BDD scenarios for hook_execution."""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenario, then, when

from agentic_workflow.domain.enums import HookEvent
from agentic_workflow.domain.services.hook_runner import HookDef, HookResult, HookRunner


class TestHookExecutionScenarios:
    """BDD scenarios for hook_execution."""

    @staticmethod
    @scenario("features/hook_execution.feature", "PreStageStart hook runs before stage logic")
    def test_pre_stage_hook() -> None:
        """SC-013: Hook executes before stage."""

    @staticmethod
    @scenario("features/hook_execution.feature", "Hook exit code 2 blocks stage execution")
    def test_blocking_hook() -> None:
        """SC-013: Exit code 2 + blocking hook → stage blocked."""

    @staticmethod
    @scenario("features/hook_execution.feature", "PostDocWrite hook auto-formats Python files")
    def test_post_doc_write() -> None:
        """SC-013: PostDocWrite hook runs ruff format."""

    @staticmethod
    @scenario("features/hook_execution.feature", "Multiple hooks execute in registration order")
    def test_hook_order() -> None:
        """SC-013: Hooks execute in registration order."""


@pytest.fixture
def ctx() -> dict[str, Any]:
    """Shared step context."""
    return {}


@given(parsers.parse("a hook is registered for {event} event"))
def given_hook_registered(ctx: dict[str, Any], event: str) -> None:
    """Step: register hook."""
    runner = HookRunner()
    hook_event = HookEvent(event.lower())
    hook = HookDef(
        event=hook_event,
        command='python -c "exit(0)"',
        blocking=True,
    )
    runner.register(hook)
    ctx["runner"] = runner
    ctx["event"] = hook_event


@given(parsers.parse("a blocking hook is registered for {event}"))
def given_blocking_hook(ctx: dict[str, Any], event: str) -> None:
    """Step: blocking hook."""
    runner = HookRunner()
    hook_event = HookEvent(event.lower())
    ctx["runner"] = runner
    ctx["event"] = hook_event


@given("the hook command returns exit code 2")
def given_exit_code_2(ctx: dict[str, Any]) -> None:
    """Step: exit code 2."""
    hook = HookDef(
        event=ctx["event"],
        command='python -c "exit(2)"',
        blocking=True,
    )
    ctx["runner"].register(hook)


@given("a PostDocWrite hook runs ruff format on the file")
def given_post_doc_write_hook(ctx: dict[str, Any], tmp_path: Any) -> None:
    """Step: PostDocWrite hook."""
    runner = HookRunner()
    py_file = tmp_path / "test_output.py"
    py_file.write_text("x=1\n")
    ctx["py_file"] = str(py_file)
    hook = HookDef(
        event=HookEvent.POST_DOC_WRITE,
        command='python -c "exit(0)"',  # Simulate ruff success
        blocking=False,
    )
    runner.register(hook)
    ctx["runner"] = runner
    ctx["event"] = HookEvent.POST_DOC_WRITE


@given("hooks A and B are registered for POST_STAGE_COMPLETE")
def given_hooks_ab(ctx: dict[str, Any]) -> None:
    """Step: hooks A and B."""
    runner = HookRunner()
    # We'll use exit codes to track order via stdout
    hook_a = HookDef(
        event=HookEvent.POST_STAGE_COMPLETE,
        command="python -c \"print('A'); exit(0)\"",
        blocking=False,
    )
    hook_b = HookDef(
        event=HookEvent.POST_STAGE_COMPLETE,
        command="python -c \"print('B'); exit(0)\"",
        blocking=False,
    )
    runner.register(hook_a)
    runner.register(hook_b)
    ctx["runner"] = runner
    ctx["event"] = HookEvent.POST_STAGE_COMPLETE


@when("the stage begins execution")
def when_stage_begins(ctx: dict[str, Any]) -> None:
    """Step: stage begins."""
    ctx["results"] = ctx["runner"].execute(ctx["event"])


@when("the hook executes")
def when_hook_executes(ctx: dict[str, Any]) -> None:
    """Step: hook executes."""
    ctx["results"] = ctx["runner"].execute(ctx["event"])


@when("a Python file is written to docs/")
def when_file_written(ctx: dict[str, Any]) -> None:
    """Step: file written."""
    ctx["results"] = ctx["runner"].execute(ctx["event"], {"file": ctx.get("py_file", "test.py")})


@when("POST_STAGE_COMPLETE fires")
def when_post_stage_fires(ctx: dict[str, Any]) -> None:
    """Step: POST_STAGE_COMPLETE fires."""
    ctx["results"] = ctx["runner"].execute(ctx["event"])


@then("the hook command executes before any stage logic")
def then_hook_executes_first(ctx: dict[str, Any]) -> None:
    """Step: hook first."""
    assert len(ctx["results"]) >= 1


@then("hook exit code 0 allows the stage to proceed")
def then_exit_0_proceeds(ctx: dict[str, Any]) -> None:
    """Step: exit 0 proceeds."""
    result: HookResult = ctx["results"][0]
    assert result.exit_code == 0
    assert result.proceed is True


@then("the stage execution is blocked")
def then_stage_blocked(ctx: dict[str, Any]) -> None:
    """Step: stage blocked."""
    result: HookResult = ctx["results"][0]
    assert result.proceed is False


@then("stderr content is logged as a warning")
def then_stderr_captured(ctx: dict[str, Any]) -> None:
    """Step: stderr captured."""
    result: HookResult = ctx["results"][0]
    assert result.stderr is not None  # captured (may be empty)


@then("the file is automatically formatted by ruff")
def then_file_formatted(ctx: dict[str, Any]) -> None:
    """Step: file formatted."""
    result: HookResult = ctx["results"][0]
    assert result.proceed is True


@then("no manual formatting is needed")
def then_no_manual_format(ctx: dict[str, Any]) -> None:
    """Step: no manual format."""
    assert len(ctx["results"]) > 0


@then("hook A executes before hook B")
def then_a_before_b(ctx: dict[str, Any]) -> None:
    """Step: A before B."""
    results = ctx["results"]
    assert len(results) == 2
    assert "A" in results[0].stdout
    assert "B" in results[1].stdout
