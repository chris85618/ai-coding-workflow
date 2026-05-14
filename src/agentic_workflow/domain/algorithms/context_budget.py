"""ALG-007: ContextBudgetAllocator — Token budget allocation.

Traceable to: FR-030, INV-021
Deterministic: priority-based token allocation across context sources.
No LLM, no I/O.

Priority order: task_context > current_files > repo_map
  - task_context gets up to 50% of total budget
  - current_files get up to 70% of remainder
  - repo_map gets the rest
"""

from __future__ import annotations

import icontract

from agentic_workflow.domain.models.model_config import ContextAllocation
from agentic_workflow.domain.models.repo_map import RepoMap

_CHARS_PER_TOKEN = 4  # Approximate: 1 token ≈ 4 characters


def _estimate_tokens(text: str) -> int:
    """Estimate token count from text length.

    Args:
        text: Input text string.

    Returns:
        Estimated token count.
    """
    return max(1, len(text) // _CHARS_PER_TOKEN)


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
    task_tokens = _estimate_tokens(task_context)
    task_budget = min(task_tokens, total_budget // 2)
    task_text = task_context[: task_budget * _CHARS_PER_TOKEN]

    remaining = total_budget - task_budget

    # Current files: up to 70% of remaining
    files_text = "\n".join(current_files)
    files_tokens = _estimate_tokens(files_text)
    files_budget = min(files_tokens, int(remaining * 0.7))
    files_text = files_text[: files_budget * _CHARS_PER_TOKEN]

    remaining -= files_budget

    # Repo map: gets whatever is left
    map_budget = remaining
    pruned_map = repo_map.prune_to_budget(map_budget) if map_budget > 0 else repo_map
    map_text = pruned_map.get_context_string() if map_budget > 0 else ""

    total = task_budget + files_budget + (
        _estimate_tokens(map_text) if map_text else 0
    )

    return ContextAllocation(
        task=task_text,
        files=current_files,
        repo_map_text=map_text,
        total_tokens=min(total, total_budget),
    )
