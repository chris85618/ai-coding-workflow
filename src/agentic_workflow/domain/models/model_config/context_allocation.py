"""ContextAllocation — Token budget allocation across context sources."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ContextAllocation:
    """Token budget allocation across context sources.

    Attributes:
        task: Task context string.
        files: List of current file paths.
        repo_map_text: Pruned repo map as string.
        total_tokens: Sum of all allocated tokens.
    """

    task: str
    files: list[str]
    repo_map_text: str
    total_tokens: int
