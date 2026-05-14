"""CLS-017: LLMStrategySelector — Strategy Pattern for LLM selection.

Traceable to: FEA-011, UC-003, FR-029, INV-022, EVT-010
INV-022: select() always returns a provider in enabled_providers.

This is the domain service that wraps ALG-008 ModelSelector.
"""

from __future__ import annotations

import icontract

from agentic_workflow.domain.algorithms.model_selector import (
    StrategyConfig,
    select_model,
)
from agentic_workflow.domain.models.enums import TaskType
from agentic_workflow.domain.models.model_config import ModelConfig


class LLMStrategySelector:
    """Strategy Pattern selector for LLM model configuration.

    Wraps the deterministic ALG-008 ModelSelector algorithm
    with domain service semantics.

    Usage:
        selector = LLMStrategySelector(config)
        model_cfg = selector.select(TaskType.CRITIQUE)
    """

    def __init__(self, config: StrategyConfig) -> None:
        """Initialize with strategy configuration.

        Args:
            config: Strategy configuration with model assignments.
        """
        self._config = config

    @icontract.ensure(
        lambda result, self: result.provider in self._config.enabled_providers,
        "Selected provider must be in enabled set (INV-022)",
    )
    def select(self, task_type: TaskType) -> ModelConfig:
        """Select the appropriate model for the given task type.

        Args:
            task_type: The type of LLM task to perform.

        Returns:
            ModelConfig for the selected model.
        """
        return select_model(task_type, self._config)

    def list_providers(self) -> list[str]:
        """Return all currently enabled provider names.

        Returns:
            Sorted list of enabled provider names.
        """
        return sorted(self._config.enabled_providers)

    @property
    def enabled_provider_count(self) -> int:
        """Return count of enabled providers."""
        return len(self._config.enabled_providers)
