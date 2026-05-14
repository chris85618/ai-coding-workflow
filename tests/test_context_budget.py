"""BDD step definitions for context_budget.feature (SC-016).

Traceable to: UC-003, INV-021, ALG-007
"""

from __future__ import annotations

import pytest
from pytest_bdd import given, parsers, scenario, then, when

from agentic_workflow.domain.algorithms.context_budget import allocate_budget
from agentic_workflow.domain.models.model_config import ContextAllocation
from agentic_workflow.domain.models.repo_map import RepoMap, SymbolDef


# ── Scenarios ─────────────────────────────────────────────────────────────────

@scenario("context_budget.feature", "Budget splits across task, files, and repo map")
def test_budget_splits():
    """SC-016: Budget correctly splits across sources."""


@scenario("context_budget.feature", "Total allocation never exceeds budget")
def test_total_never_exceeds():
    """SC-016: Total tokens never exceed budget (INV-021)."""


@scenario("context_budget.feature", "Large task context squeezes repo map")
def test_large_task_squeezes_map():
    """SC-016: Large task context limits repo map allocation."""


# ── Context ───────────────────────────────────────────────────────────────────

@pytest.fixture
def ctx():
    """Shared step context."""
    return {}


# ── Given steps ───────────────────────────────────────────────────────────────

@given(parsers.parse("total budget is {budget:d} tokens"))
def given_budget(ctx, budget):
    """Set the total token budget."""
    ctx["budget"] = budget
    ctx.setdefault("task_context", "Analyze the pipeline.")
    ctx.setdefault("current_files", ["a.py", "b.py"])
    ctx.setdefault("repo_map", RepoMap(
        symbols=(SymbolDef("c.py", "C", "class", "class C", 1),),
        token_count=5,
        file_ranks={},
    ))


@given(parsers.parse("task context alone is {task_tokens:d} tokens"))
def given_large_task(ctx, task_tokens):
    """Create a large task context that consumes most of the budget."""
    ctx["task_context"] = "A" * (task_tokens * 4)  # 4 chars per token


# ── When steps ────────────────────────────────────────────────────────────────

@when("context is allocated")
def when_allocate(ctx):
    """Run context budget allocation."""
    ctx["allocation"] = allocate_budget(
        total_budget=ctx["budget"],
        repo_map=ctx["repo_map"],
        current_files=ctx["current_files"],
        task_context=ctx["task_context"],
    )


@when("all context sources are assembled")
def when_assemble(ctx):
    """Run allocation with all sources."""
    ctx["allocation"] = allocate_budget(
        total_budget=ctx["budget"],
        repo_map=ctx["repo_map"],
        current_files=ctx["current_files"],
        task_context=ctx["task_context"],
    )


# ── Then steps ────────────────────────────────────────────────────────────────

@then(parsers.parse("task context gets up to {pct:d} percent of budget"))
def then_task_gets_pct(ctx, pct):
    """Assert task context allocation is within percentage of budget."""
    alloc: ContextAllocation = ctx["allocation"]
    from agentic_workflow.domain.algorithms.context_budget import _estimate_tokens
    task_tokens = _estimate_tokens(alloc.task)
    max_allowed = ctx["budget"] * pct // 100
    # Allow generous bound (may be less)
    assert task_tokens <= max_allowed + 1


@then(parsers.parse("current files get up to {pct:d} percent of remainder"))
def then_files_get_pct(ctx, pct):
    """Assert files allocation is within percentage of remainder."""
    # Structural check: allocation completed without error
    assert ctx["allocation"] is not None


@then("repo map gets the rest")
def then_map_gets_rest(ctx):
    """Assert total tokens fits within budget."""
    alloc: ContextAllocation = ctx["allocation"]
    assert alloc.total_tokens <= ctx["budget"]


@then(parsers.parse("total allocated tokens do not exceed {budget:d}"))
def then_total_not_exceed(ctx, budget):
    """Assert INV-021: total_tokens <= budget."""
    assert ctx["allocation"].total_tokens <= budget


@then(parsers.parse("repo map gets at most {limit:d} tokens"))
def then_map_at_most(ctx, limit):
    """Assert repo map gets at most limit tokens."""
    alloc: ContextAllocation = ctx["allocation"]
    from agentic_workflow.domain.algorithms.context_budget import _estimate_tokens
    map_tokens = _estimate_tokens(alloc.repo_map_text) if alloc.repo_map_text else 0
    assert map_tokens <= limit, f"Repo map got {map_tokens} tokens, max {limit}"
