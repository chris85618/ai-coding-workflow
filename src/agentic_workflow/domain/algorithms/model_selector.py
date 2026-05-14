"""ALG-008: ModelSelector — Strategy Pattern for LLM model routing.

Traceable to: FR-029, CLS-017, INV-022
Deterministic: maps task_type to model config via strategy table.
No LLM, no I/O. Pure lookup with fallback logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import icontract

from agentic_workflow.domain.models.enums import TaskType
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


@icontract.require(
    lambda config: len(config.enabled_providers) > 0,
    "At least one provider must be enabled",
)
@icontract.ensure(
    lambda result, config: result.provider in config.enabled_providers,
    "Selected provider must be in enabled set (INV-022)",
)
def select_model(task_type: TaskType, config: StrategyConfig) -> ModelConfig:
    """Select the appropriate LLM model for the given task type.

    Strategy mapping:
        CRITIQUE   -> reasoning_model  (Agent alpha)
        RESOLVE    -> editing_model    (Agent beta)
        COMPREHEND -> reasoning_model  (Phase 1)
        CHARTER    -> reasoning_model  (Phase 2)
        FORMAT     -> cheap_model      (Low cost)

    Falls back to fallback_model if primary provider is disabled.

    Args:
        task_type: The type of LLM task to perform.
        config: Strategy configuration with model assignments.

    Returns:
        ModelConfig for the selected model.
    """
    strategy_map: dict[TaskType, ModelConfig] = {
        TaskType.CRITIQUE: config.reasoning_model,
        TaskType.RESOLVE: config.editing_model,
        TaskType.COMPREHEND: config.reasoning_model,
        TaskType.CHARTER: config.reasoning_model,
        TaskType.FORMAT: config.cheap_model,
    }

    selected = strategy_map.get(task_type, config.default_model)

    # Graceful degradation: fall back if provider is disabled
    if selected.provider not in config.enabled_providers:
        selected = config.fallback_model

    # Final safety: if fallback is also disabled, use first enabled provider's default
    if selected.provider not in config.enabled_providers:
        # Should not happen if config is valid, but guard defensively
        selected = ModelConfig(
            provider=next(iter(config.enabled_providers)),
            model=config.fallback_model.model,
        )

    return selected
