"""ALG-007: ContextBudgetAllocator — Token budget allocation.

Traceable to: FR-030, INV-021
Deterministic: priority-based token allocation across context sources.
No LLM, no I/O.
OO Design: ContextBudgetAllocator class encapsulates all logic (ALG-010 OO mandate).
Module-level functions retained as backward-compat facades.

Priority order: task_context > current_files > repo_map
  - task_context gets up to 50% of total budget
  - current_files get up to 70% of remainder
  - repo_map gets the rest
"""

from __future__ import annotations

import icontract

from agentic_workflow.domain.models.model_config import ContextAllocation
from agentic_workflow.domain.models.repo_map import RepoMap


class ContextBudgetAllocator:
    """ALG-007: Allocates token budget across context sources by priority.

    INV-021: total allocated tokens must not exceed the budget.

    Allocation priority (highest to lowest):
        1. task_context  — up to 50% of total budget
        2. current_files — up to 70% of remaining budget
        3. repo_map      — receives the rest
    """

    CHARS_PER_TOKEN: int = 4  # Approximate: 1 token ≈ 4 characters
    TASK_BUDGET_FRACTION: float = 0.5
    FILES_BUDGET_FRACTION: float = 0.7

    @classmethod
    def estimate_tokens(cls, text: str) -> int:
        """Estimate token count from text length.

        Args:
            text: Input text string.

        Returns:
            Estimated token count (minimum 1).
        """
        return max(1, len(text) // cls.CHARS_PER_TOKEN)

    @classmethod
    @icontract.require(
        lambda total_budget: total_budget > 0,
        "Total budget must be positive",
    )
    @icontract.ensure(
        lambda result, total_budget: result.total_tokens <= total_budget,
        "Total allocated tokens must not exceed budget (INV-021)",
    )
    def allocate(
        cls,
        total_budget: int,
        repo_map: RepoMap,
        current_files: list[str],
        task_context: str,
    ) -> ContextAllocation:
        """Allocate token budget across context sources by priority.

        Args:
            total_budget: Maximum total token count allowed.
            repo_map: The current repository map.
            current_files: List of file paths currently in context.
            task_context: The current task description string.

        Returns:
            ContextAllocation with tokens distributed across sources.
        """
        # Task context: up to 50% of total budget
        task_tokens = cls.estimate_tokens(task_context)
        task_budget = min(task_tokens, int(total_budget * cls.TASK_BUDGET_FRACTION))
        task_text = task_context[: task_budget * cls.CHARS_PER_TOKEN]

        remaining = total_budget - task_budget

        # Current files: up to 70% of remaining
        files_text = "\n".join(current_files)
        files_tokens = cls.estimate_tokens(files_text)
        files_budget = min(files_tokens, int(remaining * cls.FILES_BUDGET_FRACTION))
        files_text = files_text[: files_budget * cls.CHARS_PER_TOKEN]

        remaining -= files_budget

        # Repo map: gets whatever is left
        map_budget = remaining
        pruned_map = repo_map.prune_to_budget(map_budget) if map_budget > 0 else repo_map
        map_text = pruned_map.get_context_string() if map_budget > 0 else ""

        total = task_budget + files_budget + (
            cls.estimate_tokens(map_text) if map_text else 0
        )

        return ContextAllocation(
            task=task_text,
            files=current_files,
            repo_map_text=map_text,
            total_tokens=min(total, total_budget),
        )


# ── Module-level facades (backward compatibility) ──────────────────────────────

_CHARS_PER_TOKEN = ContextBudgetAllocator.CHARS_PER_TOKEN


def _estimate_tokens(text: str) -> int:
    """Backward-compat facade — delegates to ContextBudgetAllocator."""
    return ContextBudgetAllocator.estimate_tokens(text)


@icontract.require(
    lambda total_budget: total_budget > 0,
    "Total budget must be positive",
)
@icontract.ensure(
    lambda result, total_budget: result.total_tokens <= total_budget,
    "Total allocated tokens must not exceed budget (INV-021)",
)
def allocate_budget(
    total_budget: int,
    repo_map: RepoMap,
    current_files: list[str],
    task_context: str,
) -> ContextAllocation:
    """Backward-compat facade — delegates to ContextBudgetAllocator."""
    return ContextBudgetAllocator.allocate(
        total_budget, repo_map, current_files, task_context
    )
