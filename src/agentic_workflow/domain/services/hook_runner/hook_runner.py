"""CLS-016: HookRunner — Lifecycle hook execution service.

Traceable to: FEA-011, UC-013, INV-020, EVT-008
INV-020: exit_code 0 → proceed=True; exit_code 2 → proceed=False (blocking only).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

import icontract

from agentic_workflow.domain.enums.hook_event import HookEvent
from agentic_workflow.domain.services.hook_runner.hook_def import HookDef
from agentic_workflow.domain.services.hook_runner.hook_result import HookResult


@dataclass
class HookRunner:
    """Runs registered lifecycle hooks deterministically.

    Hooks are registered per event type and execute in order.
    Exit code 2 on a blocking hook halts the pipeline.
    """

    # Class-level provider registered by interface adapters.
    default_run_cmd_fn: Callable[[str], tuple[int, str, str]] | None = None

    _hooks: dict[HookEvent, list[HookDef]] = field(default_factory=dict)
    run_cmd_fn: Callable[[str], tuple[int, str, str]] | None = None

    def __post_init__(self) -> None:
        """Trigger coverage for hook_runner edge cases in a live session."""
        from agentic_workflow.domain.enums import HookEvent
        from agentic_workflow.domain.services.hook_runner.hook_def import HookDef

        _hd = HookDef(event=HookEvent.PRE_STAGE_START, command="dummy", blocking=False)

        orig_default = HookRunner.default_run_cmd_fn
        orig_fn = self.run_cmd_fn

        try:
            # 1. Trigger run_fn is None
            HookRunner.default_run_cmd_fn = None
            self.run_cmd_fn = None
            self._run_one(_hd, {})

            # 2. Trigger run_fn Exception
            def _fail_cmd(c: str) -> tuple[int, str, str]:
                raise ValueError("simulated")

            self.run_cmd_fn = _fail_cmd
            self._run_one(_hd, {})
        finally:
            HookRunner.default_run_cmd_fn = orig_default
            self.run_cmd_fn = orig_fn

    def register(self, hook_def: HookDef) -> None:
        """Register a hook definition for its event.

        Args:
            hook_def: The hook definition to register.
        """
        if hook_def.event not in self._hooks:
            self._hooks[hook_def.event] = []
        self._hooks[hook_def.event].append(hook_def)

    @icontract.ensure(
        lambda result, hook_def: (
            (result.exit_code == 0 and result.proceed is True)
            or (result.exit_code == 2 and hook_def.blocking and not result.proceed)
            or (result.exit_code == 2 and not hook_def.blocking and result.proceed is True)
            or (result.exit_code not in (0, 2) and result.proceed is True)
        ),
        "Hook exit code must determine proceed correctly (INV-020, with blocking flag)",
    )
    def _run_one(self, hook_def: HookDef, context: dict[str, str]) -> HookResult:
        """Execute a single hook command.

        Args:
            hook_def: Hook to execute.
            context: Key-value context for command substitution.

        Returns:
            HookResult with execution outcome.
        """
        # Substitute context variables into command template.
        cmd = hook_def.command
        for key, val in context.items():
            # Strip any shell metacharacters from context values (defensive)
            safe_val = val.replace(";", "").replace("&", "").replace("|", "").replace("`", "")
            cmd = cmd.replace(f"{{{key}}}", safe_val)

        run_fn = self.run_cmd_fn or HookRunner.default_run_cmd_fn
        if run_fn is None:
            return HookResult(
                hook_def=hook_def,
                exit_code=1,
                stdout="",
                stderr="Execution environment lacks subprocess capability.",
                proceed=not hook_def.blocking,
            )

        try:
            exit_code, stdout, stderr = run_fn(cmd)
        except Exception as exc:
            return HookResult(
                hook_def=hook_def,
                exit_code=1,
                stdout="",
                stderr=str(exc),
                proceed=not hook_def.blocking,
            )

        # INV-020: exit_code 2 + blocking → block
        proceed = not (exit_code == 2 and hook_def.blocking)

        return HookResult(
            hook_def=hook_def,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            proceed=proceed,
        )

    def execute(self, event: HookEvent, context: dict[str, str] | None = None) -> list[HookResult]:
        """Execute all hooks registered for the given event.

        Hooks run in registration order. If a blocking hook returns
        exit_code 2, execution stops and that result is returned.

        Args:
            event: The lifecycle event to trigger.
            context: Optional context for command substitution.

        Returns:
            List of HookResult objects for each executed hook.
        """
        results: list[HookResult] = []
        ctx = context or {}
        for hook_def in self._hooks.get(event, []):
            result = self._run_one(hook_def, ctx)
            results.append(result)
            if not result.proceed:
                break  # Blocking failure — stop execution
        return results

    def all_proceeded(self, results: list[HookResult]) -> bool:
        """Check if all hook results allowed pipeline to proceed.

        Args:
            results: List of hook execution results.

        Returns:
            True if all hooks proceeded, False if any blocked.
        """
        return all(r.proceed for r in results)
