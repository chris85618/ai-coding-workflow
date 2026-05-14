"""CLS-018: ModelConfig — Value Object for LLM model parameters.

Traceable to: CLS-017 (LLMStrategySelector creates this)
INV-022 ensures provider is within enabled set.

Used by Agent alpha (reasoning) and Agent beta (editing)
to configure which LLM provider+model to use per task type.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelConfig:
    """Immutable configuration for a single LLM model selection.

    Attributes:
        provider: LLM provider name (e.g., "openai", "anthropic").
        model: Model identifier (e.g., "gpt-4o", "claude-opus").
        temperature: Sampling temperature. 0.0 = deterministic.
        max_tokens: Maximum tokens for LLM response.
    """

    provider: str
    model: str
    temperature: float = 0.0
    max_tokens: int = 4096


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
