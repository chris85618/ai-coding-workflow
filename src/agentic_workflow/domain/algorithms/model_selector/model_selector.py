"""ALG-008: ModelSelector — Strategy Pattern for LLM model routing.

Traceable to: FR-029, CLS-017, INV-022
Deterministic: maps task_type to model config via strategy table.
No LLM, no I/O. Pure lookup with fallback logic.
OO Design: ModelSelector class encapsulates all logic (ALG-010 OO mandate).
Module-level function retained as backward-compat facade.
"""

from __future__ import annotations

import deal

from agentic_workflow.domain.algorithms.model_selector.strategy_config import (
    StrategyConfig,
)
from agentic_workflow.domain.enums import TaskType
from agentic_workflow.domain.value_objects import ModelConfig


class ModelSelector:
    """ALG-008: Selects the appropriate LLM model for a given task type.

    Strategy mapping (CLS-017):
        CRITIQUE   -> reasoning_model  (Agent alpha)
        RESOLVE    -> editing_model    (Agent beta)
        COMPREHEND -> reasoning_model  (Phase 1)
        CHARTER    -> reasoning_model  (Phase 2)
        FORMAT     -> cheap_model      (Low cost)

    INV-022: selected provider must be in enabled_providers set.
    Graceful degradation: falls back to fallback_model if primary is disabled.
    """

    _STRATEGY_MAP_KEYS: frozenset[TaskType] = frozenset(
        [
            TaskType.CRITIQUE,
            TaskType.RESOLVE,
            TaskType.COMPREHEND,
            TaskType.CHARTER,
            TaskType.FORMAT,
        ],
    )

    @classmethod
    @deal.pre(
        lambda _: len(_.config.enabled_providers) > 0,
        message="At least one provider must be enabled",
    )
    @deal.ensure(
        lambda _: _.result.provider in _.config.enabled_providers,
        message="Selected provider must be in enabled set (INV-022)",
    )
    def select(cls, task_type: TaskType, config: StrategyConfig) -> ModelConfig:
        """Select the appropriate LLM model for the given task type.

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

        # Final safety: if fallback is disabled, use first enabled provider's default
        if selected.provider not in config.enabled_providers:
            # Should not happen if config is valid, but guard defensively
            selected = ModelConfig(
                provider=next(iter(config.enabled_providers)),
                model=config.fallback_model.model,
            )

        return selected


# ── Module-level facade (backward compatibility) ───────────────────────────────


@deal.pre(
    lambda _: len(_.config.enabled_providers) > 0,
    message="At least one provider must be enabled",
)
@deal.ensure(
    lambda _: _.result.provider in _.config.enabled_providers,
    message="Selected provider must be in enabled set (INV-022)",
)
def select_model(task_type: TaskType, config: StrategyConfig) -> ModelConfig:
    """Backward-compat facade — delegates to ModelSelector."""
    return ModelSelector.select(task_type, config)
