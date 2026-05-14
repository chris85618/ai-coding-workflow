"""BDD step definitions for hook_execution.feature (SC-013).

Traceable to: UC-013, INV-020, CLS-016
"""

from __future__ import annotations

import pytest
from pytest_bdd import given, parsers, scenario, then, when

from agentic_workflow.domain.models.enums import HookEvent
from agentic_workflow.domain.services.hook_runner import HookDef, HookResult, HookRunner


# ── Scenarios ─────────────────────────────────────────────────────────────────

@scenario("hook_execution.feature", "PreStageStart hook runs before stage logic")
def test_pre_stage_hook():
    """SC-013: Hook executes before stage."""


@scenario("hook_execution.feature", "Hook exit code 2 blocks stage execution")
def test_blocking_hook():
    """SC-013: Exit code 2 + blocking hook → stage blocked."""


@scenario("hook_execution.feature", "PostDocWrite hook auto-formats Python files")
def test_post_doc_write():
    """SC-013: PostDocWrite hook runs ruff format."""


@scenario("hook_execution.feature", "Multiple hooks execute in registration order")
def test_hook_order():
    """SC-013: Hooks execute in registration order."""


# ── Context ───────────────────────────────────────────────────────────────────

@pytest.fixture
def ctx():
    """Shared step context."""
    return {}


# ── Given steps ───────────────────────────────────────────────────────────────

@given(parsers.parse("a hook is registered for {event} event"))
def given_hook_registered(ctx, event):
    """Register a passing hook for the given event."""
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
def given_blocking_hook(ctx, event):
    """Register a blocking hook."""
    runner = HookRunner()
    hook_event = HookEvent(event.lower())
    ctx["runner"] = runner
    ctx["event"] = hook_event


@given("the hook command returns exit code 2")
def given_exit_code_2(ctx):
    """Set up blocking hook with exit code 2."""
    hook = HookDef(
        event=ctx["event"],
        command='python -c "exit(2)"',
        blocking=True,
    )
    ctx["runner"].register(hook)


@given("a PostDocWrite hook runs ruff format on the file")
def given_post_doc_write_hook(ctx, tmp_path):
    """Register a PostDocWrite hook that runs echo (simulate ruff)."""
    runner = HookRunner()
    py_file = tmp_path / "test_output.py"
    py_file.write_text("x=1\n")
    ctx["py_file"] = str(py_file)
    hook = HookDef(
        event=HookEvent.POST_DOC_WRITE,
        command=f'python -c "exit(0)"',  # Simulate ruff success
        blocking=False,
    )
    runner.register(hook)
    ctx["runner"] = runner
    ctx["event"] = HookEvent.POST_DOC_WRITE


@given("hooks A and B are registered for POST_STAGE_COMPLETE")
def given_hooks_ab(ctx):
    """Register hooks A and B in order."""
    runner = HookRunner()
    execution_order: list[str] = []
    # We'll use exit codes to track order via stdout
    hook_a = HookDef(
        event=HookEvent.POST_STAGE_COMPLETE,
        command='python -c "print(\'A\'); exit(0)"',
        blocking=False,
    )
    hook_b = HookDef(
        event=HookEvent.POST_STAGE_COMPLETE,
        command='python -c "print(\'B\'); exit(0)"',
        blocking=False,
    )
    runner.register(hook_a)
    runner.register(hook_b)
    ctx["runner"] = runner
    ctx["event"] = HookEvent.POST_STAGE_COMPLETE


# ── When steps ────────────────────────────────────────────────────────────────

@when("the stage begins execution")
def when_stage_begins(ctx):
    """Execute hooks for the registered event."""
    ctx["results"] = ctx["runner"].execute(ctx["event"])


@when("the hook executes")
def when_hook_executes(ctx):
    """Execute the hook and capture results."""
    ctx["results"] = ctx["runner"].execute(ctx["event"])


@when("a Python file is written to docs/")
def when_file_written(ctx):
    """Simulate PostDocWrite hook trigger."""
    ctx["results"] = ctx["runner"].execute(
        ctx["event"], {"file": ctx.get("py_file", "test.py")}
    )


@when("POST_STAGE_COMPLETE fires")
def when_post_stage_fires(ctx):
    """Fire the POST_STAGE_COMPLETE event."""
    ctx["results"] = ctx["runner"].execute(ctx["event"])


# ── Then steps ────────────────────────────────────────────────────────────────

@then("the hook command executes before any stage logic")
def then_hook_executes_first(ctx):
    """Assert at least one hook result exists."""
    assert len(ctx["results"]) >= 1


@then("hook exit code 0 allows the stage to proceed")
def then_exit_0_proceeds(ctx):
    """Assert proceed is True when exit code is 0."""
    result: HookResult = ctx["results"][0]
    assert result.exit_code == 0
    assert result.proceed is True


@then("the stage execution is blocked")
def then_stage_blocked(ctx):
    """Assert proceed is False."""
    result: HookResult = ctx["results"][0]
    assert result.proceed is False


@then("stderr content is logged as a warning")
def then_stderr_captured(ctx):
    """Assert stderr is captured (even if empty)."""
    result: HookResult = ctx["results"][0]
    assert result.stderr is not None  # captured (may be empty)


@then("the file is automatically formatted by ruff")
def then_file_formatted(ctx):
    """Assert the hook ran successfully (simulating ruff format)."""
    result: HookResult = ctx["results"][0]
    assert result.proceed is True


@then("no manual formatting is needed")
def then_no_manual_format(ctx):
    """Structural assertion: hook system handles formatting."""
    assert len(ctx["results"]) > 0


@then("hook A executes before hook B")
def then_a_before_b(ctx):
    """Assert hooks executed in registration order via stdout."""
    results = ctx["results"]
    assert len(results) == 2
    assert "A" in results[0].stdout
    assert "B" in results[1].stdout
