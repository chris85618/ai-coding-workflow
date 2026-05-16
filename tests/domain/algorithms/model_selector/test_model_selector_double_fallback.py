"""Cover the emergency fallback branch (L83) in ALG-008."""

from agentic_workflow.domain.algorithms.model_selector import select_model
from agentic_workflow.domain.algorithms.model_selector.strategy_config import StrategyConfig
from agentic_workflow.domain.enums import TaskType
from agentic_workflow.domain.value_objects import ModelConfig


class TestModelSelectorDoubleFallback:
    """Cover the emergency fallback branch (L83) in ALG-008."""

    def test_double_fallback_constructs_config(self) -> None:
        """When fallback is disabled, creates ModelConfig from enabled set."""
        disabled_primary = ModelConfig(provider="anthropic", model="claude-opus-4")
        disabled_fallback = ModelConfig(provider="google", model="gemini-ultra")
        cfg = StrategyConfig(
            reasoning_model=disabled_primary,
            editing_model=disabled_primary,
            cheap_model=disabled_primary,
            default_model=disabled_primary,
            fallback_model=disabled_fallback,
            enabled_providers=frozenset({"openai"}),
        )
        result = select_model(TaskType.CRITIQUE, cfg)
        assert result.provider == "openai"
