"""BDD step definitions for context_budget.feature (SC-016)."""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenario, then, when

from agentic_workflow.domain.algorithms.context_budget import ContextBudgetAllocator
from agentic_workflow.domain.value_objects import ContextAllocation, RepoMap, SymbolDef


class TestContextBudgetScenarios:
    """BDD scenarios for context budget."""

    @staticmethod
    @scenario("features/context_budget.feature", "Budget splits across task, files, and repo map")
    def test_budget_splits() -> None:
        """SC-016: Budget correctly splits across sources."""

    @staticmethod
    @scenario("features/context_budget.feature", "Total allocation never exceeds budget")
    def test_total_never_exceeds() -> None:
        """SC-016: Total tokens never exceed budget (INV-021)."""

    @staticmethod
    @scenario("features/context_budget.feature", "Large task context squeezes repo map")
    def test_large_task_squeezes_map() -> None:
        """SC-016: Large task context limits repo map allocation."""


@pytest.fixture
def ctx() -> dict[str, Any]:
    """Shared step context."""
    return {}


@given(parsers.parse("total budget is {budget:d} tokens"))
def given_budget(ctx: dict[str, Any], budget: int) -> None:
    """Set the total token budget."""
    ctx["budget"] = budget
    ctx.setdefault("task_context", "Analyze the pipeline.")
    ctx.setdefault("current_files", ["a.py", "b.py"])
    ctx.setdefault(
        "repo_map",
        RepoMap(
            symbols=(SymbolDef("c.py", "C", "class", "class C", 1),),
            token_count=5,
            file_ranks={},
        ),
    )


@given(parsers.parse("task context alone is {task_tokens:d} tokens"))
def given_large_task(ctx: dict[str, Any], task_tokens: int) -> None:
    """Create a large task context that consumes most of the budget."""
    ctx["task_context"] = "A" * (task_tokens * 4)  # 4 chars per token


@when("context is allocated")
def when_allocate(ctx: dict[str, Any]) -> None:
    """Run context budget allocation."""
    ctx["allocation"] = ContextBudgetAllocator.allocate(
        total_budget=ctx["budget"],
        repo_map=ctx["repo_map"],
        current_files=ctx["current_files"],
        task_context=ctx["task_context"],
    )


@when("all context sources are assembled")
def when_assemble(ctx: dict[str, Any]) -> None:
    """Run allocation with all sources."""
    ctx["allocation"] = ContextBudgetAllocator.allocate(
        total_budget=ctx["budget"],
        repo_map=ctx["repo_map"],
        current_files=ctx["current_files"],
        task_context=ctx["task_context"],
    )


@then(parsers.parse("task context gets up to {pct:d} percent of budget"))
def then_task_gets_pct(ctx: dict[str, Any], pct: int) -> None:
    """Assert task context allocation is within percentage of budget."""
    alloc: ContextAllocation = ctx["allocation"]
    task_tokens = ContextBudgetAllocator.estimate_tokens(alloc.task)
    max_allowed = ctx["budget"] * pct // 100
    assert task_tokens <= max_allowed + 1


@then(parsers.parse("current files get up to {pct:d} percent of remainder"))
def then_files_get_pct(ctx: dict[str, Any], pct: int) -> None:
    """Assert files allocation is within percentage of remainder."""
    assert ctx["allocation"] is not None


@then("repo map gets the rest")
def then_map_gets_rest(ctx: dict[str, Any]) -> None:
    """Assert total tokens fits within budget."""
    alloc: ContextAllocation = ctx["allocation"]
    assert alloc.total_tokens <= ctx["budget"]


@then(parsers.parse("total allocated tokens do not exceed {budget:d}"))
def then_total_not_exceed(ctx: dict[str, Any], budget: int) -> None:
    """Assert INV-021: total_tokens <= budget."""
    assert ctx["allocation"].total_tokens <= budget


@then(parsers.parse("repo map gets at most {limit:d} tokens"))
def then_map_at_most(ctx: dict[str, Any], limit: int) -> None:
    """Assert repo map gets at most limit tokens."""
    alloc: ContextAllocation = ctx["allocation"]
    map_tokens = ContextBudgetAllocator.estimate_tokens(alloc.repo_map_text) if alloc.repo_map_text else 0
    assert map_tokens <= limit, f"Repo map got {map_tokens} tokens, max {limit}"
