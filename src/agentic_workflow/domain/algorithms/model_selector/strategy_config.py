"""ALG-008: StrategyConfig — Configuration for model strategy selection.

Traceable to: FR-029, CLS-017, INV-022
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agentic_workflow.domain.models.model_config import ModelConfig


@dataclass
class StrategyConfig:
    """Configuration for model strategy selection.

    Attributes:
        reasoning_model: Model for high-reasoning tasks (Agent alpha).
        editing_model: Model for fast-editing tasks (Agent beta).
        cheap_model: Model for simple formatting tasks.
        default_model: Fallback when no strategy matches.
        fallback_model: Used when primary provider is disabled.
        enabled_providers: Set of provider names that are active.
    """

    reasoning_model: ModelConfig
    editing_model: ModelConfig
    cheap_model: ModelConfig
    default_model: ModelConfig
    fallback_model: ModelConfig
    enabled_providers: frozenset[str] = field(default_factory=frozenset)
